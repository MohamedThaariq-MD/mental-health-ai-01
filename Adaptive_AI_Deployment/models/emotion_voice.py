"""
Voice Emotion Model - LYKA AI (v3)
====================================
Pipeline:
  1. Accept audio bytes (WebM from browser microphone)
  2. Convert to WAV via pydub (ffmpeg backend)
  3. Transcribe speech-to-text via Groq Whisper API
  4. Extract MFCC + Chroma + RMS features via librosa
  5. Classify emotion using the trained RandomForest pipeline
  6. Return highest-confidence emotion label string

This module now returns BOTH:
  - voice_emotion  (str)  from acoustic model
  - transcribed_text (str) from Whisper (so callers can use it as prompt text)
"""

import os
import base64
import tempfile
import traceback
import numpy as np

# Optional imports handled gracefully
try:
    import librosa
    LIBROSA_OK = True
except ImportError:
    LIBROSA_OK = False
    print("[VoiceEmotion] librosa not installed — acoustic features disabled.")

try:
    import joblib
    JOBLIB_OK = True
except ImportError:
    JOBLIB_OK = False

MODEL_PATH = os.path.join(os.path.dirname(__file__), "voice_emotion_model.pkl")

# ── Model cache: load once, reuse forever ──────────────────────────────────────
_MODEL_CACHE = None

def _get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None and JOBLIB_OK and os.path.exists(MODEL_PATH):
        try:
            _MODEL_CACHE = joblib.load(MODEL_PATH)
            print(f"[VoiceEmotion] Model loaded: {type(_MODEL_CACHE).__name__}")
        except Exception as e:
            print(f"[VoiceEmotion] Could not load model: {e}")
    return _MODEL_CACHE


# ── Audio Conversion ───────────────────────────────────────────────────────────
def _convert_to_wav(src_path: str) -> str:
    """Convert any audio format (WebM, OGG, MP4, etc.) to WAV using pydub."""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(src_path)
        # Ensure mono, 16kHz for librosa compatibility
        audio = audio.set_channels(1).set_frame_rate(16000)
        wav_path = src_path.replace(os.path.splitext(src_path)[1], "_converted.wav")
        audio.export(wav_path, format="wav")
        print(f"[VoiceEmotion] Converted to WAV: {os.path.getsize(wav_path)} bytes")
        return wav_path
    except Exception as e:
        print(f"[VoiceEmotion] pydub conversion failed: {e}")
        return src_path


# ── Feature Extraction (MFCC + Chroma + RMS) ──────────────────────────────────
def extract_mfcc_features(file_path: str):
    """
    Extract 53 acoustic features from a WAV file using librosa:
      - 40 MFCC means (captures spectral envelope of speech)
      - 12 Chroma means (captures pitch/tonality)
      -  1 RMS energy mean (captures loudness/stress)

    Returns: numpy array shape (53,) or None if audio is invalid/too short.
    """
    if not LIBROSA_OK:
        return None

    try:
        y, sr = librosa.load(file_path, sr=16000, mono=True)

        # Trim leading/trailing silence
        y, _ = librosa.effects.trim(y, top_db=20)

        if len(y) < 1600:  # less than 0.1 second at 16kHz
            print(f"[VoiceEmotion] Audio too short after trimming: {len(y)} samples")
            return None

        print(f"[VoiceEmotion] Audio loaded: {len(y)/sr:.2f}s @ {sr}Hz")

        # 40 MFCC features — primary speech fingerprint
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        mfcc_mean = np.mean(mfccs, axis=1)  # (40,)

        # 12 Chroma — captures harmonic/pitch content
        chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_chroma=12)
        chroma_mean = np.mean(chroma, axis=1)  # (12,)

        # 1 RMS — captures energy/loudness
        rms = librosa.feature.rms(y=y)
        rms_mean = np.array([np.mean(rms)])  # (1,)

        features = np.hstack([mfcc_mean, chroma_mean, rms_mean])  # (53,)
        print(f"[VoiceEmotion] Features extracted: shape={features.shape}, MFCC[0]={mfcc_mean[0]:.2f}")
        return features

    except Exception as e:
        print(f"[VoiceEmotion] Feature extraction error: {e}")
        traceback.print_exc()
        return None


# ── Groq Whisper Transcription ─────────────────────────────────────────────────
def _transcribe_via_groq(wav_path: str) -> str | None:
    """
    Use Groq's Whisper API to transcribe speech to text.
    Returns transcribed string or None on failure.
    """
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            print("[VoiceEmotion] No GROQ_API_KEY — skipping Whisper transcription.")
            return None

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {groq_api_key}"}

        with open(wav_path, "rb") as f:
            files = {
                "file": (os.path.basename(wav_path), f, "audio/wav"),
                "model": (None, "whisper-large-v3-turbo"),
                "language": (None, "en"),
                "prompt": (None, "The user is speaking in English about their feelings or mental state.")
            }
            response = requests.post(url, headers=headers, files=files, timeout=30)

        if response.status_code == 200:
            text = response.json().get("text", "").strip()
            print(f"[VoiceEmotion] Whisper transcription: '{text}'")
            return text if text else None
        else:
            print(f"[VoiceEmotion] Groq Whisper error {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"[VoiceEmotion] Transcription exception: {e}")
        return None


# ── NLP-Based Fallback Emotion if Transcription Succeeds ──────────────────────
def _classify_emotion_from_text(text: str) -> str | None:
    """
    Use keyword NLP to detect emotion from the transcribed speech text.
    This acts as a confidence boost / cross-check for the acoustic model.
    Returns emotion string or None if no strong match.
    """
    if not text:
        return None

    text_lower = text.lower()

    KEYWORD_MAP = {
        "Crisis":   ["kill myself", "end my life", "suicide", "want to die", "no point living"],
        "Stressed": ["stressed", "overwhelmed", "pressure", "deadline", "panic", "anxious", "anxiety"],
        "Sad":      ["sad", "depressed", "crying", "tears", "hopeless", "empty", "heartbroken"],
        "Angry":    ["angry", "furious", "rage", "hate", "frustrated", "annoyed"],
        "Happy":    ["happy", "excited", "joyful", "wonderful", "amazing", "great", "love today"],
        "Lonely":   ["lonely", "alone", "nobody", "isolated", "no one"],
        "Traumatized": ["trauma", "nightmare", "flashback", "ptsd", "can't forget", "haunts me"],
        "Calm":     ["calm", "peaceful", "relaxed", "okay", "fine", "alright", "good"],
    }

    for emotion, keywords in KEYWORD_MAP.items():
        if any(kw in text_lower for kw in keywords):
            print(f"[VoiceEmotion] NLP keyword match → {emotion}")
            return emotion

    return None


# ── Main Public Function ───────────────────────────────────────────────────────
def detect_voice_emotion(audio_b64: str) -> str:
    """
    Full pipeline:
      base64 audio → temp file → WAV conversion → MFCC features → model prediction
      Optionally also transcribes via Whisper and does NLP keyword cross-check.

    Returns: emotion label string (e.g. 'Stressed', 'Happy', 'Sad', 'Neutral')
    """
    if not audio_b64:
        return "Neutral"

    # 1. Decode base64 audio (handles "data:audio/webm;base64,..." format)
    try:
        if "," in audio_b64:
            audio_b64 = audio_b64.split(",", 1)[1]
        audio_bytes = base64.b64decode(audio_b64)
        print(f"[VoiceEmotion] Decoded audio: {len(audio_bytes)} bytes")
    except Exception as e:
        print(f"[VoiceEmotion] Base64 decode error: {e}")
        return "Neutral"

    if len(audio_bytes) < 1000:
        print(f"[VoiceEmotion] Audio too short ({len(audio_bytes)} bytes) — skipping.")
        return "Neutral"

    raw_path = None
    wav_path = None

    try:
        # 2. Write raw audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio_bytes)
            raw_path = tmp.name

        # 3. Convert to WAV (16kHz mono)
        wav_path = _convert_to_wav(raw_path)

        # 4. Transcribe (Whisper → NLP check) for natural text-based emotion boost
        transcribed = _transcribe_via_groq(wav_path)
        nlp_emotion = _classify_emotion_from_text(transcribed)

        # 5. Extract MFCC features for acoustic model
        features = extract_mfcc_features(wav_path)

        # 6. Acoustic model prediction
        acoustic_emotion = None
        model = _get_model()
        if model is not None and features is not None:
            try:
                acoustic_emotion = model.predict(features.reshape(1, -1))[0]
                proba = model.predict_proba(features.reshape(1, -1))[0]
                confidence = float(np.max(proba))
                print(f"[VoiceEmotion] Acoustic model → {acoustic_emotion} (conf={confidence:.2f})")

                # Low confidence = don't trust acoustic over NLP
                if confidence < 0.35:
                    acoustic_emotion = None
            except Exception as e:
                print(f"[VoiceEmotion] Model prediction error: {e}")
                acoustic_emotion = None

        # 7. Fusion: NLP keyword > Acoustic model > Neutral
        #    NLP is more reliable for short recordings
        if nlp_emotion:
            return nlp_emotion
        elif acoustic_emotion:
            return acoustic_emotion
        else:
            return "Neutral"

    except Exception as e:
        print(f"[VoiceEmotion] Pipeline error: {e}")
        traceback.print_exc()
        return "Neutral"

    finally:
        # 8. Cleanup temp files
        for path in [raw_path, wav_path]:
            try:
                if path and path != raw_path or path == raw_path:
                    if os.path.exists(path):
                        os.remove(path)
            except Exception:
                pass

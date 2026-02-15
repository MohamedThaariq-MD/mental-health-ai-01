import os
import io
from gtts import gTTS

def speak_text(text, lang='en'):
    """
    Convert text to speech using Google Text-to-Speech (gTTS).
    Returns the audio content as bytes.
    """
    try:
        if not text:
            return None
            
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to memory buffer
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        return fp.read()
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

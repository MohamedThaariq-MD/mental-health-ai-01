import sys
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Allow import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
from models.emotion_text import detect_text_emotion
from models.emotion_face import detect_face_emotion
from models.empathetic_responder import generate_empathetic_response
from models.conversation_context import get_session_memory
from rl_engine.therapy_rl import choose_therapy, update_recommendation_model
from backend.database import init_db, save_analysis, save_conversation_turn, get_conversation_history, get_previous_emotional_state, save_feedback
import uuid

app = Flask(__name__)

# Initialize database on startup
init_db()

# --- FEEDBACK ENDPOINT (RL) ---
@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Recieve user feedback (Thumbs Up/Down) for a specific recommendation.
    Update the RL model and save to history.
    """
    try:
        data = request.json
        session_id = data.get("session_id")
        emotion = data.get("emotion")
        action = data.get("action") 
        reward = data.get("reward") # +1 or -1
        
        if not all([session_id, emotion, action, reward is not None]):
             return jsonify({"error": "Missing data fields"}), 400

        # Update the RL Model
        updated_category = update_recommendation_model(emotion, action, reward)
        
        # Save to DB
        save_feedback(session_id, emotion, action, reward)
        
        return jsonify({
            "status": "success", 
            "message": f"RL Model updated for {updated_category}."
        })
        
    except Exception as e:
        print(f"Feedback Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "")
        use_camera = data.get("use_camera", False)
        session_id = data.get("session_id", str(uuid.uuid4()))  # Generate if not provided

        text_result = detect_text_emotion(text)
        text_emotion = text_result[0].get("label", "Neutral")
        emotion_intensity = text_result[0].get("intensity", "moderate")

        # Check if user wants facial analysis
        face_emotion = "Neutral"
        face_details = {}
        processed_frame = None
        face_features = {}
        feature_desc = ""
        
        if use_camera:
            try:
                face_emotion, face_details, processed_frame, face_features, feature_desc = detect_face_emotion()
            except Exception as e:
                print(f"Camera error: {e}")
                face_emotion = "Neutral"
                face_details = {}
                processed_frame = None
                face_features = {}
                feature_desc = "Camera error."

        final_emotion = face_emotion if face_emotion != "Neutral" else text_emotion
        
        # --- EMOTION REFINEMENT LOGIC ---
        # Refine Face Emotion Labels
        refined_face_emotion = face_emotion
        ear = face_features.get("ear", 0.5)
        
        if face_emotion == "Fear":
            refined_face_emotion = "Nervous"
        elif face_emotion == "Happy" and ear > 0.32:
             refined_face_emotion = "Enjoying"
        elif face_emotion == "Sad":
            # Check for high intensity or physical cues of crying (e.g., very low EAR or specific mesh patterns if we had them)
            # For now, use intensity or low EAR as a proxy for "shut town" sadness
            if ear < 0.22 or emotion_intensity == "high":
                refined_face_emotion = "Crying"
        
        # Refine Text Emotion Labels (Simple Mapping)
        refined_text_emotion = text_emotion
        if text_emotion == "Anxious":
            refined_text_emotion = "Nervous"
            
        # Construct Final Declaration
        if refined_face_emotion == "Neutral" and refined_text_emotion == "Neutral":
             final_declaration = "You seem calm and balanced today."
        elif refined_face_emotion != "Neutral":
            final_declaration = f"You seem {refined_text_emotion.lower()}, and your face shows signs of being {refined_face_emotion.lower()}."
        else:
             final_declaration = f"I sense you are feeling {refined_text_emotion.lower()}."

        # Use the feature description from the model if available, otherwise fallback
        face_feature_desc = feature_desc if feature_desc else "No specific physical cues detected."

        # Get enhanced recommendations
        recommendations = choose_therapy(final_emotion, face_features)
        
        # Get conversation context from session memory
        session_memory = get_session_memory(session_id)
        conversation_context = session_memory.get_context_for_response()
        
        # Get historical emotional state (long-term memory)
        historical_context = get_previous_emotional_state(session_id)
        
        # Get explicit conversation history (last 20 turns)
        recent_history = session_memory.get_recent_exchanges(20)

        # Generate empathetic conversational response with context
        empathetic_response = generate_empathetic_response(
            text_emotion=text_emotion,
            face_emotion=face_emotion,
            final_emotion=final_emotion,
            user_text=text,
            recommendations=recommendations,
            context=conversation_context,
            historical_context=historical_context,
            conversation_history=recent_history
        )
        
        ai_response = empathetic_response.get("conversational_response")
        
        # Save conversation turn to memory and database
        session_memory.add_exchange(
            user_text=text,
            ai_response=ai_response,
            emotion=final_emotion,
            emotion_intensity=emotion_intensity
        )
        
        save_conversation_turn(
            session_id=session_id,
            user_text=text,
            ai_response=ai_response,
            emotion=final_emotion,
            emotion_intensity=emotion_intensity
        )

        # Save to analysis history (existing functionality)
        save_analysis(
            text_input=text,
            text_emotion=text_emotion,
            face_emotion=face_emotion,
            final_emotion=final_emotion,
            recs=recommendations
        )

        return jsonify({
            "session_id": session_id,  # Return session ID for client to maintain
            "text_emotion": refined_text_emotion,
            "face_emotion": refined_face_emotion,
            "final_declaration": final_declaration,
            "face_details": face_details,
            "processed_frame": processed_frame,
            "face_feature_desc": face_feature_desc,
            "final_emotion": final_emotion,
            "emotion_intensity": emotion_intensity,
            "therapy": recommendations.get("therapy"),
            "meditation": recommendations.get("meditation"),
            "activity": recommendations.get("activity"),
            "music": recommendations.get("music"),
            "movie": recommendations.get("movie"),
            "game": recommendations.get("game"),
            # New conversational fields
            "conversational_response": ai_response,
            "follow_up_suggestions": empathetic_response.get("follow_up_suggestions", []),
            # Context information
            "conversation_context": {
                "relationship_stage": conversation_context.get("relationship_stage"),
                "emotion_trend": conversation_context.get("emotion_trend"),
                "total_turns": conversation_context.get("total_turns")
            }
        })

    except Exception as e:
        print("Error processing request:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500




from backend.llm_service import transcribe_audio
from backend.tts_service import speak_text
import tempfile
import io
from flask import send_file

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
            
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            file.save(temp.name)
            temp_path = temp.name
            
        # Transcribe
        text = transcribe_audio(temp_path)
        
        # Cleanup
        try:
            os.remove(temp_path)
        except:
            pass
        
        if text:
            return jsonify({"text": text})
        else:
            return jsonify({"error": "Transcription failed"}), 500
            
    except Exception as e:
        print(f"Transcription Endpoint Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/tts", methods=["POST"])
def tts_endpoint():
    try:
        data = request.json
        text = data.get("text")
        lang = data.get("lang", "en") # Default to english
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        audio_bytes = speak_text(text, lang)
        
        if audio_bytes:
            return send_file(
                io.BytesIO(audio_bytes),
                mimetype="audio/mpeg",
                as_attachment=False,
                download_name="output.mp3"
            )
        else:
            return jsonify({"error": "TTS failed"}), 500
            
    except Exception as e:
        print(f"TTS Endpoint Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # LOCAL RUN ONLY
    app.run(debug=True)

import sys
import os

# Allow import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
from models.emotion_text import detect_text_emotion
from models.emotion_face import detect_face_emotion
from rl_engine.therapy_rl import choose_therapy

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "")
        use_camera = data.get("use_camera", False)

        text_result = detect_text_emotion(text)
        text_emotion = text_result[0].get("label", "Neutral")

        # Check if user wants facial analysis
        face_emotion = "Neutral"
        if use_camera:
            try:
                face_emotion = detect_face_emotion()
            except Exception as e:
                print(f"Camera error: {e}")
                face_emotion = "Neutral"

        final_emotion = face_emotion if face_emotion != "Neutral" else text_emotion
        therapy = choose_therapy(final_emotion)

        return jsonify({
            "text_emotion": text_emotion,
            "face_emotion": face_emotion,
            "final_emotion": final_emotion,
            "therapy": therapy
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # LOCAL RUN ONLY
    app.run(debug=True)

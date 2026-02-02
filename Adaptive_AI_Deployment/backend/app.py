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

        text_result = detect_text_emotion(text)
        text_emotion = text_result[0].get("label", "Neutral")

        # LOCAL machine supports camera
        face_emotion = detect_face_emotion()

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

import cv2
from fer.fer import FER
import os

# Initialize the detector once outside the function for better performance
# mtcnn=True uses a more accurate but slower face detector
detector = FER(mtcnn=False) 

def detect_face_emotion():
    """
    Real-world face emotion detection using FER library.
    Returns the most dominant emotion or 'Neutral' if unavailable.
    """
    cam = None
    try:
        # Open camera (index 0 is usually the default)
        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            print("Warning: Camera could not be opened.")
            return "Neutral"

        # Capture a single frame
        ret, frame = cam.read()
        
        if not ret or frame is None:
            print("Warning: Failed to capture image from camera.")
            return "Neutral"

        # Detect emotions
        # result is a list of dictionaries with 'box' and 'emotions' keys
        results = detector.detect_emotions(frame)

        if not results:
            print("No face detected in the frame.")
            return "Neutral"

        # Get the first detected face's emotions
        emotions = results[0]["emotions"]
        
        # Find the emotion with the highest confidence score
        dominant_emotion = max(emotions, key=emotions.get)
        
        # Capitalize for UI consistency (e.g., 'happy' -> 'Happy')
        return dominant_emotion.capitalize()

    except Exception as e:
        print("Face emotion analysis error:", e)
        return "Neutral"
    
    finally:
        if cam is not None:
            cam.release()

if __name__ == "__main__":
    # Test script
    print("Testing Face Emotion Detection...")
    emotion = detect_face_emotion()
    print(f"Detected Emotion: {emotion}")

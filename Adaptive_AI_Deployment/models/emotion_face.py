import cv2
import mediapipe as mp
import base64
import numpy as np
import os
from fer.fer import FER

# Initialize the detector once outside the function for better performance
detector = FER(mtcnn=False) 

# Initialize MediaPipe Face Mesh if available
try:
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    HAS_MEDIAPIPE = True
except Exception as e:
    # Catches ImportError, AttributeError, RuntimeError (mediapipe protobuf parse failures), etc.
    print(f"MediaPipe not available, facial mesh disabled: {e}")
    HAS_MEDIAPIPE = False


def calculate_ear(landmarks, indices):
    """Calculates Eye Aspect Ratio (EAR) for a given eye."""
    # Vertical distances
    A = np.linalg.norm(np.array([landmarks[indices[1]].x, landmarks[indices[1]].y]) - 
                       np.array([landmarks[indices[5]].x, landmarks[indices[5]].y]))
    B = np.linalg.norm(np.array([landmarks[indices[2]].x, landmarks[indices[2]].y]) - 
                       np.array([landmarks[indices[4]].x, landmarks[indices[4]].y]))
    # Horizontal distance
    C = np.linalg.norm(np.array([landmarks[indices[0]].x, landmarks[indices[0]].y]) - 
                       np.array([landmarks[indices[3]].x, landmarks[indices[3]].y]))
    
    if C == 0:
        return 0
    return (A + B) / (2.0 * C)

def draw_golden_ratio_lines(image, landmarks):
    """Draws aesthetic golden ratio lines on the face."""
    h, w, c = image.shape
    
    # Key landmarks for Golden Ratio (approximate indices)
    # Nose tip: 1
    # Chin: 152
    # Left Eye Center: 468
    # Right Eye Center: 473
    # Forehead Center: 10
    
    points = {}
    for idx in [1, 152, 468, 473, 10, 234, 454]: # 234: Left cheek, 454: Right cheek
        lm = landmarks[idx]
        points[idx] = (int(lm.x * w), int(lm.y * h))

    # Color: Gold (BGR) -> (0, 215, 255) in BGR is Gold-ish
    gold_color = (0, 215, 255)
    thickness = 1
    
    # Vertical Center Line (Forehead -> Nose -> Chin)
    cv2.line(image, points[10], points[152], gold_color, thickness)
    
    # Horizontal Eye Line
    cv2.line(image, points[468], points[473], gold_color, thickness)
    
    # Face Width Line (Cheek to Cheek)
    cv2.line(image, points[234], points[454], gold_color, thickness)
    
    # Triangle: Left Eye -> Nose -> Right Eye
    cv2.line(image, points[468], points[1], gold_color, thickness)
    cv2.line(image, points[1], points[473], gold_color, thickness)
    
    # Connection: Nose to Chin
    # Already covered by center line, but let's add dots
    for idx in points:
        cv2.circle(image, points[idx], 3, (0, 255, 0), -1) # Green dots for key points

# Load the DL Landmark geometry classifier if it exists
import tensorflow as tf
from tensorflow.keras.models import load_model

LANDMARK_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'face_landmark_model.keras')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'face_landmark_encoder.pkl')
landmark_clf = None
landmark_encoder = None

if os.path.exists(LANDMARK_MODEL_PATH) and os.path.exists(ENCODER_PATH):
    import pickle
    try:
        landmark_clf = load_model(LANDMARK_MODEL_PATH)
        with open(ENCODER_PATH, 'rb') as f:
            landmark_encoder = pickle.load(f)
        print("DL Landmark Keras model and encoder loaded successfully.")
    except Exception as e:
        print(f"Error loading DL landmark classifier: {e}")

def detect_face_emotion():
    """
    Real-world face emotion detection using FER library with geometric refinement.
    Returns the dominant emotion and the processed frame (base64).
    """
    cam = None
    processed_frame_b64 = None
    
    try:
        # Open camera
        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            print("Warning: Camera could not be opened.")
            return "Neutral", {}, None, {}, "Camera not opened"

        # Capture a single frame
        ret, frame = cam.read()
        
        if not ret or frame is None:
            print("Warning: Failed to capture image from camera.")
            return "Neutral", {}, None, {}, "Frame capture failed"
            
        frame = cv2.flip(frame, 1)

        # 1. Detect Emotions first (FER - Visual base)
        results = detector.detect_emotions(frame)
        dominant_emotion = "Neutral"
        emotions_score = {}

        if results:
            emotions_score = results[0]["emotions"]
            dominant_emotion = max(emotions_score, key=emotions_score.get).capitalize()

        # 2. Process Face Mesh (MediaPipe) and Landmark Model (Geometric refinement)
        face_features = {}
        feature_desc_parts = []
        
        if HAS_MEDIAPIPE:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results_mesh = face_mesh.process(rgb_image)

            if results_mesh.multi_face_landmarks:
                for face_landmarks in results_mesh.multi_face_landmarks:
                    landmarks = face_landmarks.landmark
                    
                    # Style settings
                    connection_spec = mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=1, circle_radius=1)
                    landmark_spec = mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=1, circle_radius=1)

                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=landmark_spec,
                        connection_drawing_spec=connection_spec
                    )
                    
                    draw_golden_ratio_lines(frame, landmarks)
                    
                    # Calculate Geometric Features
                    left_ear = calculate_ear(landmarks, [33, 160, 158, 133, 153, 144])
                    right_ear = calculate_ear(landmarks, [362, 385, 387, 263, 373, 380])
                    avg_ear = (left_ear + right_ear) / 2.0
                    
                    top_lip, bottom_lip, left_corner, right_corner = landmarks[13], landmarks[14], landmarks[61], landmarks[291]
                    mar_v = np.linalg.norm(np.array([top_lip.x, top_lip.y]) - np.array([bottom_lip.x, bottom_lip.y]))
                    mar_h = np.linalg.norm(np.array([left_corner.x, left_corner.y]) - np.array([right_corner.x, right_corner.y]))
                    mar = mar_v / mar_h if mar_h > 0 else 0
                    
                    brow_inner_L, brow_inner_R, eye_inner_L, eye_inner_R = landmarks[107], landmarks[336], landmarks[133], landmarks[362]
                    brow_d = np.linalg.norm(np.array([brow_inner_L.x, brow_inner_L.y]) - np.array([brow_inner_R.x, brow_inner_R.y]))
                    eye_d = np.linalg.norm(np.array([eye_inner_L.x, eye_inner_L.y]) - np.array([eye_inner_R.x, eye_inner_R.y]))
                    brow_ratio = brow_d / eye_d if eye_d > 0 else 0
                    
                    face_features = {'ear': avg_ear, 'mar': mar, 'brow_ratio': brow_ratio}
                    
                    # --- REFINEMENT VIA DEEP LEARNING ---
                    if landmark_clf and landmark_encoder:
                        features = np.array([[avg_ear, mar, brow_ratio]])
                        try:
                            probs = landmark_clf.predict(features, verbose=0)[0]
                            max_idx = np.argmax(probs)
                            geometric_emotion = landmark_encoder.inverse_transform([max_idx])[0]
                            # If geometric model detects high stress, override
                            if geometric_emotion in ["Stressed", "Angry", "Fear"] and dominant_emotion == "Neutral":
                                dominant_emotion = geometric_emotion
                            elif geometric_emotion == "Surprise" and avg_ear > 0.38:
                                dominant_emotion = "Surprise"
                        except Exception as e:
                            print(f"Error running inference on DL Landmark model: {e}")
                    
                    # Descriptions
                    if avg_ear < 0.2: feature_desc_parts.append("Eyes appear tired.")
                    if mar > 0.5: feature_desc_parts.append("Mouth open.")
                    if brow_ratio < 0.6: feature_desc_parts.append("Brows furrowed.")
        else:
            feature_desc_parts.append("Facial mesh disabled.")

        # 3. Encode Frame
        _, buffer = cv2.imencode('.jpg', frame)
        processed_frame_b64 = base64.b64encode(buffer).decode('utf-8')
        feature_desc = " ".join(feature_desc_parts) if feature_desc_parts else f"Dominant: {dominant_emotion}."

        return dominant_emotion, emotions_score, processed_frame_b64, face_features, feature_desc

    except Exception as e:
        print("Face emotion analysis error:", e)
        return "Neutral", {}, None, {}, "Error in analysis."
    
    finally:
        if cam is not None:
            cam.release()

def detect_face_emotion_from_b64(frame_b64: str):
    """
    Detect face emotion from a base64-encoded JPEG frame (from browser webcam).
    Runs the same FER + MediaPipe pipeline as detect_face_emotion()
    but without needing cv2.VideoCapture — works in cloud environments.
    """
    try:
        import base64
        # Decode base64 frame to numpy array
        img_bytes = base64.b64decode(frame_b64)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if frame is None:
            return "Neutral", {}, None, {}, "Could not decode browser frame."
        
        # Flip horizontally (mirror correction like VideoCapture)
        frame = cv2.flip(frame, 1)
        
        # 1. FER emotion detection
        results = detector.detect_emotions(frame)
        dominant_emotion = "Neutral"
        emotions_score = {}
        if results:
            emotions_score = results[0]["emotions"]
            dominant_emotion = max(emotions_score, key=emotions_score.get).capitalize()
        
        # 2. MediaPipe Face Mesh
        face_features = {}
        feature_desc_parts = []
        
        if HAS_MEDIAPIPE:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results_mesh = face_mesh.process(rgb_image)
            
            if results_mesh.multi_face_landmarks:
                for face_landmarks in results_mesh.multi_face_landmarks:
                    landmarks = face_landmarks.landmark
                    
                    connection_spec = mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=1, circle_radius=1)
                    landmark_spec  = mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=1, circle_radius=1)
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=landmark_spec,
                        connection_drawing_spec=connection_spec
                    )
                    draw_golden_ratio_lines(frame, landmarks)
                    
                    left_ear  = calculate_ear(landmarks, [33,  160, 158, 133, 153, 144])
                    right_ear = calculate_ear(landmarks, [362, 385, 387, 263, 373, 380])
                    avg_ear   = (left_ear + right_ear) / 2.0
                    
                    top_lip, bottom_lip = landmarks[13], landmarks[14]
                    left_corner, right_corner = landmarks[61], landmarks[291]
                    mar_v = np.linalg.norm(np.array([top_lip.x, top_lip.y]) - np.array([bottom_lip.x, bottom_lip.y]))
                    mar_h = np.linalg.norm(np.array([left_corner.x, left_corner.y]) - np.array([right_corner.x, right_corner.y]))
                    mar = mar_v / mar_h if mar_h > 0 else 0
                    
                    brow_inner_L = landmarks[107]; brow_inner_R = landmarks[336]
                    eye_inner_L  = landmarks[133]; eye_inner_R  = landmarks[362]
                    brow_d = np.linalg.norm(np.array([brow_inner_L.x, brow_inner_L.y]) - np.array([brow_inner_R.x, brow_inner_R.y]))
                    eye_d  = np.linalg.norm(np.array([eye_inner_L.x,  eye_inner_L.y])  - np.array([eye_inner_R.x,  eye_inner_R.y]))
                    brow_ratio = brow_d / eye_d if eye_d > 0 else 0
                    
                    face_features = {'ear': avg_ear, 'mar': mar, 'brow_ratio': brow_ratio}
                    
                    if landmark_clf:
                        geometric_emotion = landmark_clf.predict([[avg_ear, mar, brow_ratio]])[0]
                        if geometric_emotion in ["Stressed", "Angry", "Fear"] and dominant_emotion == "Neutral":
                            dominant_emotion = geometric_emotion
                        elif geometric_emotion == "Surprise" and avg_ear > 0.38:
                            dominant_emotion = "Surprise"
                    
                    if avg_ear   < 0.2: feature_desc_parts.append("Eyes appear tired.")
                    if mar       > 0.5: feature_desc_parts.append("Mouth open.")
                    if brow_ratio< 0.6: feature_desc_parts.append("Brows furrowed.")
        
        # 3. Encode annotated frame
        _, buffer = cv2.imencode('.jpg', frame)
        processed_frame_b64 = base64.b64encode(buffer).decode('utf-8')
        feature_desc = " ".join(feature_desc_parts) if feature_desc_parts else f"Dominant: {dominant_emotion}."
        
        return dominant_emotion, emotions_score, processed_frame_b64, face_features, feature_desc
    
    except Exception as e:
        print(f"detect_face_emotion_from_b64 error: {e}")
        return "Neutral", {}, None, {}, "Error processing browser frame."


if __name__ == "__main__":
    # Test script
    print("Testing Face Emotion Detection...")
    emotion = detect_face_emotion()
    print(f"Detected Emotion: {emotion}")

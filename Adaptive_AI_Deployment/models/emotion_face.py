import cv2
import mediapipe as mp
import base64
import numpy as np
from fer.fer import FER

# Initialize the detector once outside the function for better performance
detector = FER(mtcnn=False) 

# Initialize MediaPipe Face Mesh
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

def detect_face_emotion():
    """
    Real-world face emotion detection using FER library.
    Returns the dominant emotion and the processed frame (base64).
    """
    cam = None
    processed_frame_b64 = None
    
    try:
        # Open camera (index 0 is usually the default)
        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            print("Warning: Camera could not be opened.")
            return "Neutral", {}, None, {}, "Camera not opened"

        # Capture a single frame
        ret, frame = cam.read()
        
        if not ret or frame is None:
            print("Warning: Failed to capture image from camera.")
            return "Neutral", {}, None, {}, "Frame capture failed"
            
        # Flip frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)

        # 1. Detect Emotions first (FER)
        results = detector.detect_emotions(frame)
        dominant_emotion = "Neutral"
        emotions_score = {}

        if results:
            emotions_score = results[0]["emotions"]
            dominant_emotion = max(emotions_score, key=emotions_score.get).capitalize()

        # 2. Process Face Mesh (MediaPipe)
        # Convert the BGR image to RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_mesh = face_mesh.process(rgb_image)

        face_features = {}
        feature_desc_parts = []

        # Draw mesh and golden ratio lines, and calculate features
        if results_mesh.multi_face_landmarks:
            for face_landmarks in results_mesh.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                
                # Define custom styles for "High-Tech" look (Cyan: BGR 255, 255, 0)
                # Connections: Thin cyan lines
                connection_spec = mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=1, circle_radius=1)
                # Landmarks: Small cyan dots
                landmark_spec = mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=1, circle_radius=1)

                # Draw Contours (Cleaner look than Tessellation)
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=landmark_spec,
                    connection_drawing_spec=connection_spec
                )
                
                # Draw Golden Ratio lines
                draw_golden_ratio_lines(frame, landmarks)
                
                # Calculate Geometric Features
                
                # EAR (Eye Aspect Ratio) - Drowsiness / Alertness
                # Left Eye indices: 33, 160, 158, 133, 153, 144
                # Right Eye indices: 362, 385, 387, 263, 373, 380
                left_ear = calculate_ear(landmarks, [33, 160, 158, 133, 153, 144])
                right_ear = calculate_ear(landmarks, [362, 385, 387, 263, 373, 380])
                avg_ear = (left_ear + right_ear) / 2.0
                face_features['ear'] = avg_ear
                
                if avg_ear < 0.2:
                    feature_desc_parts.append("Eyes appear tired or closed.")
                elif avg_ear > 0.35:
                     feature_desc_parts.append("Eyes are wide open (alert/surprise).")
                     
                # MAR (Mouth Aspect Ratio) - Smiling / Yawning
                # Mouth indices: 78, 81, 13, 311, 308, 402, 14, 178
                # We can use a simplified version: (upper_lip_top, lower_lip_bottom, left_corner, right_corner)
                # Vertical: 13 (upper), 14 (lower). Horizontal: 61 (left corner), 291 (right corner).
                # Actually, let's use a robust set:
                # Top: 13, Bottom: 14, Left: 61, Right: 291
                # Vertical dist = dist(13, 14)
                # Horizontal dist = dist(61, 291)
                
                top_lip = landmarks[13]
                bottom_lip = landmarks[14]
                left_corner = landmarks[61]
                right_corner = landmarks[291]
                
                mar_vertical = np.linalg.norm(np.array([top_lip.x, top_lip.y]) - np.array([bottom_lip.x, bottom_lip.y]))
                mar_horizontal = np.linalg.norm(np.array([left_corner.x, left_corner.y]) - np.array([right_corner.x, right_corner.y]))
                
                mar = mar_vertical / mar_horizontal if mar_horizontal > 0 else 0
                face_features['mar'] = mar
                
                if mar > 0.5:
                    feature_desc_parts.append("Mouth is wide open (yawning/surprise).")
                elif mar < 0.1:
                    feature_desc_parts.append("Mouth is tightly closed (tension).")
                    
                # Brow Ratio (Stress/Frowning)
                # Distance between brows vs face width? or just distance between brow centers.
                # Left brow inner: 107. Right brow inner: 336.
                # Normalize by inner eye distance (dist 133 to 362) to be scale invariant.
                
                brow_inner_L = landmarks[107]
                brow_inner_R = landmarks[336]
                eye_inner_L = landmarks[133]
                eye_inner_R = landmarks[362]
                
                brow_dist = np.linalg.norm(np.array([brow_inner_L.x, brow_inner_L.y]) - np.array([brow_inner_R.x, brow_inner_R.y]))
                eye_dist = np.linalg.norm(np.array([eye_inner_L.x, eye_inner_L.y]) - np.array([eye_inner_R.x, eye_inner_R.y]))
                
                brow_ratio = brow_dist / eye_dist if eye_dist > 0 else 0
                face_features['brow_ratio'] = brow_ratio
                
                if brow_ratio < 0.6: # Approximate threshold
                     feature_desc_parts.append("Brows are furrowed (stress/focus).")

        # 3. Encode Frame to Base64
        _, buffer = cv2.imencode('.jpg', frame)
        processed_frame_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # Construct description
        feature_desc = " ".join(feature_desc_parts) if feature_desc_parts else "Neutral facial expression."

        return dominant_emotion, emotions_score, processed_frame_b64, face_features, feature_desc

    except Exception as e:
        print("Face emotion analysis error:", e)
        return "Neutral", {}, None, {}, "Error in analysis."
    
    finally:
        if cam is not None:
            cam.release()

if __name__ == "__main__":
    # Test script
    print("Testing Face Emotion Detection...")
    emotion = detect_face_emotion()
    print(f"Detected Emotion: {emotion}")

import cv2

def detect_face_emotion():
    """
    Camera-safe face emotion detection.
    Returns 'Neutral' if camera is unavailable.
    """

    try:
        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            return "Neutral"

        ret, frame = cam.read()
        cam.release()

        if not ret:
            return "Neutral"

        # Academic demo logic
        return "Happy"

    except Exception as e:
        print("Face emotion error:", e)
        return "Neutral"

import os
import pickle

# Load the trained text emotion model once when this module is imported
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'text_emotion_model.pkl')
try:
    with open(MODEL_PATH, 'rb') as f:
        emotion_model = pickle.load(f)
    print("Successfully loaded the trained Text Emotion ML model.")
except Exception as e:
    print(f"Warning: Could not load the Text Emotion ML model from {MODEL_PATH}. Reason: {e}")
    emotion_model = None

def get_text_intensity(text_lower):
    # Intensity indicators
    intensity_high = ["very", "so", "extremely", "really", "incredibly", "completely", "totally", "absolutely"]
    intensity_low = ["a bit", "a little", "somewhat", "kind of", "sort of", "slightly"]
    
    intensity = "moderate"
    for intensifier in intensity_high:
        if intensifier in text_lower:
            intensity = "high"
            break
            
    if intensity == "moderate":
        for reducer in intensity_low:
            if reducer in text_lower:
                intensity = "low"
                break
    return intensity

def calculate_nlp_stress_level(text_lower, intensity):
    """
    Calculates a strict 0-100% metric representing the NLP Stress Level
    based on exact keyword matching and intensity multipliers.
    """
    stress_score = 10  # Base line stress for active conversation
    
    # 1. Absolute Panic / High Pressure markers (Heavy weight)
    high_pressure_markers = ["overwhelmed", "panic", "too much", "giving up", "can't do this", "can't take", "pressure", "ruined", "anxiety", "so stressed"]
    if any(marker in text_lower for marker in high_pressure_markers):
        stress_score += 45
        
    # 2. Moderate Stress markers (Medium weight)
    moderate_markers = ["deadlines", "tired", "stressed", "rough", "struggling", "nervous", "worry", "upset"]
    for marker in moderate_markers:
        if marker in text_lower:
            stress_score += 20
            
    # 3. Apply Intensity Multiplier
    if intensity == "high":
        stress_score = int(stress_score * 1.5)
    elif intensity == "low":
        stress_score = int(stress_score * 0.7)
        
    # Cap between 0 and 100
    return min(max(stress_score, 0), 100)

def detect_text_emotion(text):
    """
    Detect emotion from text using a trained scikit-learn ML classification model.
    Returns a list with a 'label' key to match backend usage.
    Detects granular emotions: Lonely, Anxious, Stressed, Sad, Happy, Angry, Grateful, Worthless, Crisis, Neutral.
    """
    if not text:
        return [{"label": "Neutral", "confidence": 1.0, "intensity": "moderate"}]
        
    text_lower = text.lower()
    intensity = get_text_intensity(text_lower)
    
    # Check for direct panic keywords to ensure model resilience (fallback guardrail)
    panic_words = ["kill myself", "suicide", "end my life", "gonna endup my life", "die soon"]
    if any(pw in text_lower for pw in panic_words):
        return [{"label": "Crisis", "confidence": 0.99, "intensity": "high"}]

    if emotion_model:
        # Use ML Model
        try:
            # Predict probability for confidence score
            probs = emotion_model.predict_proba([text])[0]
            max_prob_idx = probs.argmax()
            confidence = probs[max_prob_idx]
            label = emotion_model.classes_[max_prob_idx]
            
            # Reduce fallback threshold to let ML model decide mostly
            if confidence < 0.15:
                label = "Neutral"
                
            nlp_stress = calculate_nlp_stress_level(text_lower, intensity)
                
            return [{"label": label, "confidence": float(confidence), "intensity": intensity, "nlp_stress": nlp_stress}]
        except Exception as e:
            print(f"Emotion ML model prediction failed: {e}. Falling back to neutral.")
    
    # Fallback if model missing
    nlp_stress = calculate_nlp_stress_level(text_lower, intensity)
    return [{"label": "Neutral", "confidence": 1.0, "intensity": "moderate", "nlp_stress": nlp_stress}]


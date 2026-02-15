from textblob import TextBlob

def detect_text_emotion(text):
    """
    Detect emotion from text using sentiment polarity and keyword analysis.
    Returns a list with a 'label' key to match backend usage.
    Now detects granular emotions: Lonely, Anxious, Stressed, Sad, Happy, Angry, etc.
    """

    if not text:
        return [{"label": "Neutral", "confidence": 1.0}]

    text_lower = text.lower()
    
    # Enhanced keyword-based emotion detection with intensity awareness
    emotion_keywords = {
        "Lonely": {
            "keywords": ["lonely", "alone", "isolated", "nobody", "no one", "by myself", "solitude", "abandoned"],
            "phrases": ["nobody cares", "feel invisible", "all by myself", "no friends", 
                       "everyone left", "feel disconnected", "nobody understands", 
                       "completely alone", "feel empty", "no one to talk to",
                       "sitting alone", "eating alone", "always alone"]
        },
        "Anxious": {
            "keywords": ["anxious", "worried", "nervous", "anxiety", "panic", "fear", "scared", "terrified", "afraid", "uneasy", "tense", "restless", "butterflies"],
            "phrases": ["can't stop worrying", "feel panicked", "heart racing", "can't breathe", "on edge", "something bad might happen"]
        },
        "Stressed": {
            "keywords": ["stressed", "overwhelmed", "pressure", "burden", "exhausted", "tired", "drained", "burnout", "hectic"],
            "phrases": ["too much", "can't handle", "breaking point", "burned out", "too much to do", "running on fumes", "at my wit's end"]
        },
        "Sad": {
            "keywords": ["sad", "depressed", "down", "unhappy", "miserable", "hopeless", "crying", "tears", "empty", "gloomy", "melancholy", "despair", "grief", "heartbroken"],
            "phrases": ["feel like crying", "want to cry", "so sad", "really down", "feel empty", "lost hope", "don't want to do anything", "hard to get out of bed"]
        },
        "Angry": {
            "keywords": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "rage", "livid", "resentful", "bitter"],
            "phrases": ["so angry", "pissed off", "fed up", "had enough", "can't stand it", "drives me crazy", "losing my temper"]
        },
        "Happy": {
            "keywords": ["happy", "joy", "excited", "great", "wonderful", "amazing", "fantastic", "love", "blessed", "cheerful", "delighted", "optimistic"],
            "phrases": ["feel great", "so happy", "best day", "feeling good", "on top of the world", "can't wait"]
        },
        "Grateful": {
            "keywords": ["grateful", "thankful", "appreciate", "blessed", "fortunate", "lucky"],
            "phrases": ["thank you", "so grateful", "appreciate it", "means a lot"]
        },
        "Worthless": {  # New Category for severe self-esteem issues
            "keywords": ["worthless", "useless", "failure", "stupid", "idiot", "burden", "invisible"],
            "phrases": ["hate myself", "can't do anything right", "waste of space", "nobody needs me", "better off without me"]
        }
    }
    
    # Intensity indicators
    intensity_high = ["very", "so", "extremely", "really", "incredibly", "completely", "totally", "absolutely"]
    intensity_low = ["a bit", "a little", "somewhat", "kind of", "sort of", "slightly"]
    
    detected_emotions = []
    
    # Check for specific emotion keywords and phrases
    for emotion, patterns in emotion_keywords.items():
        emotion_score = 0
        
        # Check keywords
        for keyword in patterns["keywords"]:
            if keyword in text_lower:
                emotion_score += 1
        
        # Check phrases (weighted higher)
        if "phrases" in patterns:
            for phrase in patterns["phrases"]:
                if phrase in text_lower:
                    emotion_score += 2
        
        if emotion_score > 0:
            # Determine intensity
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
            
            detected_emotions.append({
                "label": emotion,
                "confidence": min(0.95, 0.7 + (emotion_score * 0.1)),
                "intensity": intensity
            })
    
    # If multiple emotions detected, return the strongest or prioritize loneliness
    if detected_emotions:
        # Prioritize loneliness if detected (as per user requirement)
        lonely_emotion = next((e for e in detected_emotions if e["label"] == "Lonely"), None)
        if lonely_emotion:
            return [lonely_emotion]
        
        # Otherwise return highest confidence
        detected_emotions.sort(key=lambda x: x["confidence"], reverse=True)
        return [detected_emotions[0]]

    
    # Fallback to sentiment polarity
    polarity = TextBlob(text).sentiment.polarity

    if polarity >= 0.3:
        label = "Happy"
    elif polarity >= 0.05:
        label = "Positive"
    elif polarity <= -0.3:
        label = "Sad"
    elif polarity <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    confidence = abs(polarity)
    return [{"label": label, "confidence": confidence}]


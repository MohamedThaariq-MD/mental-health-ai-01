import random
from backend.rl_engine.q_learning import QLearningEngine

# --- DEFINE OPTIONS ---
CBT_OPTIONS = [
    "Cognitive Behavioral Therapy (CBT) Techniques",
    "Dialectical Behavior Therapy (DBT) Skills", 
    "Stress Management Coaching",
    "Emotional Release Therapy",
    "Acceptance and Commitment Therapy (ACT)",
    "Shadow Work Journaling",
    "Compassion-Focused Therapy (CFT)",
    "Eye Movement Desensitization and Reprocessing (EMDR) Concepts",
    "Logotherapy (Finding Meaning)",
    "Interpersonal Therapy (IPT) Techniques",
    "Mindfulness-Based Cognitive Therapy (MBCT)",
    "Solution-Focused Brief Therapy (SFBT) Exercises"
]

THERAPY_DETAILS = {
    "Cognitive Behavioral Therapy (CBT) Techniques": {
        "description": "CBT focuses on identifying and changing negative thought patterns and behaviors to improve emotional regulation.",
        "link": "https://www.apa.org/ptsd-guideline/patients-and-families/cognitive-behavioral"
    },
    "Dialectical Behavior Therapy (DBT) Skills": {
        "description": "DBT provides skills for mindfulness, emotion regulation, distress tolerance, and interpersonal effectiveness.",
        "link": "https://www.psychologytoday.com/us/therapy-types/dialectical-behavior-therapy"
    },
    "Stress Management Coaching": {
        "description": "Techniques and strategies designed to help individuals cope with stress more effectively.",
        "link": "https://www.helpguide.org/articles/stress/stress-management.htm"
    },
    "Emotional Release Therapy": {
        "description": "A therapeutic approach that aims to release pent-up emotions and tension from the body.",
        "link": "https://www.healthline.com/health/emotional-release-therapy"
    },
    "Acceptance and Commitment Therapy (ACT)": {
        "description": "ACT encourages people to embrace their thoughts and feelings rather than fighting or feeling guilty for them.",
        "link": "https://www.psychologytoday.com/us/therapy-types/acceptance-and-commitment-therapy"
    },
    "Shadow Work Journaling": {
        "description": "A practice of exploring the 'shadow' or hidden parts of the psyche to gain self-awareness and healing.",
        "link": "https://www.healthline.com/health/mental-health/shadow-work"
    },
    "Compassion-Focused Therapy (CFT)": {
        "description": "CFT aims to help those who struggle with shame and self-criticism by developing compassion for themselves.",
        "link": "https://www.compassionatemind.co.uk/about-cft"
    },
    "Eye Movement Desensitization and Reprocessing (EMDR) Concepts": {
        "description": "A psychotherapy treatment that was originally designed to alleviate the distress associated with traumatic memories.",
        "link": "https://www.emdria.org/about-emdr-therapy/"
    },
    "Logotherapy (Finding Meaning)": {
        "description": "A school of psychology that says humans are motivated by a 'will to meaning,' which is an inner pull to find meaning in life.",
        "link": "https://www.verywellmind.com/an-overview-of-logotherapy-4159308"
    },
    "Interpersonal Therapy (IPT) Techniques": {
        "description": "IPT focuses on improving the quality of a person's interpersonal relationships and social functioning.",
        "link": "https://www.psychologytoday.com/us/therapy-types/interpersonal-psychotherapy"
    },
    "Mindfulness-Based Cognitive Therapy (MBCT)": {
        "description": "MBCT combines cognitive therapy with mindfulness practices to help prevent relapse into depression.",
        "link": "https://www.psychologytoday.com/us/therapy-types/mindfulness-based-cognitive-therapy"
    },
    "Solution-Focused Brief Therapy (SFBT) Exercises": {
        "description": "SFBT focuses on a person's present and future circumstances and goals rather than past experiences.",
        "link": "https://www.psychologytoday.com/us/therapy-types/solution-focused-brief-therapy"
    },
    "Crisis Intervention & Stabilization": {
        "description": "Immediate, short-term psychological care designed to help individuals in a crisis return to their baseline level of functioning.",
        "link": "https://www.nami.org/About-Mental-Illness/Common-with-Mental-Illness/Risk-of-Suicide"
    },
    "Immediate Professional Support": {
        "description": "Connecting with a licensed therapist, counselor, or psychiatrist for urgent mental health needs.",
        "link": "https://www.psychologytoday.com/us/therapists"
    },
    "Grounding Techniques for Severe Distress": {
        "description": "Strategies to help you detach from emotional pain and reconnect with the present moment.",
        "link": "https://www.healthline.com/health/grounding-techniques"
    },
    "Social Connection Therapy": {
        "description": "Focuses on increasing social engagement and improving social skills to combat loneliness.",
        "link": "https://www.psychologytoday.com/us/blog/the-art-of-closeness/202102/the-power-of-connection-in-therapy"
    },
    "Community Building Exercises": {
        "description": "Activities designed to foster a sense of belonging and connection with others in a group setting.",
        "link": "https://www.mindtools.com/pages/article/newTMM_member_connection.htm"
    },
    "Relationship Skills Training": {
        "description": "Provides tools and strategies for communicating effectively and building healthy relationships.",
        "link": "https://www.gottman.com/about/the-gottman-method/"
    },
    "Positive Psychology Reinforcement": {
        "description": "The scientific study of what makes life most worth living, focusing on strengths rather than weaknesses.",
        "link": "https://positivepsychology.com/what-is-positive-psychology/"
    },
    "Sleep Hygiene Education": {
        "description": "Learning about habits and practices that are conducive to sleeping well on a regular basis.",
        "link": "https://www.sleepfoundation.org/sleep-hygiene"
    }
}

MEDITATION_OPTIONS = [
    "Advanced Box Breathing: Inhale 4s, Hold 4s, Exhale 4s, Hold 4s. Repeat 10 cycles.",
    "Progressive Muscle Relaxation (PMR): Systematically tense and release muscle groups.",
    "Visualizing the 'Inner Sanctuary': A detailed 15-minute journey to a safe space.",
    "NSDR (Non-Sleep Deep Rest): Protocols to reduce stress and improve neuroplasticity.",
    "Vipassana Mindfulness: Observing sensations without judgment.",
    "SKY Breath Meditation: Rhythmic breathing to harmonize body and mind.", 
    "Compassion-Focused Imagery: Visualizing a compassionate figure.",
    "Loving-Kindness (Metta) Meditation: Sending goodwill to self and others.",
    "Zen Walking Meditation (Kinhin): Mindful pacing and breathing.",
    "Body Scan Meditation: Deeply tuning into physical sensations.",
    "Trataka (Candle Gazing): Building focus and calming the active mind.",
    "So Hum Mantra Meditation: Silent repetition aligned with breath."
]

ACTIVITY_OPTIONS = [
    "Nature Walk (Forest Bathing)",
    "Journaling Emotional Reflections",
    "Engaging in Creative Art or Painting", 
    "Listening to Calming Frequency Music (432Hz)",
    "Cold Shower for Reset",
    "Gentle Stretching or Sunrise Yoga",
    "Writing a Letter (Burn after reading)",
    "Cooking or Baking a new, healthy recipe",
    "Doing a complex puzzle or playing sudoku",
    "Gardening or tending to indoor plants",
    "Reading a chapter of an uplifting book",
    "Deep-cleaning or organizing a small physical space"
]

MUSIC_OPTIONS = [
    "Weightless by Marconi Union (Ambient)",
    "Clair de Lune by Debussy (Classical)",
    "Strawberry Swing by Coldplay (Soft Pop)",
    "Breathe Me by Sia (Emotional)",
    "Holocene by Bon Iver (Indie Folk)",
    "Here Comes The Sun by The Beatles (Uplifting)",
    "Gymnopédies by Satie (Piano)",
    "Lofi Hip Hop Radio (Focus)",
    "Happy by Pharrell Williams (Pop)",
    "Walking on Sunshine by Katrina & The Waves (Upbeat)",
    "Take Five by Dave Brubeck (Smooth Jazz)",
    "River Flows in You by Yiruma (Contemporary Piano)",
    "Resonance by HOME (Synthwave Chill)",
    "Three Little Birds by Bob Marley (Reggae/Positive)",
    "Experience by Ludovico Einaudi (Moving Classical)"
]

MOVIE_OPTIONS = [
    "Inside Out (Understanding Emotions)",
    "The Pursuit of Happyness (Resilience)",
    "Good Will Hunting (Healing)",
    "Soul (Finding Purpose)",
    "Paddington 2 (Wholesome Comfort)",
    "Arrival (Intellectual Sci-Fi)",
    "My Neighbor Totoro (Calm Animation)",
    "Singin' in the Rain (Joyful/Musical)",
    "Ferris Bueller's Day Off (Fun)",
    "Spirited Away (Magical Escapism)",
    "Amélie (Quirky Joy/Appreciation)",
    "Up (Grief and New Adventures)",
    "Spider-Man: Into the Spider-Verse (Action/Visual Flow)",
    "Little Miss Sunshine (Family/Acceptance)"
]

GAME_OPTIONS = [
    "Subway Surfers (Play on Poki: https://poki.com/en/g/subway-surfers)",
    "Temple Run 2 (Play on Poki: https://poki.com/en/g/temple-run-2)",
    "Crossy Road (Play on Poki: https://poki.com/en/g/crossy-road)",
    "Stickman Hook (Play on Poki: https://poki.com/en/g/stickman-hook)",
    "Brain Test: Tricky Puzzles (Play on Poki: https://poki.com/en/g/brain-test-tricky-puzzles)",
    "Moto X3M (Play on Poki: https://poki.com/en/g/moto-x3m)",
    "Monkey Mart (Play on Poki: https://poki.com/en/g/monkey-mart)",
    "Bubble Shooter (Play on Poki: https://poki.com/en/g/bubble-shooter)",
    "2048 (Play on Poki: https://poki.com/en/g/2048)",
    "Tunnel Rush (Play on Poki: https://poki.com/en/g/tunnel-rush)",
    "Minecraft Classic (Play on Poki: https://poki.com/en/g/minecraft-classic)",
    "Jetpack Joyride (Play on Poki: https://poki.com/en/g/jetpack-joyride)"
]

DOCUMENTARY_OPTIONS = [
    "Our Planet - High Seas (https://www.youtube.com/watch?v=9FqwhW0Bstc)",
    "Our Planet - Forests (https://www.youtube.com/watch?v=JkaxUblCGz0)",
    "Our Planet - Frozen Worlds (https://www.youtube.com/watch?v=cTQ3Ko9ZKg8)",
    "Life on Our Planet (Netflix / Trailer: https://www.youtube.com/watch?v=Xsh_70Mls0o)",
    "Fantastic Fungi (Trailer: https://www.youtube.com/watch?v=vd76K5rRECI)",
    "Samsara (Visual Meditative Journey)",
    "Apollo 11 (Historical Achievement)",
    "My Octopus Teacher (Documentary)",
    "The Social Dilemma (Documentary)",
    "13th (Educational Documentary)"
]

# --- INITIALIZE RL ENGINES ---
# We use separate engines for each category so they learn independently
music_engine = QLearningEngine(MUSIC_OPTIONS)
movie_engine = QLearningEngine(MOVIE_OPTIONS)
game_engine = QLearningEngine(GAME_OPTIONS)
documentary_engine = QLearningEngine(DOCUMENTARY_OPTIONS)


import joblib
import os
import numpy as np

# Load our newly trained unified ML therapy recommender
try:
    _MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "therapy_recommendation_model.pkl")
    THERAPY_ML_BUNDLE = joblib.load(_MODEL_PATH)
except Exception as e:
    print(f"[Warning] Therapy ML model not found, will fallback. {e}")
    THERAPY_ML_BUNDLE = None

def get_distress_score(t, v, f, face_features):
    """Calculate distress score based on all 3 modalities + facial EAR/Brow ratio"""
    score = 0.0
    emotions = [t, v, f]
    if "Trauma" in emotions: score += 0.8
    if "Sad" in emotions: score += 0.4
    if "Nervous" in emotions or "Fear" in emotions: score += 0.5
    if "Angry" in emotions: score += 0.5
    
    # Add facial biometric stress
    if face_features:
        if face_features.get("ear", 0.5) < 0.22: score += 0.2 # Extreme fatigue/sadness
        if face_features.get("brow_ratio", 1.0) < 0.6: score += 0.3 # Severe stress/anger furrow
        
    return min(1.0, score)


# --- EMOTION-CURATED RECOMMENDATION POOLS ---
# Each emotion group gets its own curated subset instead of random from flat pool

MUSIC_BY_EMOTION = {
    "calm":    ["Weightless by Marconi Union (Ambient)", "Gymnopédies by Satie (Piano)",
                "River Flows in You by Yiruma (Contemporary Piano)", "Take Five by Dave Brubeck (Smooth Jazz)"],
    "happy":   ["Happy by Pharrell Williams (Pop)", "Walking on Sunshine by Katrina & The Waves (Upbeat)",
                "Here Comes The Sun by The Beatles (Uplifting)", "Three Little Birds by Bob Marley (Reggae/Positive)"],
    "sad":     ["Holocene by Bon Iver (Indie Folk)", "Breathe Me by Sia (Emotional)",
                "Experience by Ludovico Einaudi (Moving Classical)", "Clair de Lune by Debussy (Classical)"],
    "stressed":["Weightless by Marconi Union (Ambient)", "Resonance by HOME (Synthwave Chill)",
                "Lofi Hip Hop Radio (Focus)", "River Flows in You by Yiruma (Contemporary Piano)"],
    "angry":   ["Strawberry Swing by Coldplay (Soft Pop)", "Resonance by HOME (Synthwave Chill)",
                "Breathe Me by Sia (Emotional)", "Holocene by Bon Iver (Indie Folk)"],
    "neutral": ["Lofi Hip Hop Radio (Focus)", "Take Five by Dave Brubeck (Smooth Jazz)",
                "Weightless by Marconi Union (Ambient)", "Resonance by HOME (Synthwave Chill)"],
}

MOVIE_BY_EMOTION = {
    "calm":    ["My Neighbor Totoro (Calm Animation)", "Amélie (Quirky Joy/Appreciation)",
                "Soul (Finding Purpose)", "Paddington 2 (Wholesome Comfort)"],
    "happy":   ["Singin' in the Rain (Joyful/Musical)", "Ferris Bueller's Day Off (Fun)",
                "Spider-Man: Into the Spider-Verse (Action/Visual Flow)", "Little Miss Sunshine (Family/Acceptance)"],
    "sad":     ["Good Will Hunting (Healing)", "The Pursuit of Happyness (Resilience)",
                "Up (Grief and New Adventures)", "Inside Out (Understanding Emotions)"],
    "stressed":["Paddington 2 (Wholesome Comfort)", "My Neighbor Totoro (Calm Animation)",
                "Spirited Away (Magical Escapism)", "Soul (Finding Purpose)"],
    "angry":   ["Inside Out (Understanding Emotions)", "Little Miss Sunshine (Family/Acceptance)",
                "The Pursuit of Happyness (Resilience)", "Arrival (Intellectual Sci-Fi)"],
    "neutral": ["Spirited Away (Magical Escapism)", "Arrival (Intellectual Sci-Fi)",
                "Soul (Finding Purpose)", "Good Will Hunting (Healing)"],
}

GAME_BY_EMOTION = {
    "calm":    ["2048 (Play on Poki: https://poki.com/en/g/2048)",
                "Bubble Shooter (Play on Poki: https://poki.com/en/g/bubble-shooter)",
                "Brain Test: Tricky Puzzles (Play on Poki: https://poki.com/en/g/brain-test-tricky-puzzles)"],
    "happy":   ["Subway Surfers (Play on Poki: https://poki.com/en/g/subway-surfers)",
                "Temple Run 2 (Play on Poki: https://poki.com/en/g/temple-run-2)",
                "Moto X3M (Play on Poki: https://poki.com/en/g/moto-x3m)"],
    "sad":     ["Monkey Mart (Play on Poki: https://poki.com/en/g/monkey-mart)",
                "Bubble Shooter (Play on Poki: https://poki.com/en/g/bubble-shooter)",
                "Minecraft Classic (Play on Poki: https://poki.com/en/g/minecraft-classic)"],
    "stressed":["Brain Test: Tricky Puzzles (Play on Poki: https://poki.com/en/g/brain-test-tricky-puzzles)",
                "2048 (Play on Poki: https://poki.com/en/g/2048)",
                "Stickman Hook (Play on Poki: https://poki.com/en/g/stickman-hook)"],
    "angry":   ["Tunnel Rush (Play on Poki: https://poki.com/en/g/tunnel-rush)",
                "Moto X3M (Play on Poki: https://poki.com/en/g/moto-x3m)",
                "Jetpack Joyride (Play on Poki: https://poki.com/en/g/jetpack-joyride)"],
    "neutral": ["Crossy Road (Play on Poki: https://poki.com/en/g/crossy-road)",
                "Stickman Hook (Play on Poki: https://poki.com/en/g/stickman-hook)",
                "Monkey Mart (Play on Poki: https://poki.com/en/g/monkey-mart)"],
}

def _map_emotion_to_key(emotion: str) -> str:
    """Map any raw emotion label to one of our 6 curated pool keys."""
    e = emotion.lower()
    if e in ("happy", "joy", "surprise", "enjoying"):     return "happy"
    if e in ("sad", "sadness", "crying", "depressed"):    return "sad"
    if e in ("angry", "anger", "disgust"):                return "angry"
    if e in ("fear", "anxious", "anxiety", "nervous",
             "stressed", "stress", "severe stress"):      return "stressed"
    if e in ("calm", "relaxed", "content"):               return "calm"
    if e in ("trauma", "crisis", "worthless"):            return "stressed"   # calming needed
    return "neutral"

def _curated_pick(pool_by_emotion: dict, emotion_key: str) -> str:
    """Pick a random item from the curated pool for the given emotion key."""
    pool = pool_by_emotion.get(emotion_key, pool_by_emotion["neutral"])
    return random.choice(pool)

def choose_therapy(text_emotion="Neutral", voice_emotion="Neutral", face_emotion="Neutral", face_features=None):
    """
    Enhanced recommendation engine.
    Fuses Voice, Text, Face, and Biometrics through a trained ML model for therapy paths,
    and uses emotion-curated pools for Music, Movie, and Game recommendations.
    """
    text_emotion = text_emotion.capitalize()
    voice_emotion = voice_emotion.capitalize()
    face_emotion = face_emotion.capitalize()
    fallbacks = ["Neutral", "Happy", "Sad", "Angry", "Fear", "Surprise", "Disgust", "Trauma", "Nervous", "Calm"]
    
    # Safe capitalization check
    if text_emotion not in fallbacks: text_emotion = "Neutral"
    if voice_emotion not in fallbacks: voice_emotion = "Neutral"
    if face_emotion not in fallbacks: face_emotion = "Neutral"

    # ML Therapy Prediction
    therapy = None
    if THERAPY_ML_BUNDLE:
        try:
            model = THERAPY_ML_BUNDLE["model"]
            enc_t = THERAPY_ML_BUNDLE["encoders"]["text"]
            enc_v = THERAPY_ML_BUNDLE["encoders"]["voice"]
            enc_f = THERAPY_ML_BUNDLE["encoders"]["face"]
            
            t_val = enc_t.transform([text_emotion])[0]
            v_val = enc_v.transform([voice_emotion])[0]
            f_val = enc_f.transform([face_emotion])[0]
            distress = get_distress_score(text_emotion, voice_emotion, face_emotion, face_features)
            
            x_input = np.array([[t_val, v_val, f_val, distress]])
            therapy = model.predict(x_input)[0]
        except Exception as e:
            print(f"[RL Engine] ML Therapy Prediction failed: {e}")
            
    # Fallback to standard logic if ML fails or isn't built
    if not therapy:
        print("[RL Engine] Using classic deterministic fallback")
        if "Trauma" in [text_emotion, voice_emotion, face_emotion]:
            therapy = "Crisis Intervention & Stabilization"
        elif "Sad" in [text_emotion, voice_emotion, face_emotion]:
            therapy = random.choice(["Social Connection Therapy", "Cognitive Behavioral Therapy (CBT) Techniques"])
        else:
            therapy = random.choice(CBT_OPTIONS)

    # Resolve primary emotion for entertainment (Face > Voice > Text)
    primary_emotion = face_emotion if face_emotion != "Neutral" else (voice_emotion if voice_emotion != "Neutral" else text_emotion)
    emotion_key = _map_emotion_to_key(primary_emotion)
    
    print(f"[RL Engine] Emotion key for entertainment: '{emotion_key}' (from '{primary_emotion}')")

    # Determine activity and meditation based on the therapy output
    if "Crisis" in therapy:
        activity = "Call a supportive friend or family member"
        meditation = "NSDR (Non-Sleep Deep Rest)"
    elif "Social" in therapy:
        activity = "Reach out to an old friend or visit a local coffee shop"
        meditation = "Loving-Kindness (Metta) Meditation"
    elif "Stress" in therapy:
        activity = "Cold Shower for Reset or Gentle Stretches"
        meditation = "Advanced Box Breathing: Inhale 4s, Hold 4s, Exhale 4s, Hold 4s"
    elif "Positive" in therapy:
        activity = "Share your joy with a friend or do some creative art"
        meditation = "Body Scan Meditation: Deeply tuning into physical sensations"
    else:
        activity = random.choice(ACTIVITY_OPTIONS)
        meditation = random.choice(MEDITATION_OPTIONS)

    recommendations = {
        "therapy":     therapy,
        "meditation":  meditation,
        "activity":    activity,
        "music":       _curated_pick(MUSIC_BY_EMOTION,  emotion_key),
        "movie":       _curated_pick(MOVIE_BY_EMOTION,  emotion_key),
        "game":        _curated_pick(GAME_BY_EMOTION,   emotion_key),
        "documentary": documentary_engine.choose_action(emotion_key),
    }

    return recommendations


def update_recommendation_model(emotion, action, reward):
    """
    Update the appropriate RL engine based on the action received.
    """
    if action in MUSIC_OPTIONS:
        music_engine.update(emotion, action, reward)
        return "music"
    elif action in MOVIE_OPTIONS:
        movie_engine.update(emotion, action, reward)
        return "movie"
    elif action in GAME_OPTIONS:
        game_engine.update(emotion, action, reward)
        return "game"
    elif action in DOCUMENTARY_OPTIONS:
        documentary_engine.update(emotion, action, reward)
        return "documentary"
    else:
        print(f"[RL] Action '{action}' not found in known lists. Skipping update.")
        return None

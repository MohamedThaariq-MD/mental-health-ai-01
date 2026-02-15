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
    "Compassion-Focused Therapy (CFT)"
]

MEDITATION_OPTIONS = [
    "Advanced Box Breathing: Inhale 4s, Hold 4s, Exhale 4s, Hold 4s. Repeat 10 cycles.",
    "Progressive Muscle Relaxation (PMR): Systematically tense and release muscle groups.",
    "Visualizing the 'Inner Sanctuary': A detailed 15-minute journey to a safe space.",
    "NSDR (Non-Sleep Deep Rest): Protocols to reduce stress and improve neuroplasticity.",
    "Vipassana Mindfulness: Observing sensations without judgment.",
    "SKY Breath Meditation: Rhythmic breathing to harmonize body and mind.", 
    "Compassion-Focused Imagery: Visualizing a compassionate figure."
]

ACTIVITY_OPTIONS = [
    "Nature Walk (Forest Bathing)",
    "Journaling Emotional Reflections",
    "Engaging in Creative Art or Painting", 
    "Listening to Calming Frequency Music (432Hz)",
    "Cold Shower for Reset",
    "Gentle Stretching",
    "Writing a Letter (Burn after reading)"
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
    "Walking on Sunshine by Katrina & The Waves (Upbeat)"
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
    "Ferris Bueller's Day Off (Fun)"
]

GAME_OPTIONS = [
    "Journey (Meditative Exploration)",
    "Abzu (Underwater Relaxation)",
    "Gris (Emotional Healing)",
    "Animal Crossing (Cozy Socializing)",
    "Minecraft (Creative Zen)",
    "Stardew Valley (Farming Sim)",
    "Tetris Effect (Flow State)",
    "Sky: Children of the Light (Social Adventure)",
    "Super Mario Odyssey (Joyful Adventure)",
    "Just Dance (Physical Fun)"
]

# --- INITIALIZE RL ENGINES ---
# We use separate engines for each category so they learn independently
music_engine = QLearningEngine(MUSIC_OPTIONS)
movie_engine = QLearningEngine(MOVIE_OPTIONS)
game_engine = QLearningEngine(GAME_OPTIONS)


def choose_therapy(emotion, face_features=None):
    """
    Enhanced recommendation engine with Reinforcement Learning.
    Returns a dictionary with therapy, meditation, and activity suggestions.
    """
    emotion = emotion.lower()

    # --- GEOMETRIC FEATURE OVERRIDES ---
    if face_features:
        # Check for Drowsiness (Low EAR)
        ear = face_features.get("ear", 0.5)
        if ear < 0.22:
            return {
                "therapy": "Sleep Hygiene Education",
                "meditation": "NSDR (Non-Sleep Deep Rest)",
                "activity": "Power Nap (20 mins)",
                "music": music_engine.choose_action(emotion),
                "movie": movie_engine.choose_action(emotion),
                "game": game_engine.choose_action(emotion)
            }
        
        # Check for High Stress (High Brow Furrow / Low Ratio)
        brow_ratio = face_features.get("brow_ratio", 1.0)
        if brow_ratio < 0.55:
            # We enforce therapy but randomize entertainment
            therapy = "Stress Management Coaching"
            meditation = "Progressive Muscle Relaxation (PMR)"
            activity = "Gentle Neck & Shoulder Stretches"
            if emotion not in ["happy", "surprise"]:
                 return {
                    "therapy": therapy,
                    "meditation": meditation,
                    "activity": activity,
                    "music": music_engine.choose_action(emotion),
                    "movie": movie_engine.choose_action(emotion),
                    "game": game_engine.choose_action(emotion)
                 }

    # --- STANDARD LOGIC ---
    # Therapy/Meditation/Activity - Keep random for variety (or could add RL here too)
    
    if "lonely" in emotion or "isolated" in emotion:
        therapy = random.choice([
            "Social Connection Therapy", "Community Building Exercises", "Relationship Skills Training"
        ])
        activity = random.choice([
            "Reach out to an old friend", "Join an online community", "Visit a local coffee shop"
        ])
    elif "happy" in emotion or "positive" in emotion:
        therapy = "Positive Psychology Reinforcement"
        activity = "Share your joy with a friend"
    else:
        therapy = random.choice(CBT_OPTIONS)
        activity = random.choice(ACTIVITY_OPTIONS)

    # Use RL Engines for Entertainment
    # The engines will start random (exploration) and become smarter (exploitation)
    recommendations = {
        "therapy": therapy,
        "meditation": random.choice(MEDITATION_OPTIONS),
        "activity": activity,
        "music": music_engine.choose_action(emotion),
        "movie": movie_engine.choose_action(emotion),
        "game": game_engine.choose_action(emotion)
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
    else:
        print(f"[RL] Action '{action}' not found in known lists. Skipping update.")
        return None

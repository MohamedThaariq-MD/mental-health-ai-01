import random

def choose_therapy(emotion):
    """
    Simple RL-inspired therapy selection.
    Returns a therapy based on detected emotion.
    """

    emotion = emotion.lower()

    if emotion in ["negative", "sad", "stressed", "angry"]:
        return random.choice([
            "Deep Breathing",
            "Meditation",
            "Relaxing Music",
            "AI Chat Support"
        ])

    elif emotion in ["positive", "happy"]:
        return random.choice([
            "Gratitude Journaling",
            "Positive Affirmations",
            "Mindfulness Exercise"
        ])

    else:
        return random.choice([
            "Mindfulness Exercise",
            "Light Stretching",
            "Calm Music"
        ])

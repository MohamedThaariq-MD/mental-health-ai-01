import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "mental_health.db")

def init_db():
    """Initializes the database and creates the necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            text_input TEXT,
            text_emotion TEXT,
            face_emotion TEXT,
            final_emotion TEXT,
            therapy TEXT,
            meditation TEXT,
            activity TEXT
        )
    ''')

    # New table for conversation history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_text TEXT,
            ai_response TEXT,
            emotion TEXT,
            emotion_intensity TEXT
        )
    ''')
    
    # Table for Long-Term Memory (Facts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default_user',
            fact_content TEXT NOT NULL,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for RL Feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            emotion TEXT,
            action TEXT,
            reward INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def save_analysis(text_input, text_emotion, face_emotion, final_emotion, recs):
    """Saves analysis results and recommendations to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analysis_history (
                text_input, text_emotion, face_emotion, final_emotion, 
                therapy, meditation, activity
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            text_input, 
            text_emotion, 
            face_emotion, 
            final_emotion, 
            recs.get("therapy"), 
            recs.get("meditation"), 
            recs.get("activity")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def save_conversation_turn(session_id, user_text, ai_response, emotion, emotion_intensity="moderate"):
    """Save a single conversation turn to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_history (
                session_id, user_text, ai_response, emotion, emotion_intensity
            ) VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_text, ai_response, emotion, emotion_intensity))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error saving conversation: {e}")
        return False

def get_conversation_history(session_id, limit=10):
    """Retrieve conversation history for a session."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, user_text, ai_response, emotion, emotion_intensity
            FROM conversation_history
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts (reversed to chronological order)
        history = []
        for row in reversed(rows):
            history.append({
                "timestamp": row[0],
                "user_text": row[1],
                "ai_response": row[2],
                "emotion": row[3],
                "emotion_intensity": row[4]
            })
        return history
    except Exception as e:
        print(f"Database error retrieving conversation: {e}")
        return []

def get_previous_emotional_state(current_session_id):
    """
    Retrieve the last emotional state from a DIFFERENT session.
    Useful for "Yesterday you felt..." type responses.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Find the most recent entry from a different session
        cursor.execute('''
            SELECT timestamp, emotion, emotion_intensity
            FROM conversation_history
            WHERE session_id != ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (current_session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "timestamp": row[0],
                "emotion": row[1],
                "intensity": row[2]
            }
        return None
        
    except Exception as e:
        print(f"Database error retrieving previous state: {e}")
        return None

# --- LONG TERM MEMORY FUNCTIONS ---

def save_user_fact(fact_content, category="general", user_id="default_user"):
    """Save a specific fact about the user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_facts (user_id, fact_content, category)
            VALUES (?, ?, ?)
        ''', (user_id, fact_content, category))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error saving fact: {e}")
        return False

def get_user_facts(user_id="default_user"):
    """Retrieve all facts about a user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT fact_content, category, timestamp
            FROM user_facts
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        facts = []
        for row in rows:
            facts.append({
                "content": row[0],
                "category": row[1],
                "timestamp": row[2]
            })
        return facts
    except Exception as e:
        print(f"Database error retrieving facts: {e}")
        return []

# --- RL FEEDBACK FUNCTIONS ---

def save_feedback(session_id, emotion, action, reward):
    """Save user feedback for RL training."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feedback_history (session_id, emotion, action, reward)
            VALUES (?, ?, ?, ?)
        ''', (session_id, emotion, action, reward))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error saving feedback: {e}")
        return False

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")

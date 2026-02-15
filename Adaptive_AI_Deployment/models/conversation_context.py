"""
Conversation Context System
Tracks dialogue history and builds context-aware responses for more natural,
friend-like conversations that build rapport over time.
"""

from datetime import datetime
from collections import deque
from typing import List, Dict, Optional


class ConversationMemory:
    """
    Manages conversation history and context for building rapport with users.
    Tracks recent exchanges, identifies recurring themes, and determines relationship stage.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of conversation turns to remember
        """
        self.max_history = max_history
        self.exchanges = deque(maxlen=max_history)
        self.themes = {}  # Track recurring themes and their frequency
        self.start_time = datetime.now()
        self.total_exchanges = 0
        
    def add_exchange(self, user_text: str, ai_response: str, emotion: str, 
                     emotion_intensity: str = "moderate"):
        """
        Add a conversation exchange to memory.
        
        Args:
            user_text: What the user said
            ai_response: How the AI responded
            emotion: Detected emotion
            emotion_intensity: Intensity level (mild, moderate, severe)
        """
        exchange = {
            "timestamp": datetime.now(),
            "user_text": user_text,
            "ai_response": ai_response,
            "emotion": emotion,
            "intensity": emotion_intensity,
            "turn_number": self.total_exchanges + 1
        }
        
        self.exchanges.append(exchange)
        self.total_exchanges += 1
        
        # Update theme tracking
        emotion_lower = emotion.lower()
        if emotion_lower in self.themes:
            self.themes[emotion_lower] += 1
        else:
            self.themes[emotion_lower] = 1
    
    def get_recent_exchanges(self, count: int = 5) -> List[Dict]:
        """Get the most recent conversation exchanges."""
        return list(self.exchanges)[-count:] if self.exchanges else []
    
    def get_conversation_summary(self) -> Dict:
        """
        Generate a summary of the conversation so far.
        
        Returns:
            Dict with conversation statistics and insights
        """
        if not self.exchanges:
            return {
                "total_turns": 0,
                "duration_minutes": 0,
                "dominant_emotion": "neutral",
                "recurring_themes": [],
                "relationship_stage": "new"
            }
        
        duration = (datetime.now() - self.start_time).total_seconds() / 60
        dominant_emotion = max(self.themes.items(), key=lambda x: x[1])[0] if self.themes else "neutral"
        
        # Get recurring themes (emotions mentioned 2+ times)
        recurring = [theme for theme, count in self.themes.items() if count >= 2]
        
        return {
            "total_turns": self.total_exchanges,
            "duration_minutes": round(duration, 1),
            "dominant_emotion": dominant_emotion,
            "recurring_themes": recurring,
            "relationship_stage": self.get_relationship_stage()
        }
    
    def detect_recurring_themes(self) -> List[str]:
        """
        Identify emotions/themes that keep appearing in the conversation.
        
        Returns:
            List of recurring emotional themes
        """
        # Themes that appear in 30%+ of exchanges are considered recurring
        threshold = max(2, self.total_exchanges * 0.3)
        return [theme for theme, count in self.themes.items() if count >= threshold]
    
    def get_relationship_stage(self) -> str:
        """
        Determine the stage of the relationship based on conversation history.
        
        Returns:
            "new", "building", or "established"
        """
        if self.total_exchanges <= 2:
            return "new"
        elif self.total_exchanges <= 5:
            return "building"
        else:
            return "established"
    
    def get_emotion_trend(self) -> str:
        """
        Analyze if emotions are improving, declining, or stable.
        
        Returns:
            "improving", "declining", "stable", or "unknown"
        """
        if len(self.exchanges) < 3:
            return "unknown"
        
        # Define emotion valence (positive = higher score)
        emotion_scores = {
            "happy": 5, "positive": 4, "grateful": 5, "surprise": 3,
            "neutral": 2,
            "lonely": -2, "sad": -3, "negative": -2, "anxious": -2,
            "stressed": -2, "angry": -3, "fear": -3
        }
        
        recent_exchanges = list(self.exchanges)[-5:]
        scores = [emotion_scores.get(ex["emotion"].lower(), 0) for ex in recent_exchanges]
        
        if len(scores) < 3:
            return "unknown"
        
        # Compare first half vs second half
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(scores[mid:]) / (len(scores) - mid)
        
        if second_half_avg > first_half_avg + 1:
            return "improving"
        elif second_half_avg < first_half_avg - 1:
            return "declining"
        else:
            return "stable"
    
    def should_check_in(self) -> bool:
        """
        Determine if the AI should proactively check in on the user's wellbeing.
        
        Returns:
            True if a check-in would be appropriate
        """
        # Check in if:
        # 1. User has been consistently negative
        # 2. Emotion trend is declining
        # 3. It's been a while since last exchange (for established relationships)
        
        if not self.exchanges:
            return False
        
        trend = self.get_emotion_trend()
        if trend == "declining":
            return True
        
        # Check if last 3 exchanges were all negative
        recent = self.get_recent_exchanges(3)
        negative_emotions = ["lonely", "sad", "negative", "anxious", "stressed", "angry", "fear"]
        
        if len(recent) >= 3:
            all_negative = all(ex["emotion"].lower() in negative_emotions for ex in recent)
            if all_negative:
                return True
        
        return False
    
    def get_context_for_response(self) -> Dict:
        """
        Get relevant context to inform the next AI response.
        
        Returns:
            Dict with context information for response generation
        """
        summary = self.get_conversation_summary()
        trend = self.get_emotion_trend()
        recent = self.get_recent_exchanges(3)
        
        return {
            "relationship_stage": summary["relationship_stage"],
            "dominant_emotion": summary["dominant_emotion"],
            "recurring_themes": summary["recurring_themes"],
            "emotion_trend": trend,
            "recent_emotions": [ex["emotion"] for ex in recent],
            "should_check_in": self.should_check_in(),
            "total_turns": summary["total_turns"]
        }
    
    def clear(self):
        """Clear all conversation history (start fresh)."""
        self.exchanges.clear()
        self.themes.clear()
        self.start_time = datetime.now()
        self.total_exchanges = 0


# Session-based memory manager
class SessionManager:
    """
    Manages multiple conversation sessions.
    Each session has its own ConversationMemory.
    """
    
    def __init__(self):
        self.sessions = {}  # session_id -> ConversationMemory
    
    def get_or_create_session(self, session_id: str) -> ConversationMemory:
        """
        Get existing session or create a new one.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            ConversationMemory for this session
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory()
        return self.sessions[session_id]
    
    def end_session(self, session_id: str):
        """End a session and remove it from memory."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_active_sessions(self) -> List[str]:
        """Get list of all active session IDs."""
        return list(self.sessions.keys())


# Global session manager instance
_session_manager = SessionManager()


def get_session_memory(session_id: str) -> ConversationMemory:
    """
    Convenience function to get conversation memory for a session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        ConversationMemory instance for this session
    """
    return _session_manager.get_or_create_session(session_id)

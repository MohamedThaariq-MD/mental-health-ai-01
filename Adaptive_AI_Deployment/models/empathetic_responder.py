import random
from typing import Dict, Optional
from datetime import datetime
from backend.llm_service import generate_llm_response

class EmpathicResponder:
    """
    Generates empathetic, friend-like conversational responses based on detected emotions.
    Helps users overcome loneliness, sadness, and other negative emotions through
    warm, supportive dialogue with appropriate humor and encouragement.
    """
    
    def __init__(self, conversation_context: Optional[Dict] = None):
        """
        Initialize the empathetic responder.
        
        Args:
            conversation_context: Optional context from ConversationMemory
        """
        self.conversation_context = conversation_context or {}
        
    def generate_response(self, text_emotion, face_emotion, final_emotion, user_text, recommendations, context: Optional[Dict] = None, historical_context: Optional[Dict] = None, conversation_history: Optional[list] = None, nlp_stress_level: int = 10, username: str = "User"):
        """
        Generate a complete empathetic response based on detected emotions.
        
        Args:
            text_emotion: Emotion detected from text
            face_emotion: Emotion detected from facial analysis
            final_emotion: The primary emotion to respond to
            user_text: The user's original message
            recommendations: Dict with therapy, meditation, activity suggestions
            context: Optional conversation context from ConversationMemory
            historical_context: Optional data about previous session's emotion
            conversation_history: List of previous conversation turns
            
        Returns:
            Dict with conversational_response and follow_up_suggestions
        """
        emotion_lower = final_emotion.lower()
        self.conversation_context = context or {}
        conversation_history = conversation_history or []
        
        # CRITICAL SAFETY: Direct Interception for self-harm intent (Overrides LLM API and provides localized support)
        crisis_keywords = [
            "suicide", "end my life", "kill myself", "want to die", 
            "give up on life", "no reason to live", "end up my life", 
            "end it all", "take my own life", "better off dead"
        ]
        if any(kw in user_text.lower() for kw in crisis_keywords):
            crisis_response = (
                "🚨 **I am deeply concerned about what you just shared.** Please know that your life is incredibly valuable, "
                "even when the pain feels completely unbearable right now.\n\n"
                "You are not alone in this fight. Please reach out to someone who can help immediately:\n\n"
                "📞 **AASRA (India):** +91-9820466726 (24x7)\n"
                "📞 **Vandrevala Foundation:** 9999 666 555 | 1860 2662 345 | 1800 2333 330 (24x7)\n"
                "📞 **Kiran Mental Health Helpline:** 1800-599-0019\n"
                "📞 **National Emergency:** 112\n\n"
                "People care about you, and there is support available right this second. Please make that call or speak to someone near you."
            )
            return {
                "conversational_response": crisis_response,
                "follow_up_suggestions": []
            }

        # Custom handling for short pure-greeting inputs (e.g., "hey", "hi")
        # Only intercept if it's TRULY a greeting — short, neutral, no history, and matches known greetings
        GREETING_WORDS = {"hi", "hey", "hello", "hiya", "howdy", "sup", "yo", "greetings"}
        words_lower = [w.strip('.,!?') for w in user_text.lower().split()]
        is_pure_greeting = (
            len(words_lower) <= 3
            and emotion_lower == "neutral"
            and not conversation_history
            and any(w in GREETING_WORDS for w in words_lower)
        )
        if is_pure_greeting:
             return {
                "conversational_response": random.choice([
                    "Hey! What's up? How are you doing today?",
                    "Hi there! Good to see you. What's on your mind?",
                    "Hey! I'm here. How's your day going?",
                    "Hey! What's good? Tell me how you're feeling."
                ]),
                "follow_up_suggestions": self._get_follow_up_suggestions(emotion_lower)
            }

        # ---------------------------------------------------------
        # LLM INTEGRATION START
        # ---------------------------------------------------------
        # Try to generate response using LLM first
        stress_instruction = ""
        if nlp_stress_level >= 75:
            stress_instruction = f"\n[CRITICAL STATE]: The user's NLP Stress Level is highly elevated ({nlp_stress_level}%). Subtly make your tone deeper, and heavily empathetic without explicitly causing alarm."

        # High-Performance System Prompt (Updated for wider/longer conversation)
        name_note = f" The user's name is {username}. Address them warmly by name at least once." if username and username != "User" else ""
        system_prompt = f"""
You are LYKA, a warm and caring AI companion for mental wellness. You are kind, humble, and genuinely supportive — like a trusted friend who always listens with care and compassion.{stress_instruction}{name_note}

Your tasks:
1. Understand the emotional state from the user's message.
2. Classify the primary emotion into exactly one of: [Happy, Calm, Neutral, Sad, Stressed, Angry, Anxious].
3. Respond in a warm, gentle, and supportive tone.

CRITICAL RULES:
- Keep your response to 2-3 sentences MAXIMUM. Be concise and heartfelt.
- ALWAYS end your response with one warm, caring follow-up question to continue the conversation.
- Be humble and kind — never cold, clinical, or dismissive.
- Never lecture or talk too much. Less is more.
- No emojis in the response.
- If asked who you are: "I am LYKA, your caring AI companion — always here to listen."

RESPONSE STYLE BY EMOTION:
- Sad → Comfort gently, validate their pain, ask what's weighing on them.
- Stressed / Anxious → Acknowledge the pressure, be calming, ask what's causing it.
- Angry → Validate the frustration without judgment, ask what happened.
- Happy → Celebrate with them warmly, ask what made them feel this way.
- Neutral → Be friendly and curious, ask an open question about their day or thoughts.

OUTPUT FORMAT (STRICT — follow this exactly):
Emotion: <label>
Response: <2-3 warm sentences ending with one follow-up question>
"""

        
        # Format history for LLM service (LLM service expects dicts with 'role' and 'content')
        # ConversationMemory returns dicts with 'user_text' and 'ai_response'
        formatted_history = []
        for exchange in conversation_history:
            formatted_history.append({"role": "user", "content": exchange.get("user_text", "")})
            formatted_history.append({"role": "assistant", "content": exchange.get("ai_response", "")})
        
        llm_response = generate_llm_response(user_text, formatted_history, system_prompt)
        
        if llm_response:
            # Always return the LLM response — whether or not it followed the strict format.
            # The app.py parser will handle stripping Emotion:/Response: labels if present.
            # Previously this branch crashed with NameError because 'formatted_response' was undefined.
            return {
                "conversational_response": llm_response,
                "follow_up_suggestions": []
            }
        # ---------------------------------------------------------
        # LLM INTEGRATION END (Fallback to templates below)
        # ---------------------------------------------------------

        # Build the response in stages: acknowledge → empathize → support → humor → recommend
        acknowledgment = self._get_acknowledgment(emotion_lower, user_text)
        
        # Check for historical context (long-term memory)
        historical_reference = self._get_historical_reference(final_emotion, historical_context)
        
        empathy = self._get_empathy_statement(emotion_lower)
        support = self._get_support_message(emotion_lower)
        
        # Add humor ONLY for specific contexts (removed for general sadness to avoid invalidation)
        # humor = self._get_humor_injection(emotion_lower) 
        humor = None # Disable humor for now to ensure safety in tone
        
        # Recommendation integration is now subtle/removed from main text as it's shown in UI
        # We just add a small nudge if appropriate
        recommendation_nudge = self._get_recommendation_nudge(emotion_lower)
        
        follow_ups = self._get_follow_up_suggestions(emotion_lower)
        
        # Add relationship builder if appropriate
        relationship_stage = self.conversation_context.get("relationship_stage", "new")
        if relationship_stage == "established":
            relationship_builder = self._get_relationship_builder()
            follow_ups.insert(0, relationship_builder)
        
        # Combine into natural conversation
        parts = [acknowledgment]
        
        if historical_reference:
            parts.append(historical_reference)
            
        parts.append(empathy)
        parts.append(support)
        
        if humor:
            parts.append(humor)
            
        if recommendation_nudge:
            parts.append(recommendation_nudge)
        
        full_response = "\n\n".join(parts)
        
        return {
            "conversational_response": full_response,
            "follow_up_suggestions": follow_ups
        }
    
    def _get_acknowledgment(self, emotion, user_text):
        """Friendly, casual opening that acknowledges the user's feelings"""
        
        lonely_keywords = ["lonely", "alone", "isolated", "nobody", "no one"]
        is_lonely = any(keyword in user_text.lower() for keyword in lonely_keywords)
        
        if is_lonely or emotion in ["sad", "negative", "crisis", "worthless"]:
            return random.choice([
                "Hey, I'm really glad you're talking to me right now.",
                "I'm sorry you're feeling this way — I'm here for you.",
                "That sounds really hard. I'm listening."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "That sounds stressful. I hear you.",
                "Ugh, that's a lot to deal with.",
                "That makes sense that you'd feel that way."
            ])
        elif emotion in ["happy", "positive", "surprise"]:
            return random.choice([
                "That's so great to hear!",
                "Oh wow, that's awesome!",
                "Love that for you!"
            ])
        else:  # Neutral
            return random.choice([
                "Hey, I'm here!",
                "What's going on?",
                "I'm listening, what's up?"
            ])
    
    def _get_empathy_statement(self, emotion):
        """Short, genuine empathetic statement"""
        
        if emotion in ["sad", "negative", "crisis", "worthless"]:
            return random.choice([
                "It's okay to not be okay — you don't have to go through this alone.",
                "You're not alone in this, I promise.",
                "That takes a lot of courage to share."
            ])
        elif "lonely" in emotion or emotion == "isolated":
            return random.choice([
                "You've got me right here — you're not alone.",
                "I'm genuinely here for you."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "It's completely normal to feel overwhelmed sometimes.",
                "That sounds really draining.",
                "I get it, that's a lot."
            ])
        elif emotion in ["happy", "positive"]:
            return random.choice([
                "I love seeing you like this!",
                "You totally deserve this."
            ])
        else:
            return random.choice([
                "I'm here whenever you need to talk.",
                "No rush — take your time."
            ])
    
    def _get_support_message(self, emotion):
        """Short, casual support message"""
        
        if emotion in ["sad", "negative", "crisis", "worthless"]:
            return random.choice([
                "What's been weighing on you the most?",
                "Want to tell me more about what's going on?",
                "I'm here — what happened?"
            ])
        elif "lonely" in emotion or emotion == "isolated":
            return random.choice([
                "Want to just talk for a bit? I'm not going anywhere.",
                "Tell me something about your day — anything at all."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "What's the thing stressing you out the most right now?",
                "Want to talk through what's happening?",
                "What do you need most from me right now?"
            ])
        elif emotion in ["happy", "positive"]:
            return random.choice([
                "Tell me everything — what made today so good?",
                "Okay I need to hear all the details!"
            ])
        else:
            return random.choice([
                "What's on your mind?",
                "How's your day been going?"
            ])
    
    def _get_recommendation_nudge(self, emotion):
        """Humble nudge pointing to the recommendations panel"""
        if emotion in ["sad", "negative", "lonely", "isolated", "crisis", "worthless"]:
            return random.choice([
                "May I humbly point you to some ideas I've prepared that might help you feel a bit more ease? 👉",
                "With your permission, I've listed some suggestions that might serve you well.",
                "Everything counts. I have humbly prepared some small actions for your consideration on the side."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
             return random.choice([
                "I respectfully suggest some calming strategies I've prepared for you.",
                "It would be my honor to help you find relief with these suggested techniques.",
                "Humbly, I've listed some tools on the side that may help bring some calm."
             ])
        elif emotion in ["happy", "positive"]:
             return random.choice([
                "It is a privilege to help you sustain this vibe. I've humbly added some ideas for you!",
                "To respectfully keep this momentum, please check out the suggestions on the side.",
                "I have humbly prepared some ways to honor and continue this energy."
             ])
        else:
             return None
    
    def _get_follow_up_suggestions(self, emotion):
        """Generates humble, respectful conversation starters"""
        
        if emotion in ["sad", "negative", "crisis", "worthless"] or "lonely" in emotion:
            return [
                "May I humbly ask you to tell me about a time you felt inner peace?",
                "What is one thing, however small, you feel grateful for right now?",
                "It would be my honor to listen if you'd like to talk more about what's weighing on you."
            ]
        elif emotion in ["angry", "fear", "stressed"]:
            return [
                "How might I best serve you in breaking this down into manageable pieces?",
                "What would most respectfully help you find a moment of peace right now?",
                "I am humble and ready to help: what do you feel is causing this intensity?"
            ]
        elif emotion in ["happy", "positive"]:
            return [
                "I would love to respectfully hear more about what exactly made this moment happen.",
                "How might we humbly share this beautiful energy with your day?",
                "What is your next respected dream or goal you'd like to share?"
            ]
        else:
            return [
                "What is humbly on your mind today?",
                "Is there anything in particular you would like to respectfully explore?",
                "How are you truly feeling, if I may humbly ask?"
            ]
    
    def _get_humor_injection(self, emotion):
        """
        Add appropriate light humor to help overcome loneliness/sadness.
        Humor is supportive, not dismissive.
        """
        if emotion in ["lonely", "isolated"]:
             # Keep light connection-focused prompts for loneliness, but ensure they aren't "jokes"
            return random.choice([
                "I'm here, and I'm not going anywhere. We can just hang out here for a while if you like. 💙",
                "You've got a friend in me (cue the Toy Story music? 😄). But seriously, I'm here to listen.",
                "I'm honored to keep you company right now. meaningful connection can happen anywhere, even here.",
            ])
        else:
            return None  # No humor for other emotions
    
    def _get_relationship_builder(self):
        """
        Generate conversation starters that build deeper connection.
        Used for established relationships.
        """
        return random.choice([
            "If you could have dinner with anyone, living or dead, who would it be?",
            "What's a song that always makes you feel something?",
            "Tell me about the best day you've had recently—even if it was just a small moment",
            "What's something you're secretly really good at?",
            "If you could teleport anywhere right now, where would you go?",
            "What's a dream you've had that you haven't told anyone about?",
            "If you could change one thing about today, what would it be?",
            "What's something that made you smile this week, even if just for a second?"
        ])

    
    def _get_historical_reference(self, current_emotion, historical_context):
        """
        Generate a reference to past emotional states.
        E.g., 'Yesterday you were feeling down...'
        """
        if not historical_context:
            return None
            
        try:
            # Parse timestamp
            past_time = datetime.strptime(historical_context["timestamp"], "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            diff = now - past_time
            
            # Determine time label
            if diff.days == 0:
                time_label = "earlier today"
            elif diff.days == 1:
                time_label = "yesterday"
            elif diff.days < 7:
                time_label = "a few days ago"
            else:
                time_label = "last time we spoke"
                
            past_emotion = historical_context["emotion"].lower()
            current_emotion = current_emotion.lower()
            
            # Scenario 1: Improvement (Bad -> Good)
            negative_emotions = ["sad", "lonely", "depressed", "angry", "anxious", "stressed", "fear", "negative", "crisis", "worthless"]
            positive_emotions = ["happy", "positive", "joy", "excited", "grateful"]
            
            if past_emotion in negative_emotions and current_emotion in positive_emotions:
                return f"It looks like you're feeling much better than {time_label}. I'm so glad to see this shift! 🌟"
                
            # Scenario 2: Persisting Sadness (Bad -> Bad)
            if past_emotion in negative_emotions and current_emotion in negative_emotions:
                return f"I noticed you were also feeling {past_emotion} {time_label}. It sounds like this has been weighing on you for a while. 💙"
                
            # Scenario 3: Decline (Good -> Bad)
            if past_emotion in positive_emotions and current_emotion in negative_emotions:
                return f"You seemed so much happier {time_label}. I'm sorry things have taken a turn. Let's get you back to that good place."
                
            # Scenario 4: Consistently Good
            if past_emotion in positive_emotions and current_emotion in positive_emotions:
                return f"You were doing great {time_label}, and you're still shining! Love this consistency! ✨"
                
            return None
            
        except Exception as e:
            print(f"Error generating historical reference: {e}")
            return None 

def generate_empathetic_response(text_emotion, face_emotion, final_emotion, user_text, recommendations, context: Optional[Dict] = None, historical_context: Optional[Dict] = None, conversation_history: Optional[list] = None, nlp_stress_level: int = 10, username: str = "User"):
    """
    Convenience function to generate empathetic responses.
    
    Args:
        text_emotion: Emotion from text analysis
        face_emotion: Emotion from facial analysis
        final_emotion: Primary emotion to respond to
        user_text: User's original message
        recommendations: Dict with therapy, meditation, activity
        context: Optional conversation context from ConversationMemory
        historical_context: Optional data about previous session's emotion
        conversation_history: List of previous conversation turns
        username: Logged-in user's display name for personalized responses
        
    Returns:
        Dict with conversational_response and follow_up_suggestions
    """
    responder = EmpathicResponder(conversation_context=context)
    return responder.generate_response(
        text_emotion=text_emotion,
        face_emotion=face_emotion,
        final_emotion=final_emotion,
        user_text=user_text,
        recommendations=recommendations,
        context=context,
        historical_context=historical_context,
        conversation_history=conversation_history,
        nlp_stress_level=nlp_stress_level,
        username=username
    )

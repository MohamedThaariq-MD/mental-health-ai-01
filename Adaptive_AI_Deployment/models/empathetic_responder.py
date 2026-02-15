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
        
    def generate_response(self, text_emotion, face_emotion, final_emotion, user_text, recommendations, context: Optional[Dict] = None, historical_context: Optional[Dict] = None, conversation_history: Optional[list] = None):
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
        
        # Custom handling for short inputs (e.g., "hey", "hi")
        if len(user_text.split()) <= 3 and emotion_lower == "neutral" and not conversation_history:
             return {
                "conversational_response": random.choice([
                    "Hey there! 👋 I'm all ears. What's going on in your world?",
                    "Hi! It's good to see you. How are you feeling right now?",
                    "Hello! I'm here for you. What's on your mind?"
                ]),
                "follow_up_suggestions": self._get_follow_up_suggestions(emotion_lower)
            }

        # ---------------------------------------------------------
        # LLM INTEGRATION START
        # ---------------------------------------------------------
        # Try to generate response using LLM first
        system_prompt = f"""
        You are a warm, empathetic, and supportive friend (not a therapist or a robot).
        Your name is "Adaptive AI".
        
        GOAL: Help the user feel heard and supported. Engage in a natural, flowing conversation.
        
        CURRENT STATE:
        - User Emotion: {final_emotion}
        - User Input: "{user_text}"
        
        GUIDELINES:
        1. **BE NATURAL**: Talk like a real friend. Use casual language. Avoid stiff phrases like "I understand that you are feeling...".
        2. **ALWAYS ASK A FOLLOW-UP QUESTION**: To keep the conversation going, almost ALWAYS end your response with a relevant, open-ended question based on what the user just said or a related topic.
        3. **USE CONTEXT**: Look at the conversation history. If the user just answered a question, follow up naturally. Don't repeat yourself.
        4. **BE BRIEF**: Keep responses to 1-3 sentences maximum.
        5. **NO UNSOLICITED ADVICE**: Don't give advice unless asked. Focus on listening and validation.
        6. **AVOID REPETITION**: Do not start sentences with "I hear you", "It sounds like", or "I understand". Vary your language.
        7. **SAFETY**: If the user mentions self-harm or severe distress, gently suggest professional help, but remain supportive.
        8. **STAY ON TOPIC**: Respond directly to what the user just said.
        """
        
        # Format history for LLM service (LLM service expects dicts with 'role' and 'content')
        # ConversationMemory returns dicts with 'user_text' and 'ai_response'
        formatted_history = []
        for exchange in conversation_history:
            formatted_history.append({"role": "user", "content": exchange.get("user_text", "")})
            formatted_history.append({"role": "assistant", "content": exchange.get("ai_response", "")})
        
        llm_response = generate_llm_response(user_text, formatted_history, system_prompt)
        
        if llm_response:
            return {
                "conversational_response": llm_response,
                "follow_up_suggestions": [] # LLM responses don't need hardcoded suggestions
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
        """Warm opening that acknowledges the user's feelings"""
        
        lonely_keywords = ["lonely", "alone", "isolated", "nobody", "no one"]
        is_lonely = any(keyword in user_text.lower() for keyword in lonely_keywords)
        
        if is_lonely or emotion in ["sad", "negative"]:
            return random.choice([
                "Hey, I hear you. 💙 It sounds like you're going through a tough time right now.",
                "I'm really glad you shared that with me. 🤗 What you're feeling is completely valid.",
                "Thank you for opening up. I can sense that things feel heavy for you right now.",
                "I'm here with you. 💜 It takes courage to express how you're really feeling.",
                "I appreciate you trusting me with this. Let's work through this together."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "I can feel the intensity in your words. 💪 Let's take a breath together.",
                "That sounds really frustrating. I'm here to help you navigate this.",
                "Wow, that's a lot to carry. Let's unpack this and find some relief.",
                "I hear the stress in what you're saying. You're not alone in this."
            ])
        elif emotion in ["happy", "positive", "surprise"]:
            return random.choice([
                "That's wonderful! 🌟 I can feel the positive energy in your words!",
                "Yes! I love hearing this! 🎉 Your happiness is contagious!",
                "This is amazing! ✨ Tell me more about what's making you feel so good!",
                "I'm so happy for you! 😊 This is exactly the kind of energy we need!"
            ])
        else:  # Neutral
            return random.choice([
                "Thanks for sharing. I'm here to listen and support you. 🌸",
                "I'm glad you're here. Let's explore what's on your mind together.",
                "Hey there! 👋 I'm all ears. What's going on in your world?"
            ])
    
    def _get_empathy_statement(self, emotion):
        """Empathetic statement that validates feelings"""
        
        if emotion in ["sad", "negative"]:
            return random.choice([
                "Feeling down is part of being human, and it's okay to not be okay sometimes. You're not alone in this—I'm right here with you.",
                "Sadness can feel overwhelming, but remember: this feeling is temporary, and you have the strength to move through it.",
                "I know it might not feel like it right now, but brighter days are ahead. Let's take small steps together.",
                "Your feelings are valid, and it's important to honor them. But let's also remember that you deserve joy and peace."
            ])
        elif "lonely" in emotion or emotion == "isolated":
            return random.choice([
                "Loneliness can be one of the hardest feelings to sit with. But here's the thing: you're never truly alone. I'm here, and there are people who care about you.",
                "I get it—feeling lonely is tough. But you know what? Even in this moment, we're connected. And that's a start. 💙",
                "Loneliness is like a cloud that passes through. It feels heavy now, but it won't last forever. Let's find ways to bring some light in.",
                "You're reaching out, and that's already a brave step. Connection starts with moments like this."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "These intense emotions are your mind's way of protecting you. Let's channel this energy into something constructive.",
                "It's completely normal to feel this way when things get overwhelming. You're handling more than you think.",
                "Strong emotions like this show how much you care. Let's use that passion to find solutions."
            ])
        elif emotion in ["happy", "positive"]:
            return random.choice([
                "This is beautiful! Positive emotions are like fuel for your soul—let's keep this momentum going!",
                "Your joy is a gift, not just to yourself but to everyone around you. Soak it in!",
                "Happiness looks good on you! Let's make sure we nurture this feeling."
            ])
        else:
            return random.choice([
                "Sometimes a calm, neutral space is exactly what we need to reflect and recharge.",
                "There's wisdom in stillness. Let's use this moment to check in with yourself."
            ])
    
    def _get_support_message(self, emotion):
        """Supportive message with light humor or encouragement"""
        
        if emotion in ["sad", "negative"]:
            return random.choice([
                "It takes strength to face these feelings, and I admire that you're doing it. 💙 Let's take this one moment at a time. Is there something small we can do to make you feel a little more comfortable right now?",
                "Please be gentle with yourself today. You're navigating something difficult, and it's okay to rest and recharge. I'm here to support you in whatever way you need.",
                "Sometimes the bravest thing we can do is just breathe through the difficult moments. I'm right here with you. What's one thing that usually brings you a sense of peace?",
                "Your well-being matters to me. Let's focus on getting through this moment together. You don't have to figure it all out right now."
            ])
        elif "lonely" in emotion or emotion == "isolated":
            return random.choice([
                "Fun fact: Did you know that talking to yourself counts as socializing? (Okay, maybe not officially, but I say it counts! 😄) But seriously, let's find ways to connect—whether it's reaching out to an old friend, joining an online community, or even just chatting with me more.",
                "Loneliness is like being the only person at a party... but here's the good news: the party isn't over, and more guests are on the way. 🎉 Let's think about who you could reach out to, or what activities might help you feel more connected.",
                "You know what's wild? Sometimes the best cure for loneliness is doing something kind for someone else. It's like a cheat code for connection. 💡 What if we brainstormed a small act of kindness you could do today?",
                "Okay, real talk: Loneliness is tough, but you're tougher. And right now, in this moment, you're not alone—I'm here, and I'm not going anywhere. Let's figure out how to bring more connection into your life."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
            return random.choice([
                "When stress hits, our brains go into 'fight or flight' mode. But here's the hack: we can trick it into 'rest and digest' mode with some simple techniques. Let's try one together!",
                "Anger is just passion that needs direction. Let's channel this into something productive—you've got the energy, now let's use it wisely! 💪",
                "Fear is often just excitement in disguise. What if we reframe this as your body preparing you for something important?"
            ])
        elif emotion in ["happy", "positive"]:
            return random.choice([
                "This is the energy we love to see! 🎊 Let's bottle this feeling up and save it for the days when we need a reminder of how good life can be.",
                "You're radiating good vibes right now! Keep this going—happiness is contagious, and the world needs more of what you're bringing! ✨",
                "Celebrate this moment! You deserve all the good things coming your way. Let's make sure you're doing things to sustain this joy."
            ])
        else:
            return random.choice([
                "A calm mind is a powerful mind. Let's use this peaceful moment to set some intentions or just enjoy the stillness.",
                "Sometimes the best thing we can do is simply be present. You're doing great just by being here."
            ])
    
    def _get_recommendation_nudge(self, emotion):
        """Simple nudge pointing to the recommendations panel"""
        if emotion in ["sad", "negative", "lonely", "isolated"]:
            return random.choice([
                "I've popped some ideas for things that might help on the side. 👉",
                "Check out the suggestions I've prepared for you.",
                "Small steps matter. I've listed a few ideas for you."
            ])
        elif emotion in ["angry", "fear", "stressed"]:
             return random.choice([
                "I've listed some calming strategies for you to try.",
                "Take a look at the techniques I've suggested.",
                "There are some tools on the side that might help cool things down."
             ])
        elif emotion in ["happy", "positive"]:
             return random.choice([
                "I've added some ways to keep this vibe going!",
                "Check out the activity ideas to sustain this energy.",
                "Let's keep this momentum! suggestions are on the side."
             ])
        else:
             return None
    
    def _get_follow_up_suggestions(self, emotion):
        """Generate conversation starters for continued engagement"""
        
        if emotion in ["sad", "negative"] or "lonely" in emotion:
            return [
                "Tell me about a time when you felt truly happy",
                "What's one thing you're grateful for today?",
                "Is there someone you've been meaning to reach out to?"
            ]
        elif emotion in ["angry", "fear", "stressed"]:
            return [
                "What's the main thing stressing you out right now?",
                "How can I help you break this down into smaller pieces?",
                "What would make you feel better in this moment?"
            ]
        elif emotion in ["happy", "positive"]:
            return [
                "What made today so great?",
                "How can you share this joy with others?",
                "What's your next goal or dream?"
            ]
        else:
            return [
                "What's on your mind today?",
                "Is there anything you'd like to explore or talk about?",
                "How are you really feeling?"
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
            negative_emotions = ["sad", "lonely", "depressed", "angry", "anxious", "stressed", "fear", "negative"]
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

def generate_empathetic_response(text_emotion, face_emotion, final_emotion, user_text, recommendations, context: Optional[Dict] = None, historical_context: Optional[Dict] = None, conversation_history: Optional[list] = None):
    """
    Convenience function to generate empathetic responses.
    
    Args:
        text_emotion: Emotion from text analysis
        face_emotion: Emotion from facial analysis
        final_emotion: Primary emotion to respond to
        user_text: User's original message
        recommendations: Dict with therapy, meditation, activity
    user_text: User's original message
        recommendations: Dict with therapy, meditation, activity
        context: Optional conversation context from ConversationMemory
        historical_context: Optional data about previous session's emotion
        conversation_history: List of previous conversation turns
        
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
        conversation_history=conversation_history
    )

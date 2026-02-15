import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.empathetic_responder import generate_empathetic_response
from models.conversation_context import ConversationMemory

def test_chat_flow():
    print("Initializing test chat flow...")
    
    # Simulate a session
    memory = ConversationMemory()
    
    # Turn 1: User is sad
    user_input_1 = "I feel really lonely today."
    print(f"\nUser: {user_input_1}")
    
    # Generate response
    # currrently app.py passes 'context' but NOT raw history. 
    # We will simulate what app.py DOES pass currently.
    context = memory.get_context_for_response()
    
    response_1 = generate_empathetic_response(
        text_emotion="Sad",
        face_emotion="Neutral",
        final_emotion="Sad",
        user_text=user_input_1,
        recommendations={"therapy": "Talk to a friend"},
        context=context
    )
    
    ai_msg_1 = response_1["conversational_response"]
    print(f"AI: {ai_msg_1}")
    
    # Add to memory
    memory.add_exchange(user_input_1, ai_msg_1, "Sad")
    
    # Turn 2: User follows up (dependent on context)
    user_input_2 = "I don't have anyone to talk to though."
    print(f"\nUser: {user_input_2}")
    
    # Get context and history (Simulating app.py)
    context = memory.get_context_for_response()
    recent_history = memory.get_recent_exchanges(10)
    
    response_2 = generate_empathetic_response(
        text_emotion="Sad",
        face_emotion="Neutral",
        final_emotion="Sad", # Still sad
        user_text=user_input_2,
        recommendations={"therapy": "Join a club"},
        context=context,
        conversation_history=recent_history # Now passing history!
    )
    
    ai_msg_2 = response_2["conversational_response"]
    print(f"AI: {ai_msg_2}")
    
    print("\nTest Complete.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_chat_flow()

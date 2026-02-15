import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.llm_service import generate_llm_response, _call_groq

def test_groq_integration():
    load_dotenv()
    
    api_key = os.environ.get("GROQ_API_KEY")
    print(f"Groq API Key present: {bool(api_key)}")
    
    if not api_key:
        print("Note: No GROQ_API_KEY found in .env. Please add it to test Groq integration.")
        print("You can get a free key at: https://console.groq.com/keys")
    
    print("\nTesting generate_llm_response (expecting Groq)...")
    response = generate_llm_response(
        user_text="Hello, are you there?", 
        conversation_history=[],
        system_prompt="You are a helpful assistant."
    )
    
    if response:
        print("\nVerification Successful! Response received:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    else:
        print("\nVerification Failed. No response received.")

if __name__ == "__main__":
    test_groq_integration()

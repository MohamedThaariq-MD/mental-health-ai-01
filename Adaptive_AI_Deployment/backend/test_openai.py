import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.llm_service import generate_llm_response, _call_openai

def test_openai_integration():
    load_dotenv()
    
    api_key = os.environ.get("OPENAI_API_KEY")
    print(f"OpenAI API Key present: {bool(api_key)}")
    
    if not api_key:
        print("Note: No OPENAI_API_KEY found in .env. Please add it to test OpenAI integration.")
        print("Falling back to other providers if available...")
    
    print("\nTesting generate_llm_response...")
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
        print("\nVerification Failed. No response received from any provider.")

if __name__ == "__main__":
    test_openai_integration()

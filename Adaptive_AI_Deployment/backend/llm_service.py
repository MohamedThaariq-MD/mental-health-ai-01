import os
import requests
import json
import traceback
from openai import OpenAI
from backend.database import get_user_facts, save_user_fact

def generate_llm_response(user_text, conversation_history, system_prompt=None, user_id="default_user"):
    """
    Generate a response using an LLM (Groq, OpenAI, or Gemini) if available.
    Returns None if no API key is configured or if the request fails.
    """
    
    # --- LONG TERM MEMORY INJECTION ---
    # Fetch known facts about the user
    user_facts = get_user_facts(user_id)
    if user_facts:
        facts_str = "\n".join([f"- {f['content']}" for f in user_facts])
        memory_context = f"\n\nLONG-TERM MEMORY (Things you know about the user):\n{facts_str}\n"
        if system_prompt:
            system_prompt += memory_context
        else:
            system_prompt = memory_context

    # --- FACT EXTRACTION (SIDE EFFECT) ---
    # We attempt to learn new things from this input
    try:
        extract_and_save_facts(user_text, user_id)
    except Exception as e:
        print(f"Fact extraction failed: {e}")
    
    # Priority 1: Groq (Free / Open Source Models like Llama 3) - RECOMMENDED
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        return _call_groq(groq_api_key, user_text, conversation_history, system_prompt)

    # Priority 2: OpenAI (Paid)
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        return _call_openai(openai_api_key, user_text, conversation_history, system_prompt)
        
    # Priority 3: Google Gemini (Free Tier available)
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if gemini_api_key:
        return _call_gemini(gemini_api_key, user_text, conversation_history, system_prompt)

    # No keys found
    return None

def extract_and_save_facts(user_text, user_id):
    """
    Analyze user text for permanent facts (Name, Location, Hobbies, etc.)
    and save them to the database.
    """
    # Simple Heuristics for speed/cost (can be replaced with LLM call)
    user_text_lower = user_text.lower()
    
    fact_prefixes = [
        "my name is ", "i am called ", "call me ",
        "i live in ", "i'm from ",
        "i love ", "i hate ", "i like ", "my favorite ",
        "i work as ", "i am a "
    ]
    
    for prefix in fact_prefixes:
        if prefix in user_text_lower:
            # Simple extraction: Save the whole sentence as a fact for now
            # In a production system, we'd use an LLM to clean this up
            # e.g., "My name is John" -> "Name: John"
            
            # Using a mini-LLM call for extraction if Groq is available is better
            groq_key = os.environ.get("GROQ_API_KEY")
            if groq_key:
                _llm_extract_fact(groq_key, user_text, user_id)
            else:
                # Fallback: Save raw sentence if it's short
                if len(user_text) < 100:
                    save_user_fact(user_text, "heuristic", user_id)
            break

def _llm_extract_fact(api_key, text, user_id):
    """Use Llama 3 via Groq to exact precise facts."""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        system = "You are a fact extractor. If the user mentions a personal fact (name, hobby, job, location), extract it as a concise statement. If not, return 'None'."
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            "temperature": 0.1,
            "max_tokens": 50
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            fact = response.json()["choices"][0]["message"]["content"].strip()
            if fact and "None" not in fact:
                print(f"[MEMORY] Learned new fact: {fact}")
                save_user_fact(fact, "learned", user_id)
    except:
        pass

def _call_openai(api_key, user_text, history, system_prompt):
    try:
        client = OpenAI(api_key=api_key)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        # Add recent history (limited to last 20 turns to save context)
        for msg in history[-20:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
            
        messages.append({"role": "user", "content": user_text})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # or "gpt-4o" if available/preferred
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
            
    except Exception as e:
        print(f"LLM Service Error (OpenAI): {e}")
        traceback.print_exc()
        return None

def _call_groq(api_key, user_text, history, system_prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        # Add recent history (limited to last 20 turns to save context)
        for msg in history[-20:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
            
        messages.append({"role": "user", "content": user_text})
        
        payload = {
            "model": "llama-3.3-70b-versatile", # Updated to supported model
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Groq API Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"LLM Service Error (Groq): {e}")
        traceback.print_exc()
        return None

def _call_gemini(api_key, user_text, history, system_prompt):
    # Valid but basic implementation for Gemini REST API
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Gemini specific formatting
        contents = []
        
        if system_prompt:
             contents.append({"role": "user", "parts": [{"text": system_prompt}]})
             contents.append({"role": "model", "parts": [{"text": "Understood. I will act as the supportive empathetic friend."}]})

        for msg in history[-20:]:
             role = "user" if msg["role"] == "user" else "model"
             contents.append({"role": role, "parts": [{"text": msg["content"]}]})
             
        contents.append({"role": "user", "parts": [{"text": user_text}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 300
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"Gemini API Error: {response.text}")
            return None

    except Exception as e:
        print(f"LLM Service Error (Gemini): {e}")
        return None

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Groq's Whisper API.
    """
    try:
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            print("Groq API Key missing for transcription")
            return None
            
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {groq_api_key}"
        }
        
        # Open the audio file
        with open(audio_file_path, "rb") as file:
            files = {
                "file": (os.path.basename(audio_file_path), file, "audio/wav"), # Adjust mime if needed
                "model": (None, "distil-whisper-large-v3-en") # or "whisper-large-v3"
            }
            
            response = requests.post(url, headers=headers, files=files)
            
        if response.status_code == 200:
            return response.json().get("text")
        else:
            print(f"Groq Transcription Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Transcription Error: {e}")
        return None

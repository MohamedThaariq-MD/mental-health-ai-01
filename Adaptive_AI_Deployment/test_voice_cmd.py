import os
from dotenv import load_dotenv
load_dotenv()
from backend.llm_service import transcribe_audio

# Let's see what happens with text_voice
try:
    print(transcribe_audio('test.wav'))
except Exception as e:
    print(e)

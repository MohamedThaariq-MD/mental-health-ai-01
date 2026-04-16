import requests
import json

payload = {
    "text": "I feel so stressed today and I don't know what to do.",
    "use_camera": False
}

try:
    response = requests.post("http://127.0.0.1:5000/analyze", json=payload)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Request failed:", e)

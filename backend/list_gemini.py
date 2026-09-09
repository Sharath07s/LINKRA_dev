import os
import sys
import requests
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.config import settings

def list_gemini():
    print("--- Gemini Models ---")
    if not settings.GEMINI_API_KEY: return
    r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.GEMINI_API_KEY}")
    if r.status_code == 200:
        data = r.json()
        for m in data.get("models", []):
            print(f"- {m['name']}")
    else:
        print("Failed to list Gemini models:", r.status_code, r.text)

list_gemini()

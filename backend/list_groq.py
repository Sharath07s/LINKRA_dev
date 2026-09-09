import os
import sys
import requests
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.config import settings

def list_groq():
    print("--- Groq Models ---")
    if not settings.GROQ_API_KEY: return
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
    r = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
    if r.status_code == 200:
        data = r.json()
        for m in data.get("data", []):
            print(f"- {m['id']}")
    else:
        print("Failed to list Groq models:", r.status_code, r.text)

list_groq()

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.core.config import settings
from app.ai.provider import get_ai_provider

def diagnose():
    print("--- Environment Variables ---")
    keys_to_check = [
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
        "DEEPSEEK_API_KEY",
        "GROQ_API_KEY"
    ]
    for key in keys_to_check:
        val = getattr(settings, key, None)
        status = "CONFIGURED (length: {})".format(len(val)) if val else "NOT CONFIGURED"
        print(f"{key}: {status}")

    print("\n--- Testing Providers ---")
    
    # Test OpenAI
    if settings.OPENAI_API_KEY:
        try:
            provider = get_ai_provider("openai", openai_api_key=settings.OPENAI_API_KEY)
            resp = provider.generate_response("Say 'OK'")
            print(f"OpenAI: PASS (Response: {resp})")
        except Exception as e:
            print(f"OpenAI: FAIL ({type(e).__name__}: {str(e)})")
    else:
        print("OpenAI: NOT CONFIGURED")
        
    # Test Gemini
    if settings.GEMINI_API_KEY:
        try:
            provider = get_ai_provider("gemini", gemini_api_key=settings.GEMINI_API_KEY)
            resp = provider.generate_response("Say 'OK'")
            print(f"Gemini: PASS (Response: {resp})")
        except Exception as e:
            print(f"Gemini: FAIL ({type(e).__name__}: {str(e)})")
    else:
        print("Gemini: NOT CONFIGURED")
        
    # Test Groq
    if settings.GROQ_API_KEY:
        try:
            provider = get_ai_provider("groq", groq_api_key=settings.GROQ_API_KEY)
            resp = provider.generate_response("Say 'OK'")
            print(f"Groq: PASS (Response: {resp})")
        except Exception as e:
            print(f"Groq: FAIL ({type(e).__name__}: {str(e)})")
    else:
        print("Groq: NOT CONFIGURED")
        
    # Test DeepSeek
    if settings.DEEPSEEK_API_KEY:
        try:
            provider = get_ai_provider("deepseek", deepseek_api_key=settings.DEEPSEEK_API_KEY)
            resp = provider.generate_response("Say 'OK'")
            print(f"DeepSeek: PASS (Response: {resp})")
        except Exception as e:
            print(f"DeepSeek: FAIL ({type(e).__name__}: {str(e)})")
    else:
        print("DeepSeek: NOT CONFIGURED")

if __name__ == "__main__":
    diagnose()

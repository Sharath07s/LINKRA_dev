import os
import sys
import logging
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from langchain_groq import ChatGroq
from app.core.config import settings

logging.basicConfig(level=logging.DEBUG)

class TestSchema(BaseModel):
    name: str = Field(description="The name of the person")
    age: int = Field(description="The age of the person")

def test_groq():
    models_to_test = ["llama3-groq-70b-8192-tool-use-preview", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it", "qwen-2.5-32b"]
    
    for model_name in models_to_test:
        print(f"\nTesting model: {model_name}")
        try:
            llm = ChatGroq(model=model_name, api_key=settings.GROQ_API_KEY, temperature=0.0)
            structured_llm = llm.with_structured_output(TestSchema)
            res = structured_llm.invoke("John is 35 years old.")
            print(f"SUCCESS: {res}")
            return  # If one succeeds, we know which one to use!
        except Exception as e:
            print(f"FAILED: {e}")

if __name__ == "__main__":
    test_groq()

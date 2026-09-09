import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Abstract base class for all AI providers."""
    
    @abstractmethod
    def get_chat_model(self, temperature: float = 0.0) -> BaseChatModel:
        """Return the initialized LangChain Chat Model."""
        pass
        
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a direct text response."""
        pass

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider")
        self.api_key = api_key

    def get_chat_model(self, temperature: float = 0.0) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(api_key=self.api_key, temperature=temperature, model="gpt-4o")

    def generate_response(self, prompt: str, **kwargs) -> str:
        model = self.get_chat_model()
        response = model.invoke(prompt)
        return response.content

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiProvider")
        self.api_key = api_key

    def get_chat_model(self, temperature: float = 0.0) -> BaseChatModel:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(google_api_key=self.api_key, temperature=temperature, model="gemini-3.6-flash")

    def generate_response(self, prompt: str, **kwargs) -> str:
        model = self.get_chat_model()
        response = model.invoke(prompt)
        return response.content

class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for ClaudeProvider")
        self.api_key = api_key

    def get_chat_model(self, temperature: float = 0.0) -> BaseChatModel:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(anthropic_api_key=self.api_key, temperature=temperature, model="claude-3-opus-20240229")

    def generate_response(self, prompt: str, **kwargs) -> str:
        model = self.get_chat_model()
        response = model.invoke(prompt)
        return response.content

class DeepSeekProvider(AIProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is required for DeepSeekProvider")
        self.api_key = api_key

    def get_chat_model(self, temperature: float = 0.0) -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key, 
            base_url="https://api.deepseek.com/v1", 
            temperature=temperature, 
            model="deepseek-chat"
        )

    def generate_response(self, prompt: str, **kwargs) -> str:
        model = self.get_chat_model()
        response = model.invoke(prompt)
        return response.content

class GroqProvider(AIProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GROQ_API_KEY is required for GroqProvider")
        self.api_key = api_key

    def get_chat_model(self, temperature: float = 0.0) -> BaseChatModel:
        from langchain_groq import ChatGroq
        return ChatGroq(groq_api_key=self.api_key, temperature=temperature, model="qwen/qwen3.6-27b")

    def generate_response(self, prompt: str, **kwargs) -> str:
        model = self.get_chat_model()
        response = model.invoke(prompt)
        return response.content

def get_ai_provider(provider_name: str, **kwargs) -> AIProvider:
    """Factory method to get the configured AI provider."""
    provider_name = provider_name.lower()
    
    if provider_name == "openai":
        return OpenAIProvider(api_key=kwargs.get("openai_api_key"))
    elif provider_name == "gemini":
        return GeminiProvider(api_key=kwargs.get("gemini_api_key"))
    elif provider_name == "claude":
        return ClaudeProvider(api_key=kwargs.get("anthropic_api_key"))
    elif provider_name == "deepseek":
        return DeepSeekProvider(api_key=kwargs.get("deepseek_api_key"))
    elif provider_name == "groq":
        return GroqProvider(api_key=kwargs.get("groq_api_key"))
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")

class FallbackManager:
    """Manages fallback execution across multiple providers."""
    
    @staticmethod
    def execute_with_fallback(
        prompt: Any, 
        structured_schema: Optional[Type] = None, 
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Executes a prompt (or list of messages) with fallback logic.
        Returns {"result": Any, "provider": str}
        """
        from app.core.config import settings
        
        # Priority: Groq -> Gemini -> OpenAI -> DeepSeek
        fallback_sequence = ["groq", "gemini", "openai", "deepseek"]
        
        last_error = None
        
        for provider_name in fallback_sequence:
            try:
                if provider_name == "groq" and not settings.GROQ_API_KEY: continue
                if provider_name == "gemini" and not settings.GEMINI_API_KEY: continue
                if provider_name == "openai" and not settings.OPENAI_API_KEY: continue
                if provider_name == "deepseek" and not settings.DEEPSEEK_API_KEY: continue
                
                provider = get_ai_provider(
                    provider_name,
                    groq_api_key=settings.GROQ_API_KEY,
                    gemini_api_key=settings.GEMINI_API_KEY,
                    openai_api_key=settings.OPENAI_API_KEY,
                    deepseek_api_key=settings.DEEPSEEK_API_KEY
                )
                
                model = provider.get_chat_model(temperature=temperature)
                
                if structured_schema:
                    structured_model = model.with_structured_output(structured_schema)
                    result = structured_model.invoke(prompt)
                else:
                    result = model.invoke(prompt)
                    content = result.content
                    if isinstance(content, list):
                        text_parts = []
                        for part in content:
                            if isinstance(part, dict) and "text" in part:
                                text_parts.append(part["text"])
                            elif isinstance(part, str):
                                text_parts.append(part)
                        result = "".join(text_parts)
                    else:
                        result = str(content)
                    
                return {"result": result, "provider": provider_name}
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
                last_error = e
                continue
                
        raise RuntimeError(f"All AI providers failed. Last error: {last_error}")

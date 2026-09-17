from typing import Optional, List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json

import os
from pathlib import Path

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
_ENV_PATH = _ROOT_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=(str(_ENV_PATH), ".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    PROJECT_NAME: str = "KCIA"
    APP_NAME: str = "KCIA"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = []
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "kcia"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""
        
    # Security
    SECRET_KEY: str  # Required, no insecure default
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Providers
    AI_PROVIDER: str = "gemini"
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.6-flash"
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Entity Resolution Settings
    RESOLUTION_WEIGHT_NAME: float = 0.50
    RESOLUTION_WEIGHT_PHONE: float = 0.30
    RESOLUTION_WEIGHT_VEHICLE: float = 0.15
    RESOLUTION_WEIGHT_LOCATION: float = 0.05
    RESOLUTION_THRESHOLD_AUTO_MATCH: float = 0.80
    RESOLUTION_THRESHOLD_REVIEW: float = 0.65
    RESOLUTION_TEMPORAL_PENALTY: float = 0.10

settings = Settings()


"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://devdocs:devdocs@localhost:5432/devdocs"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # AI Settings
    DEFAULT_MODEL: str = "claude-sonnet-4-5"
    FALLBACK_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    
    # Context Management
    MAX_CONVERSATION_LENGTH: int = 50  # messages
    SUMMARIZATION_THRESHOLD: int = 20  # messages before summarizing
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


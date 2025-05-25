"""Configuration management for the Bot Service."""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str
    database_url: str
    
    # LLM Configuration
    openai_api_key: str
    llm_model: str = "gpt-3.5-turbo"
    huggingfacehub_api_token: str
    huggingfacehub_model: str

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    # Application
    app_name: str = "Telegram Expense Bot Service"
    version: str = "1.0.0"
    dev: bool = True
    expense_categories: List[str]
    
    class Config:
        case_sensitive = False


# Global settings instance
settings = Settings() # type: ignore

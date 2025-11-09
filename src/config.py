"""
Configuration management for the application.
Loads settings from environment variables and .env files.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Defines the application settings, loaded from environment variables or .env file.
    """
    # --- General Settings ---
    APP_ENV: str = "DEV" # "DEV" or "DEMO"

    # --- LLM Provider Configuration ---
    # Default to Ollama DEV settings
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_API_KEY: str = "ollama" # Placeholder for OpenAI client, actual key for OpenRouter

    # Model names
    LLM_EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_FAST_MODEL: str = "mistral:7b"
    LLM_THINKING_MODEL: str = "deepseek-r1:8b"

    # --- Observability Settings (LangSmith) ---
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "MediScout-Dev"

    # --- ChromaDB Settings ---
    CHROMA_PERSIST_DIR: str = "data/chromadb"
    CHROMA_COLLECTION_NAME: str = "mediscout_kb"

    # --- External APIs ---
    # PUBMED_API_KEY: Optional[str] = None # Example for future external APIs

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

# Instantiate settings
settings = Settings()

# Optional: Print loaded settings for debugging (can be removed in production)
print("Loaded Settings:")
for field, value in settings.model_dump().items():
    if 'KEY' not in field:
        print(f"  {field}: {value}")
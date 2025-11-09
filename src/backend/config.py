"""
Configuration loader for backend services.
Reads environment variables for model selection, API keys, and observability.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    APP_ENV = os.getenv("APP_ENV", "DEV")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL")
    LLM_FAST_MODEL = os.getenv("LLM_FAST_MODEL")
    LLM_THINKING_MODEL = os.getenv("LLM_THINKING_MODEL")
    BASE_URL = os.getenv("BASE_URL")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

settings = Settings()

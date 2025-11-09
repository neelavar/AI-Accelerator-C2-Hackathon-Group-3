# src/config.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# --- General Settings ---
# APP_ENV is still useful for parts of the app that might have other environment-specific logic.
APP_ENV = os.getenv("APP_ENV", "DEV") 

# --- LLM Client Configuration ---
class LLMClient:
    def __init__(self):
        self.client = None
        self.embedding_model = ""
        self.fast_model = ""
        self.thinking_model = ""
        self._configure_client()

    def _configure_client(self):
        # Configuration is now driven entirely by environment variables
        base_url = os.getenv("LLM_BASE_URL")
        api_key = os.getenv("LLM_API_KEY")

        if not base_url or not api_key:
            raise ValueError("LLM configuration environment variables (LLM_BASE_URL, LLM_API_KEY) are not set. Please create a .env file based on .env.example.")

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        # Fetch model names from environment, with sensible defaults for local dev
        self.embedding_model = os.getenv("LLM_EMBEDDING_MODEL", "nomic-embed-text")
        self.fast_model = os.getenv("LLM_FAST_MODEL", "mistral:7b")
        self.thinking_model = os.getenv("LLM_THINKING_MODEL", "deepseek-r1:8b")
        
        print(f"LLM client configured for base URL: {base_url} in {APP_ENV} mode.")

# Instantiate a single, shared client configuration
llm_config = LLMClient()

# --- Expose the configured client and model names ---
llm_client = llm_config.client
EMBEDDING_MODEL = llm_config.embedding_model
FAST_MODEL = llm_config.fast_model
THINKING_MODEL = llm_config.thinking_model

# Example of how to use in another file:
# from src.config import llm_client, FAST_MODEL
# response = llm_client.chat.completions.create(model=FAST_MODEL, ...)

# --- Agent & Orchestrator Configurations ---
AGENT_CONFIGS = {
    "retrieval_timeout": 60, # Timeout for parallel retrieval steps

    "analysis_agent": {
        "model": THINKING_MODEL, # Needs strong reasoning
        "max_iterations": 2, # Allow for self-correction
        "timeout": 120,      # seconds
    },
    "insight_agent": {
        "model": THINKING_MODEL, # The most creative task
        "max_iterations": 1,
        "timeout": 150,
    },
    "report_agent": {
        "model": FAST_MODEL, # Primarily a formatting task
        "max_iterations": 1,
        "timeout": 60,
    }
}
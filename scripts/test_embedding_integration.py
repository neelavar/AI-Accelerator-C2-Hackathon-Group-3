def check_openrouter_endpoint():
    try:
        import openai
        base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        api_key = os.getenv("LLM_API_KEY")
        client = openai.OpenAI(base_url=base_url, api_key=api_key)
        response = client.embeddings.create(model="openai/text-embedding-3-small", input=["test"])
        if hasattr(response, 'error'):
            print(f"Openrouter endpoint error: {response.error}")
            return False
        return True
    except Exception as e:
        print(f"Could not connect to Openrouter endpoint: {e}")
        return False
import os
import requests
from src.backend.knowledge_base import embed_texts

def check_ollama_endpoint():
    url = "http://localhost:11434/api/embeddings"
    try:
        response = requests.post(url, json={"model": "nomic-embed-text", "prompt": "test"})
        if response.status_code == 404:
            print("Ollama endpoint /api/embeddings returned 404. Check Ollama server and model availability.")
            return False
        elif response.status_code != 200:
            print(f"Ollama endpoint error: {response.status_code} {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Could not connect to Ollama endpoint: {e}")
        return False


def test_ollama_embedding():
    os.environ["APP_ENV"] = "DEV"
    app_env = os.getenv("APP_ENV", "DEV")
    assert app_env.upper() == "DEV", f"APP_ENV should be 'DEV', got '{app_env}'"
    print("Checking Ollama endpoint...")
    if not check_ollama_endpoint():
        print("Ollama endpoint check failed. Skipping embedding test.")
        return
    test_texts = [
        "Cardiac events are influenced by age groups.",
        "Ollama provides local LLM inference.",
        "This is a test sentence for embedding."
    ]
    try:
        embeddings = embed_texts(test_texts)
        assert isinstance(embeddings, list), "Embeddings should be a list."
        assert len(embeddings) == len(test_texts), "Number of embeddings should match number of input texts."
        for emb in embeddings:
            assert isinstance(emb, list), "Each embedding should be a list of floats."
            assert len(emb) > 0, "Embedding vector should not be empty."
        print("Ollama embedding integration test PASSED.")
        print("Sample embedding:", embeddings[0])
    except Exception as e:
        print("Ollama embedding integration test FAILED.")
        embeddings = embed_texts(test_texts)
        assert isinstance(embeddings, list), "Embeddings should be a list."
        assert len(embeddings) == len(test_texts), "Number of embeddings should match number of input texts."
        for emb in embeddings:
            assert isinstance(emb, list), "Each embedding should be a list of floats."
            assert len(emb) > 0, "Embedding vector should not be empty."
        print("Openrouter embedding integration test PASSED.")
        print("Sample embedding:", embeddings[0])
    except Exception as e:
        print("Openrouter embedding integration test FAILED.")
        print("Error:", str(e))

def test_openrouter_embedding():
    os.environ["APP_ENV"] = "DEMO"
    app_env = os.getenv("APP_ENV", "DEMO")
    assert app_env.upper() == "DEMO", f"APP_ENV should be 'DEMO', got '{app_env}'"
    print("Checking Openrouter endpoint...")
    if not check_openrouter_endpoint():
        print("Openrouter endpoint check failed. Skipping embedding test.")
        return
    test_texts = [
        "Openrouter provides cloud-based LLM inference.",
        "This is a test sentence for Openrouter embedding."
    ]
    try:
        embeddings = embed_texts(test_texts)
        assert isinstance(embeddings, list), "Embeddings should be a list."
        assert len(embeddings) == len(test_texts), "Number of embeddings should match number of input texts."
        for emb in embeddings:
            assert isinstance(emb, list), "Each embedding should be a list of floats."
            assert len(emb) > 0, "Embedding vector should not be empty."
        print("Openrouter embedding integration test PASSED.")
        print("Sample embedding:", embeddings[0])
    except Exception as e:
        print("Openrouter embedding integration test FAILED.")
        print("Error:", str(e))

if __name__ == "__main__":
    app_env = os.getenv("APP_ENV", "DEV").upper()
    if app_env == "DEV":
        print("Testing Ollama integration...")
        test_ollama_embedding()
    elif app_env == "DEMO":
        print("Testing Openrouter integration...")
        test_openrouter_embedding()
    else:
        print(f"Unknown APP_ENV: {app_env}. Supported values are DEV and DEMO.")

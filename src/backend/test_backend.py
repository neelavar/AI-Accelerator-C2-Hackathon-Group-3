"""
Test script for backend modules: config, knowledge_base, and services.
"""
from config import settings
from knowledge_base import test_load_and_chunk
from services import test_pubmed_search

if __name__ == "__main__":
    print("Testing config loader...")
    print("LLM_FAST_MODEL:", settings.LLM_FAST_MODEL)
    print("Testing document loader and chunker...")
    # test_load_and_chunk('sample.txt', 'txt')  # Uncomment and provide a sample file
    print("Testing PubMed client...")
    test_pubmed_search()

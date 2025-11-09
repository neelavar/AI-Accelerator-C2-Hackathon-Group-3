"""
Test script for the KnowledgeBase in src/knowledge_base.py.
"""
import sys
import os
import asyncio
import shutil

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.knowledge_base import KnowledgeBase
from src.config import settings

async def main():
    """
    Tests the KnowledgeBase by adding a dummy document and performing a search.
    """
    kb = KnowledgeBase()
    
    # Define paths for dummy files
    dummy_txt_path = "dummy_test_kb.txt"
    
    # Ensure ChromaDB directory is clean for a fresh test
    if os.path.exists(settings.CHROMA_PERSIST_DIR):
        shutil.rmtree(settings.CHROMA_PERSIST_DIR)
        print(f"Cleaned up old ChromaDB directory: {settings.CHROMA_PERSIST_DIR}")

    # Create a dummy text file
    with open(dummy_txt_path, "w") as f:
        f.write("This is a test document about cardiovascular health. It discusses heart disease and risk factors. "
                "A healthy lifestyle is crucial for preventing these conditions. Regular exercise and a balanced diet "
                "are often recommended by doctors. Early detection can also play a role in treatment success.")
    print(f"Created dummy file: {dummy_txt_path}")
    
    try:
        print("\n--- Testing KnowledgeBase.add_documents ---")
        kb.add_documents([dummy_txt_path])

        print("\n--- Testing KnowledgeBase.search ---")
        query = "heart disease prevention"
        print(f"Searching for query: '{query}'")
        results = kb.search(query)
        
        if results:
            print(f"Found {len(results)} relevant documents:")
            for i, doc in enumerate(results):
                print(f"\n--- Result {i+1} ---")
                print(f"Source File: {doc.metadata.get('source_file', 'N/A')}")
                print(f"Content Snippet: {doc.page_content[:200]}...") # Print first 200 chars
        else:
            print("No relevant documents found for the query.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up dummy files
        if os.path.exists(dummy_txt_path):
            os.remove(dummy_txt_path)
            print(f"Removed dummy file: {dummy_txt_path}")
        
        # Clean up ChromaDB directory
        if os.path.exists(settings.CHROMA_PERSIST_DIR):
            shutil.rmtree(settings.CHROMA_PERSIST_DIR)
            print(f"Cleaned up ChromaDB directory: {settings.CHROMA_PERSIST_DIR}")

if __name__ == "__main__":
    asyncio.run(main())

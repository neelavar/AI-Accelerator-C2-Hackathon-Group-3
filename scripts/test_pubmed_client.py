"""
Test script for the PubMedClient in src/services/external_apis.py.
"""
import sys
import os
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.external_apis import PubMedClient
from src.config import settings # To potentially use API keys

async def main():
    """
    Tests the PubMedClient by performing a sample search and printing results.
    """
    # Initialize PubMedClient, potentially with an API key from settings
    # For basic searches, an API key is not strictly required, but good practice
    # client = PubMedClient(api_key=settings.PUBMED_API_KEY) # If PUBMED_API_KEY is defined in settings
    client = PubMedClient() # Using without API key for now

    try:
        print("--- Testing PubMedClient.search ---")
        query = "CRISPR gene editing cancer"
        print(f"Searching for: '{query}'")
        
        # Fetch a small number of results for testing
        results = await client.search(query, retmax=2)
        
        if results:
            print(f"Found {len(results)} articles:")
            for i, doc in enumerate(results):
                print(f"\n--- Article {i+1} ---")
                print(f"Title: {doc.metadata.get('title', 'N/A')}")
                print(f"PMID: {doc.metadata.get('pmid', 'N/A')}")
                print(f"URL: {doc.metadata.get('url', 'N/A')}")
                print(f"Authors: {doc.metadata.get('authors', 'N/A')}")
                print(f"Publication Date: {doc.metadata.get('publication_date', 'N/A')}")
                print(f"Content Snippet: {doc.page_content[:500]}...") # Print first 500 chars
        else:
            print("No articles found for the query.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the httpx client is closed
        await client.client.aclose()

if __name__ == "__main__":
    asyncio.run(main())

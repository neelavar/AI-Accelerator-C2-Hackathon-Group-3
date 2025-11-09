#!/usr/bin/env python3
"""
CLI script to test document retrieval functionality.

Usage: python scripts/test_retrieval.py "your search query"
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger
from mediscout.knowledge_base import KnowledgeBase
from mediscout.services.pubmed_client import PubMedClient


def main():
    """Test retrieval from both knowledge base and PubMed."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_retrieval.py 'search query'")
        print("Example: python scripts/test_retrieval.py 'diabetes treatment'")
        sys.exit(1)
    
    query = sys.argv[1]
    
    logger.info(f"Testing retrieval for query: '{query}'")
    
    # Test Knowledge Base
    print("\n" + "="*80)
    print("TESTING KNOWLEDGE BASE")
    print("="*80)
    
    try:
        kb = KnowledgeBase()
        stats = kb.get_collection_stats()
        
        print(f"\nKnowledge Base Stats:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Collection: {stats['collection_name']}")
        print(f"  Embedding model: {stats['embedding_model']}")
        
        if stats['total_chunks'] > 0:
            print(f"\nSearching knowledge base for: '{query}'")
            results = kb.search(query, top_k=5)
            
            print(f"\nFound {len(results)} results:")
            for i, doc in enumerate(results, 1):
                print(f"\n{i}. {doc.title}")
                print(f"   ID: {doc.id}")
                print(f"   Source: {doc.source}")
                print(f"   Relevance: {doc.relevance_score:.3f}")
                print(f"   Content preview: {doc.content[:200]}...")
        else:
            print("\n⚠️  Knowledge base is empty. Upload documents first.")
    
    except Exception as e:
        print(f"\n❌ Knowledge base search failed: {e}")
        logger.exception("KB search error")
    
    # Test PubMed
    print("\n" + "="*80)
    print("TESTING PUBMED API")
    print("="*80)
    
    try:
        client = PubMedClient()
        print(f"\nSearching PubMed for: '{query}'")
        print("This may take a few seconds...")
        
        results = client.search(query, max_results=5)
        
        print(f"\nFound {len(results)} PubMed articles:")
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.title}")
            print(f"   PMID: {doc.metadata.get('pmid', 'N/A')}")
            print(f"   Year: {doc.metadata.get('year', 'N/A')}")
            print(f"   Journal: {doc.metadata.get('journal', 'N/A')}")
            print(f"   URL: {doc.metadata.get('url', 'N/A')}")
            print(f"   Abstract preview: {doc.content[:200]}...")
    
    except Exception as e:
        print(f"\n❌ PubMed search failed: {e}")
        logger.exception("PubMed search error")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()


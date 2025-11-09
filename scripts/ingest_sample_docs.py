#!/usr/bin/env python3
"""
CLI script to ingest sample documents into the knowledge base.

Usage: python scripts/ingest_sample_docs.py <file1.pdf> <file2.txt> ...
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger
from mediscout.knowledge_base import KnowledgeBase


def main():
    """Ingest documents into the knowledge base."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_sample_docs.py <file1> <file2> ...")
        print("Example: python scripts/ingest_sample_docs.py data/sample.pdf data/study.txt")
        sys.exit(1)
    
    file_paths = [Path(f) for f in sys.argv[1:]]
    
    print("\n" + "="*80)
    print("DOCUMENT INGESTION")
    print("="*80)
    
    # Validate files
    for file_path in file_paths:
        if not file_path.exists():
            print(f"✗ File not found: {file_path}")
            sys.exit(1)
        
        if file_path.suffix.lower() not in ['.pdf', '.txt']:
            print(f"✗ Unsupported file type: {file_path}")
            print("  Only .pdf and .txt files are supported")
            sys.exit(1)
    
    print(f"\n📁 Files to ingest: {len(file_paths)}")
    for fp in file_paths:
        print(f"   - {fp.name} ({fp.stat().st_size / 1024:.1f} KB)")
    
    # Initialize knowledge base
    print("\n⚙️  Initializing knowledge base...")
    try:
        kb = KnowledgeBase()
        print("✓ Knowledge base initialized")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        logger.exception("Initialization failed")
        sys.exit(1)
    
    # Ingest each file
    print("\n🔄 Starting ingestion...")
    print("="*80)
    
    total_chunks = 0
    successful = 0
    failed = 0
    
    for file_path in file_paths:
        print(f"\n📄 Processing: {file_path.name}")
        
        try:
            chunks, doc_id = kb.ingest_document(file_path)
            
            print(f"   ✓ Success!")
            print(f"   Document ID: {doc_id}")
            print(f"   Chunks created: {chunks}")
            
            total_chunks += chunks
            successful += 1
        
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            failed += 1
            logger.exception(f"Failed to ingest {file_path}")
    
    # Summary
    print("\n" + "="*80)
    print("INGESTION SUMMARY")
    print("="*80)
    print(f"\n✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print(f"📦 Total chunks: {total_chunks}")
    
    # Knowledge base stats
    stats = kb.get_collection_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"   Total chunks in database: {stats['total_chunks']}")
    print(f"   Collection: {stats['collection_name']}")
    
    # Test search
    if total_chunks > 0:
        print(f"\n🔍 Testing search functionality...")
        test_query = "medical treatment"
        results = kb.search(test_query, top_k=3)
        print(f"   Query: '{test_query}'")
        print(f"   Results found: {len(results)}")
        
        if results:
            print(f"\n   Top result:")
            doc = results[0]
            print(f"   - Title: {doc.title}")
            print(f"   - Relevance: {doc.relevance_score:.3f}")
            print(f"   - Preview: {doc.content[:150]}...")
    
    print("\n✅ Ingestion complete!")


if __name__ == "__main__":
    main()


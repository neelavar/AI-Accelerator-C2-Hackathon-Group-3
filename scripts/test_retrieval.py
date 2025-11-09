from src.backend.knowledge_base import load_and_chunk_document, ingest_document
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

PDF_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'project-docs', 'sample-pdfs')

def test_load_and_chunk():
    # Find a PDF file in the sample-pdfs directory
    for fname in os.listdir(PDF_DIR):
        if fname.lower().endswith('.pdf'):
            pdf_path = os.path.join(PDF_DIR, fname)
            print(f"Testing load_and_chunk_document on: {pdf_path}")
            chunks = load_and_chunk_document(pdf_path)
            print(f"Total chunks: {len(chunks)}")
            for i, chunk in enumerate(chunks):
                print(f"Chunk {i}: {chunk[:100]}...")  # Print first 100 chars
            return pdf_path
    print("No PDF files found in sample-pdfs directory.")
    return None

def test_ingest_document(pdf_path):
    print(f"Testing ingest_document on: {pdf_path}")
    ingest_document(pdf_path, 'pdf')

if __name__ == "__main__":
    pdf_path = test_load_and_chunk()
    if pdf_path:
        test_ingest_document(pdf_path)
"""
CLI script to retrieve results from ChromaDB and PubMed, and print combined results.
"""
import sys
from src.backend.services import PubMedClient

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_retrieval.py <query_text>")
        sys.exit(1)
    query_text = sys.argv[1]
    # Query PubMed
    pubmed = PubMedClient()
    pubmed_results = pubmed.search(query_text)
    print("\nPubMed Results:")
    print(pubmed_results)

if __name__ == "__main__":
    main()

"""
Manages the local knowledge base using ChromaDB for document storage and retrieval.
"""
import os
from typing import List
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from src.config import settings

class KnowledgeBase:
    """
    Manages document ingestion, chunking, embedding, and retrieval using ChromaDB.
    """
    def __init__(self):
        # Initialize embedding model
        print(f"Initializing embeddings with model: {settings.LLM_EMBEDDING_MODEL} at base_url: {settings.LLM_BASE_URL}")
        self.embeddings = OpenAIEmbeddings(
            openai_api_base=settings.LLM_BASE_URL,
            openai_api_key=settings.LLM_API_KEY,
            model=settings.LLM_EMBEDDING_MODEL
        )
        
        # Initialize ChromaDB client
        self.vector_db = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )
        
        self.text_splitter = self._get_text_splitter()
        print(f"KnowledgeBase initialized. ChromaDB will persist to: {settings.CHROMA_PERSIST_DIR}")

    def _get_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Returns a configured RecursiveCharacterTextSplitter.
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    def _load_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Loads documents from a list of file paths based on their extension.
        """
        all_documents = []
        for file_path in file_paths:
            _, ext = os.path.splitext(file_path)
            if ext.lower() == ".pdf":
                loader = PyPDFLoader(file_path)
            elif ext.lower() == ".txt":
                loader = TextLoader(file_path)
            # elif ext.lower() == ".csv":
            #     # CSV support deferred as per MVP scope
            #     # For now, we can treat it as text or skip
            #     print(f"Warning: CSV file '{file_path}' skipped. CSV support is deferred.")
            #     continue
            else:
                print(f"Warning: File type '{ext}' not supported for '{file_path}'. Skipping.")
                continue
            
            try:
                documents = loader.load()
                # Add original filename to metadata
                for doc in documents:
                    doc.metadata["source_file"] = os.path.basename(file_path)
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        return all_documents

    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits loaded documents into smaller chunks.
        """
        chunked_documents = self.text_splitter.split_documents(documents)
        print(f"Chunked {len(documents)} documents into {len(chunked_documents)} chunks.")
        return chunked_documents

    def add_documents(self, file_paths: List[str]):
        """
        Loads, chunks, embeds, and adds documents to the ChromaDB.
        """
        print(f"Adding documents from: {file_paths}")
        loaded_docs = self._load_documents(file_paths)
        if not loaded_docs:
            print("No documents loaded. Skipping addition to KB.")
            return
        
        chunked_docs = self._chunk_documents(loaded_docs)
        
        # Add to ChromaDB
        self.vector_db.add_documents(chunked_docs)
        print(f"Successfully added {len(chunked_docs)} chunks to ChromaDB.")

    def search(self, query: str, k: int = 4) -> List[Document]:
        """
        Performs a similarity search in the ChromaDB for the given query.
        """
        print(f"Searching KnowledgeBase for query: '{query}' (top {k} results)")
        results = self.vector_db.similarity_search(query, k=k)
        print(f"Found {len(results)} relevant documents in KB.")
        return results

    def clear_collection(self):
        """
        Clears all data from the ChromaDB collection.
        Useful for testing or resetting the KB.
        """
        print(f"Clearing ChromaDB collection: {settings.CHROMA_COLLECTION_NAME}")
        self.vector_db.delete_collection()
        # Re-initialize the collection after deletion
        self.vector_db = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )
        print("ChromaDB collection cleared and re-initialized.")

# Example usage (for testing purposes)
async def main():
    kb = KnowledgeBase()
    
    # Create dummy files for testing
    dummy_txt_path = "dummy_test.txt"
    dummy_pdf_path = "dummy_test.pdf" # Requires a real PDF file or mock
    
    with open(dummy_txt_path, "w") as f:
        f.write("This is a test document about cardiovascular health. It discusses heart disease and risk factors.")
    
    # For PDF, you'd need a real PDF. Let's skip PDF for this simple test if not available.
    # Or create a very basic one if possible programmatically.
    # For now, we'll just test with TXT.
    
    try:
        # Clear existing data for a clean test run
        kb.clear_collection()

        # Add documents
        kb.add_documents([dummy_txt_path]) # Add dummy_pdf_path if you have one

        # Perform a search
        query = "heart disease risk factors"
        results = kb.search(query)
        
        print(f"\n--- Search Results for '{query}' ---")
        for i, doc in enumerate(results):
            print(f"Doc {i+1} (Source: {doc.metadata.get('source_file', 'N/A')}): {doc.page_content[:100]}...")
            
    finally:
        # Clean up dummy files
        if os.path.exists(dummy_txt_path):
            os.remove(dummy_txt_path)
        # if os.path.exists(dummy_pdf_path):
        #     os.remove(dummy_pdf_path)
        
        # Optionally clear the ChromaDB directory for a clean slate next time
        # import shutil
        # if os.path.exists(settings.CHROMA_PERSIST_DIR):
        #     shutil.rmtree(settings.CHROMA_PERSIST_DIR)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
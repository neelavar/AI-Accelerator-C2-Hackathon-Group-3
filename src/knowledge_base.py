import os
from typing import List
import chromadb # Import chromadb
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
        
        # Initialize ChromaDB client using PersistentClient
        print(f"Initializing ChromaDB PersistentClient at: {os.path.abspath(settings.CHROMA_PERSIST_DIR)}")
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        
        # Get or create the collection directly from the client
        self.chroma_collection = self.client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)
        
        # Wrap the chromadb collection with Langchain's Chroma
        self.vector_db = Chroma(
            client=self.client, # Pass the persistent client
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
        )
        
        self.text_splitter = self._get_text_splitter()
        print(f"KnowledgeBase initialized. ChromaDB will persist to: {os.path.abspath(settings.CHROMA_PERSIST_DIR)}")

    def _get_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Returns a configured RecursiveCharacterTextSplitter.
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks using the configured text splitter.
        """
        if not documents:
            return []
            
        print(f"Chunking {len(documents)} documents...")
        try:
            chunked_docs = self.text_splitter.split_documents(documents)
            print(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
            return chunked_docs
        except Exception as e:
            print(f"Error during document chunking: {e}")
            return []

    def _load_documents(self, file_info_list: List[tuple]) -> List[Document]:
        """
        Loads documents from a list of (file_path, original_file_name) tuples based on their extension.
        """
        all_documents = []
        for file_path, original_file_name in file_info_list:
            _, ext = os.path.splitext(file_path)
            if ext.lower() == ".pdf":
                loader = PyPDFLoader(file_path)
            elif ext.lower() == ".txt":
                loader = TextLoader(file_path)
            else:
                print(f"Warning: File type '{ext}' not supported for '{original_file_name}'. Skipping.")
                continue
            
            try:
                documents = loader.load()
                # Add original filename to metadata
                for doc in documents:
                    doc.metadata["source_file"] = original_file_name
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error loading {original_file_name} from {file_path}: {e}")
        return all_documents

    def add_documents(self, file_info_list: List[tuple]):
        """
        Loads, chunks, embeds, and adds documents to the ChromaDB.
        file_info_list is a list of (temp_file_path, original_file_name) tuples.
        """
        print(f"Adding documents from: {[info[1] for info in file_info_list]}")
        
        # Load documents
        loaded_docs = self._load_documents(file_info_list)
        print(f"Loaded {len(loaded_docs)} documents successfully")
        
        if not loaded_docs:
            print("No documents loaded. Skipping addition to KB.")
            return
        
        # Chunk documents
        print(f"Starting document chunking with {self.text_splitter}")
        chunked_docs = self._chunk_documents(loaded_docs)
        print(f"Created {len(chunked_docs)} chunks")
        
        if not chunked_docs:
            print("No chunks created. Skipping addition to KB.")
            return
            
        try:
            # Add to ChromaDB
            print("Adding chunks to ChromaDB...")
            self.vector_db.add_documents(chunked_docs)
            print(f"Successfully added {len(chunked_docs)} chunks to ChromaDB.")
            
            # Verify addition
            collection_info = self.vector_db._collection.get()
            total_docs = len(collection_info.get('ids', []))
            print(f"ChromaDB collection now contains {total_docs} total chunks")
        except Exception as e:
            print(f"Error adding documents to ChromaDB: {e}")
            raise  # Re-raise the exception to be handled by the caller

    def search(self, query: str, k: int = 4) -> List[Document]:
        """
        Performs a similarity search in the ChromaDB for the given query.
        """
        print(f"Searching KnowledgeBase for query: '{query}' (top {k} results)")
        results = self.vector_db.similarity_search(query, k=k)
        print(f"Found {len(results)} relevant documents in KB.")
        return results

    def get_all_document_metadata(self) -> List[dict]:
        """
        Retrieves metadata and page content for all documents in the ChromaDB collection.
        This is useful for re-populating the UI's indexed documents list across sessions.
        """
        print("Retrieving all document metadata from ChromaDB.")
        try:
            # First, get all IDs in the collection
            # Use a more robust way to get IDs, handling potential empty collection
            collection_info = self.vector_db._collection.get()
            all_ids = collection_info.get('ids', [])
            print(f"ChromaDB: Found {len(all_ids)} IDs in collection.")

            if not all_ids:
                print("ChromaDB: Collection is empty, no documents to retrieve.")
                return []

            collection_data = self.vector_db._collection.get(
                ids=all_ids,
                include=['metadatas', 'documents']
            )
            print(f"ChromaDB: Retrieved collection data: {collection_data}")
            
            unique_documents = {}
            for i in range(len(collection_data['ids'])):
                metadata = collection_data['metadatas'][i]
                page_content = collection_data['documents'][i]
                source_file = metadata.get('source_file', 'Unknown')
                
                # For simplicity, we'll store the first chunk's content as the preview content
                # In a real app, you might want to store a summary or a specific part.
                if source_file not in unique_documents:
                    unique_documents[source_file] = {
                        'name': source_file,
                        'size': 0, # We don't store size in ChromaDB, so this will be 0 or estimated
                        'status': 'indexed',
                        'content': page_content # Store content of the first chunk
                    }
                # Append content if multiple chunks from the same file
                else:
                    unique_documents[source_file]['content'] += "\n\n" + page_content

            print(f"ChromaDB: Processed {len(unique_documents)} unique documents from ChromaDB.")
            return list(unique_documents.values())
        except Exception as e:
            print(f"ChromaDB: Error retrieving all document metadata from ChromaDB: {e}")
            return []

    def clear_collection(self):
        """
        Clears all data from the ChromaDB collection.
        Useful for testing or resetting the KB.
        """
        print(f"Clearing ChromaDB collection: {settings.CHROMA_COLLECTION_NAME}")
        try:
            self.client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
            print(f"ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}' deleted.")
        except Exception as e:
            print(f"Warning: Could not delete collection '{settings.CHROMA_COLLECTION_NAME}'. It might not exist. Error: {e}")
        
        # Re-get the collection from the client to ensure self.vector_db points to a fresh, empty collection
        self.chroma_collection = self.client.get_or_create_collection(name=settings.CHROMA_COLLECTION_NAME)
        self.vector_db = Chroma(
            client=self.client,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
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
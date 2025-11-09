"""
Embedding generation and ChromaDB storage for document chunks.
"""
from chromadb import Client
from chromadb.config import Settings as ChromaSettings
from typing import List

class EmbeddingStore:
    def __init__(self, persist_directory: str = "chromadb_store"):
        self.client = Client(ChromaSettings(persist_directory=persist_directory))
        self.collection = self.client.get_or_create_collection(name="documents")

    def add_embeddings(self, ids: List[str], embeddings: List[List[float]], metadatas: List[dict]):
        self.collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)

    def query(self, query_embedding: List[float], n_results: int = 5):
        return self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

# Placeholder for embedding generation
# Replace with actual model inference (e.g., OpenAI, HuggingFace, etc.)
def generate_embedding(text: str) -> List[float]:
    # Dummy embedding: return a list of zeros
    return [0.0] * 768

# Example test function
def test_embedding_store():
    store = EmbeddingStore()
    texts = ["This is a test document.", "Another document for testing."]
    ids = ["doc1", "doc2"]
    embeddings = [generate_embedding(t) for t in texts]
    metadatas = [{"source": "test"}, {"source": "test"}]
    store.add_embeddings(ids, embeddings, metadatas)
    result = store.query(generate_embedding("test"))
    print(result)

if __name__ == "__main__":
    test_embedding_store()

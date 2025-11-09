import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import chromadb
from chromadb.config import Settings
from src.config import EMBEDDING_MODEL, llm_client, APP_ENV

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chromadb")

def load_and_chunk_document(file_path):
    """
    Loads a PDF or TXT file and splits it into chunks.
    Returns a list of text chunks.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    return [chunk.page_content for chunk in chunks]

def embed_texts(texts):
    """
    Generate embeddings for a list of texts using the configured embedding model.
    Uses Ollama in DEV mode and Openrouter in DEMO mode, based on APP_ENV.
    Returns a list of embeddings.
    """
    app_env = os.getenv("APP_ENV", "DEV")
    if app_env.upper() == "DEV":
        # Use Ollama embedding endpoint, sending one request per text
        import requests
        ollama_url = "http://localhost:11434/api/embeddings"
        embeddings = []
        for text in texts:
            response = requests.post(ollama_url, json={"model": EMBEDDING_MODEL, "prompt": text})
            response.raise_for_status()
            data = response.json()
            # Ollama returns embedding in 'embedding' key
            emb = data.get("embedding", [])
            embeddings.append(emb)
        return embeddings
    elif app_env.upper() == "DEMO":
        # Use Openrouter via llm_client
        response = llm_client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
        return [r.embedding for r in response.data]
    else:
        raise ValueError(f"Unknown APP_ENV: {app_env}. Supported: DEV (Ollama), DEMO (Openrouter)")

def ingest_document(file_path):
    """
    Loads, chunks, embeds, and stores a document in ChromaDB.
    """
    chunks = load_and_chunk_document(file_path)
    embeddings = embed_texts(chunks)
    client = chromadb.PersistentClient(path=DATA_DIR, settings=Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(name="kb")
    metadatas = [{"source": os.path.basename(file_path), "chunk_id": i} for i in range(len(chunks))]
    ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)
    print(f"Ingested {len(chunks)} chunks from {file_path} into ChromaDB at {DATA_DIR}")
"""
Document ingestion, chunking, embedding, and vector store management.
"""

from typing import List

class DocumentLoader:
    def load_txt(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_pdf(self, file_path: str) -> str:
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF loading.")
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

class TextChunker:
    def chunk(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - chunk_overlap
        return chunks

def ingest_document(file_path: str, file_type: str, store_dir: str = "chromadb_store"):
    loader = DocumentLoader()
    chunker = TextChunker()
    if file_type == 'txt':
        text = loader.load_txt(file_path)
    elif file_type == 'pdf':
        text = loader.load_pdf(file_path)
    else:
        raise ValueError('Unsupported file type')
    chunks = chunker.chunk(text)
    # ChromaDB ingestion logic is handled by ingest_document above
    print(f"Ingested {len(chunks)} chunks.")

def test_ingest_and_query(file_path: str, file_type: str, query_text: str):
    pass

if __name__ == "__main__":
    pass

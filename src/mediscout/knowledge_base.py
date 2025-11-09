"""
Knowledge base management for MediScout.

Handles document ingestion, text extraction, embedding generation, and vector storage.
"""

import hashlib
import uuid
from pathlib import Path
from typing import List, Optional, Tuple
from loguru import logger

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

from mediscout.config import get_settings
from mediscout.schemas import Document


class KnowledgeBase:
    """Manages document ingestion and vector search."""
    
    def __init__(self):
        """Initialize knowledge base with ChromaDB and embedding model."""
        self.settings = get_settings()
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.settings.embedding_model}")
        self.embedding_model = SentenceTransformer(
            self.settings.embedding_model,
            device=self.settings.embedding_device
        )
        
        # Initialize ChromaDB
        logger.info(f"Initializing ChromaDB at: {self.settings.chroma_persist_dir}")
        self.settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.settings.chroma_persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.settings.chroma_collection_name,
            metadata={"description": "MediScout document collection"}
        )
        
        logger.info(f"ChromaDB collection '{self.settings.chroma_collection_name}' ready")
    
    def extract_text_from_file(self, file_path: Path) -> str:
        """
        Extract text content from PDF or TXT file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file type not supported or extraction fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        # Check file size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self.settings.max_document_size_mb:
            raise ValueError(
                f"File too large: {size_mb:.1f}MB exceeds limit of {self.settings.max_document_size_mb}MB"
            )
        
        suffix = file_path.suffix.lower()
        
        if suffix == '.txt':
            logger.info(f"Extracting text from TXT: {file_path.name}")
            return file_path.read_text(encoding='utf-8', errors='ignore')
        
        elif suffix == '.pdf':
            logger.info(f"Extracting text from PDF: {file_path.name}")
            try:
                reader = PdfReader(str(file_path))
                text_parts = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                
                full_text = "\n\n".join(text_parts)
                
                if not full_text.strip():
                    raise ValueError("No text extracted from PDF (may be scanned image)")
                
                logger.info(f"Extracted {len(full_text)} characters from {len(reader.pages)} pages")
                return full_text
            
            except Exception as e:
                raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        
        else:
            raise ValueError(f"Unsupported file type: {suffix}. Only .txt and .pdf supported.")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of text chunks
        """
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        chunk_size_words = self.settings.chunk_size // 4  # Approximate tokens to words
        overlap_words = self.settings.chunk_overlap // 4
        
        for i in range(0, len(words), chunk_size_words - overlap_words):
            chunk_words = words[i:i + chunk_size_words]
            chunk = " ".join(chunk_words)
            if chunk.strip():
                chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=self.settings.embedding_batch_size,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def ingest_document(self, file_path: Path) -> Tuple[int, str]:
        """
        Ingest a document: extract text, chunk, embed, and store.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Tuple of (number of chunks added, document ID)
            
        Raises:
            ValueError: If ingestion fails
        """
        # Ensure file_path is a Path object
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
            
        logger.info(f"Ingesting document: {file_path}")
        
        # Extract text
        text = self.extract_text_from_file(file_path)
        
        # Generate document ID from file content hash
        content_hash = hashlib.md5(text.encode()).hexdigest()
        doc_id = f"user_{file_path.stem}_{content_hash[:8]}"
        
        # Check if already indexed
        existing = self.collection.get(ids=[doc_id])
        if existing['ids']:
            logger.info(f"Document already indexed: {doc_id}")
            return 0, doc_id
        
        # Chunk text
        chunks = self.chunk_text(text)
        
        if not chunks:
            raise ValueError("No chunks created from document")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)
        
        # Prepare data for ChromaDB
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": "user",
                "document_id": doc_id,
                "filename": file_path.name,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i in range(len(chunks))
        ]
        
        # Add to ChromaDB
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully indexed {len(chunks)} chunks for document: {doc_id}")
        return len(chunks), doc_id
    
    def search(self, query: str, top_k: int = 10) -> List[Document]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of Document objects
        """
        logger.info(f"Searching knowledge base for: '{query}' (top_k={top_k})")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )
        
        if not results['ids'] or not results['ids'][0]:
            logger.info("No results found")
            return []
        
        # Convert to Document objects
        documents = []
        for i, doc_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            content = results['documents'][0][i]
            distance = results['distances'][0][i]
            
            # Convert distance to similarity score (1 - normalized distance)
            similarity = 1.0 / (1.0 + distance)
            
            doc = Document(
                id=metadata.get('document_id', doc_id),
                source="user",
                title=metadata.get('filename', 'Unknown'),
                content=content,
                metadata=metadata,
                relevance_score=similarity
            )
            documents.append(doc)
        
        logger.info(f"Found {len(documents)} relevant documents")
        return documents
    
    def get_collection_stats(self) -> dict:
        """Get statistics about the knowledge base."""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.settings.chroma_collection_name,
            "embedding_model": self.settings.embedding_model,
            "embedding_dimension": self.settings.embedding_dimension
        }
    
    def clear_collection(self):
        """Delete all documents from collection (for testing)."""
        logger.warning("Clearing all documents from collection")
        self.chroma_client.delete_collection(self.settings.chroma_collection_name)
        self.collection = self.chroma_client.create_collection(
            name=self.settings.chroma_collection_name,
            metadata={"description": "MediScout document collection"}
        )


"""Unit tests for knowledge base module."""

import pytest
from pathlib import Path
import tempfile

from src.mediscout.knowledge_base import KnowledgeBase


@pytest.fixture
def kb():
    """Create a KnowledgeBase instance for testing."""
    kb = KnowledgeBase()
    yield kb
    # Cleanup after tests
    kb.clear_collection()


@pytest.fixture
def sample_txt_file():
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document about medical research. " * 100)
        f.flush()
        yield Path(f.name)
    
    Path(f.name).unlink(missing_ok=True)


def test_kb_initialization(kb):
    """Test KnowledgeBase initialization."""
    assert kb.embedding_model is not None
    assert kb.collection is not None
    
    stats = kb.get_collection_stats()
    assert "total_chunks" in stats
    assert "collection_name" in stats


def test_text_chunking(kb):
    """Test text chunking functionality."""
    text = "word " * 1000  # 1000 words
    chunks = kb.chunk_text(text)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_embedding_generation(kb):
    """Test embedding generation."""
    texts = ["Test sentence 1", "Test sentence 2"]
    embeddings = kb.generate_embeddings(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == kb.settings.embedding_dimension


def test_extract_text_from_txt(kb, sample_txt_file):
    """Test text extraction from TXT file."""
    text = kb.extract_text_from_file(sample_txt_file)
    
    assert len(text) > 0
    assert "medical research" in text


def test_extract_text_unsupported_type(kb):
    """Test extraction fails for unsupported file types."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        kb.extract_text_from_file(Path("test.docx"))


def test_ingest_document(kb, sample_txt_file):
    """Test document ingestion."""
    chunks, doc_id = kb.ingest_document(sample_txt_file)
    
    assert chunks > 0
    assert doc_id.startswith("user_")
    
    # Verify document is searchable
    results = kb.search("medical research", top_k=5)
    assert len(results) > 0


def test_search_empty_kb():
    """Test search on empty knowledge base."""
    kb = KnowledgeBase()
    kb.clear_collection()
    
    results = kb.search("test query", top_k=5)
    assert len(results) == 0


def test_search_returns_documents(kb, sample_txt_file):
    """Test search returns Document objects."""
    kb.ingest_document(sample_txt_file)
    
    results = kb.search("medical", top_k=3)
    
    assert len(results) > 0
    for doc in results:
        assert doc.id is not None
        assert doc.source == "user"
        assert doc.content is not None
        assert doc.relevance_score is not None


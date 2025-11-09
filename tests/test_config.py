"""Unit tests for configuration module."""

import pytest
from pathlib import Path

from src.mediscout.config import get_settings, reset_settings


def test_get_settings():
    """Test settings singleton."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2  # Should be same instance


def test_settings_defaults():
    """Test default settings values."""
    settings = get_settings()
    
    assert settings.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.embedding_dimension == 384
    assert settings.chunk_size == 1000
    assert settings.chunk_overlap == 200
    assert settings.top_k_results == 20


def test_settings_validation():
    """Test settings validation."""
    from src.mediscout.config import Settings
    
    # Chunk overlap must be less than chunk size
    with pytest.raises(ValueError):
        Settings(chunk_size=500, chunk_overlap=600)


def test_reset_settings():
    """Test settings reset."""
    settings1 = get_settings()
    reset_settings()
    settings2 = get_settings()
    
    # Should be different instances after reset
    assert settings1 is not settings2


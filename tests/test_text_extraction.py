"""
Unit tests for text extraction service.

TDD approach: Tests define expected behavior for PDF/TXT extraction.
"""

import pytest
from pathlib import Path
from typing import BinaryIO
from io import BytesIO

from mediscout.services.text_extraction import (
    TextExtractionService,
    UnsupportedFileTypeError,
    EmptyDocumentError,
    FileTooLargeError,
)


class TestTextExtractionService:
    """Test text extraction from various file types."""

    @pytest.fixture
    def extractor(self) -> TextExtractionService:
        """Create text extraction service instance."""
        return TextExtractionService(max_size_mb=50)

    def test_extract_from_txt_file(self, extractor: TextExtractionService, tmp_path: Path) -> None:
        """Test extracting text from plain text file."""
        # Create a temporary text file
        txt_file = tmp_path / "test.txt"
        content = "This is a test document.\nWith multiple lines.\n"
        txt_file.write_text(content, encoding="utf-8")

        # Extract text
        extracted = extractor.extract_from_file(txt_file)

        assert extracted == content
        assert len(extracted) > 0

    def test_extract_from_txt_bytes(self, extractor: TextExtractionService) -> None:
        """Test extracting text from text bytes."""
        content = "Test content from bytes"
        file_bytes = BytesIO(content.encode("utf-8"))

        extracted = extractor.extract_from_bytes(file_bytes, filename="test.txt")

        assert extracted == content

    def test_unsupported_file_type(self, extractor: TextExtractionService, tmp_path: Path) -> None:
        """Test that unsupported file types raise error."""
        unsupported_file = tmp_path / "test.doc"  # .doc not supported
        unsupported_file.write_bytes(b"fake doc content")

        with pytest.raises(UnsupportedFileTypeError):
            extractor.extract_from_file(unsupported_file)

    def test_empty_file_raises_error(self, extractor: TextExtractionService, tmp_path: Path) -> None:
        """Test that empty files raise appropriate error."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("", encoding="utf-8")

        with pytest.raises(EmptyDocumentError):
            extractor.extract_from_file(empty_file)

    def test_file_too_large(self, tmp_path: Path) -> None:
        """Test that files exceeding size limit raise error."""
        extractor = TextExtractionService(max_size_mb=1)  # 1MB limit

        large_file = tmp_path / "large.txt"
        # Create 2MB file
        large_file.write_text("a" * (2 * 1024 * 1024), encoding="utf-8")

        with pytest.raises(FileTooLargeError):
            extractor.extract_from_file(large_file)

    def test_supported_extensions(self, extractor: TextExtractionService) -> None:
        """Test that service reports supported extensions."""
        supported = extractor.supported_extensions

        assert ".txt" in supported
        assert ".pdf" in supported
        assert len(supported) >= 2

    def test_whitespace_normalization(self, extractor: TextExtractionService, tmp_path: Path) -> None:
        """Test that excessive whitespace is normalized."""
        txt_file = tmp_path / "whitespace.txt"
        content = "Text   with    extra     spaces\n\n\nAnd   newlines"
        txt_file.write_text(content, encoding="utf-8")

        extracted = extractor.extract_from_file(txt_file, normalize_whitespace=True)

        # Should have single spaces
        assert "   " not in extracted
        # Should have max 2 newlines
        assert "\n\n\n" not in extracted


class TestPDFExtraction:
    """Test PDF-specific extraction."""

    @pytest.fixture
    def extractor(self) -> TextExtractionService:
        """Create text extraction service."""
        return TextExtractionService()

    def test_extract_from_simple_pdf(self, extractor: TextExtractionService) -> None:
        """Test extracting from a simple PDF (mock)."""
        # This test would use a real PDF in integration tests
        # For unit tests, we'll mock the PDF extraction
        pytest.skip("Requires real PDF file for integration testing")

    def test_pdf_with_multiple_pages(self, extractor: TextExtractionService) -> None:
        """Test extracting from multi-page PDF."""
        pytest.skip("Requires real PDF file for integration testing")

    def test_pdf_page_metadata(self, extractor: TextExtractionService) -> None:
        """Test extraction includes page metadata."""
        pytest.skip("Requires real PDF file for integration testing")


@pytest.mark.unit
class TestTextCleaning:
    """Test text cleaning utilities."""

    @pytest.fixture
    def extractor(self) -> TextExtractionService:
        return TextExtractionService()

    def test_remove_special_characters(self, extractor: TextExtractionService) -> None:
        """Test removing special control characters."""
        dirty_text = "Text\x00with\x01control\x02chars"
        clean = extractor.clean_text(dirty_text)

        assert "\x00" not in clean
        assert "\x01" not in clean
        assert "Text" in clean

    def test_normalize_unicode(self, extractor: TextExtractionService) -> None:
        """Test Unicode normalization."""
        text_with_unicode = "Café naïve résumé"
        normalized = extractor.clean_text(text_with_unicode)

        # Should preserve readable unicode
        assert "Café" in normalized or "Cafe" in normalized

    def test_preserve_medical_terms(self, extractor: TextExtractionService) -> None:
        """Test that medical terminology is preserved."""
        medical_text = "Patient showed α-synuclein aggregation and β-amyloid plaques."
        cleaned = extractor.clean_text(medical_text)

        # Should preserve Greek letters and hyphens
        assert "α" in cleaned or "alpha" in cleaned
        assert "β" in cleaned or "beta" in cleaned


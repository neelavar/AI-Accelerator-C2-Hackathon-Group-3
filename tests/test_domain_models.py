"""
Unit tests for domain models.

TDD approach: These tests define the expected behavior.
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from mediscout.models.domain import (
    AnalysisResult,
    Chunk,
    ConfidenceLevel,
    Document,
    DocumentSource,
    Hypothesis,
    Report,
    RetrievalResult,
    SessionStatus,
    StudyDesign,
)


class TestDocumentModel:
    """Test Document model validation and behavior."""

    def test_create_document_with_required_fields(self) -> None:
        """Test creating a document with minimum required fields."""
        doc = Document(
            source=DocumentSource.USER_UPLOAD,
            title="Test Paper",
            content="This is test content for the research paper.",
        )

        assert isinstance(doc.document_id, UUID)
        assert doc.source == DocumentSource.USER_UPLOAD
        assert doc.title == "Test Paper"
        assert doc.content == "This is test content for the research paper."
        assert doc.authors == []
        assert isinstance(doc.created_at, datetime)

    def test_document_with_all_fields(self) -> None:
        """Test document with all optional fields populated."""
        doc = Document(
            source=DocumentSource.PUBMED,
            title="Complete Research Paper",
            authors=["Dr. Smith", "Dr. Jones"],
            abstract="This is an abstract.",
            content="Full paper content here.",
            url="https://example.com/paper",
            doi="10.1234/test",
            publication_date=datetime(2024, 1, 1),
        )

        assert doc.source == DocumentSource.PUBMED
        assert len(doc.authors) == 2
        assert doc.url == "https://example.com/paper"
        assert doc.doi == "10.1234/test"

    def test_document_content_cannot_be_empty(self) -> None:
        """Test that document content validation rejects empty strings."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            Document(
                source=DocumentSource.USER_UPLOAD,
                title="Test",
                content="   ",  # Only whitespace
            )

    def test_document_word_count(self) -> None:
        """Test word count property."""
        doc = Document(
            source=DocumentSource.USER_UPLOAD,
            title="Test",
            content="This is a test document with ten words here now.",
        )
        assert doc.word_count == 10

    def test_document_to_dict(self) -> None:
        """Test serialization to dictionary."""
        doc = Document(
            source=DocumentSource.PUBMED,
            title="Test Paper",
            content="Content here.",
        )
        doc_dict = doc.to_dict()

        assert isinstance(doc_dict, dict)
        assert doc_dict["title"] == "Test Paper"
        assert doc_dict["source"] == "pubmed"


class TestChunkModel:
    """Test Chunk model validation and behavior."""

    def test_create_chunk_with_required_fields(self) -> None:
        """Test creating a chunk with minimum fields."""
        doc_id = uuid4()
        chunk = Chunk(
            document_id=doc_id,
            content="This is a text chunk.",
            sequence_number=0,
            start_char=0,
            end_char=21,
        )

        assert chunk.document_id == doc_id
        assert chunk.sequence_number == 0
        assert chunk.char_count == 21
        assert not chunk.has_embedding

    def test_chunk_with_embedding(self) -> None:
        """Test chunk with embedding vector."""
        chunk = Chunk(
            document_id=uuid4(),
            content="Text chunk",
            sequence_number=0,
            start_char=0,
            end_char=10,
            embedding=[0.1, 0.2, 0.3] * 128,  # 384-dim vector
        )

        assert chunk.has_embedding
        assert len(chunk.embedding) == 384

    def test_chunk_end_char_must_be_after_start(self) -> None:
        """Test validation that end_char > start_char."""
        with pytest.raises(ValueError, match="end_char must be greater than start_char"):
            Chunk(
                document_id=uuid4(),
                content="Test",
                sequence_number=0,
                start_char=10,
                end_char=5,  # Invalid: before start
            )


class TestRetrievalResultModel:
    """Test RetrievalResult model."""

    def test_create_retrieval_result(self) -> None:
        """Test creating retrieval result with ranked chunks."""
        chunk1 = Chunk(
            document_id=uuid4(),
            content="Relevant chunk 1",
            sequence_number=0,
            start_char=0,
            end_char=16,
        )
        chunk2 = Chunk(
            document_id=uuid4(),
            content="Relevant chunk 2",
            sequence_number=1,
            start_char=0,
            end_char=16,
        )

        result = RetrievalResult(
            query="test query",
            results=[(chunk1, 0.9), (chunk2, 0.7)],
            total_results=2,
        )

        assert result.query == "test query"
        assert len(result.results) == 2
        assert result.total_results == 2
        assert result.average_score == 0.8

    def test_retrieval_result_top_k_chunks(self) -> None:
        """Test extracting just chunks without scores."""
        chunk1 = Chunk(
            document_id=uuid4(), content="C1", sequence_number=0, start_char=0, end_char=2
        )
        chunk2 = Chunk(
            document_id=uuid4(), content="C2", sequence_number=0, start_char=0, end_char=2
        )

        result = RetrievalResult(
            query="test", results=[(chunk1, 0.9), (chunk2, 0.8)], total_results=2
        )

        chunks = result.top_k_chunks
        assert len(chunks) == 2
        assert chunks[0].content == "C1"
        assert chunks[1].content == "C2"

    def test_retrieval_scores_must_be_valid(self) -> None:
        """Test score validation (0-1 range)."""
        chunk = Chunk(
            document_id=uuid4(), content="Test", sequence_number=0, start_char=0, end_char=4
        )

        with pytest.raises(ValueError, match="Score must be between 0 and 1"):
            RetrievalResult(query="test", results=[(chunk, 1.5)], total_results=1)


class TestAnalysisResultModel:
    """Test AnalysisResult model."""

    def test_create_analysis_result(self) -> None:
        """Test creating analysis result."""
        doc_id = uuid4()
        analysis = AnalysisResult(
            document_id=doc_id,
            summary="This RCT shows significant results.",
            study_design=StudyDesign.RCT,
            outcomes=["Primary outcome improved", "Secondary outcome stable"],
            reliability_score=0.9,
        )

        assert analysis.document_id == doc_id
        assert analysis.study_design == StudyDesign.RCT
        assert analysis.is_high_quality
        assert 0.0 <= analysis.reliability_score <= 1.0

    def test_case_study_not_high_quality(self) -> None:
        """Test that case studies are not marked as high quality."""
        analysis = AnalysisResult(
            document_id=uuid4(),
            summary="Case study summary",
            study_design=StudyDesign.CASE_STUDY,
            outcomes=[],
            reliability_score=0.3,
        )

        assert not analysis.is_high_quality


class TestHypothesisModel:
    """Test Hypothesis model."""

    def test_create_hypothesis(self) -> None:
        """Test creating hypothesis with valid data."""
        hyp = Hypothesis(
            statement="SSRIs may inhibit c-KIT pathway in GIST prevention.",
            reasoning_chain=[
                "SSRI users show lower GIST incidence",
                "c-KIT mutation is primary GIST driver",
                "SSRIs have off-target kinase effects",
            ],
            supporting_docs=[uuid4(), uuid4()],
            confidence=ConfidenceLevel.MEDIUM,
            novelty_score=0.75,
        )

        assert hyp.confidence == ConfidenceLevel.MEDIUM
        assert len(hyp.supporting_docs) >= 2
        assert 0.0 <= hyp.novelty_score <= 1.0

    def test_hypothesis_requires_min_two_sources(self) -> None:
        """Test that hypotheses require at least 2 supporting documents."""
        with pytest.raises(ValueError, match="minimum 2 supporting documents"):
            Hypothesis(
                statement="Test hypothesis",
                reasoning_chain=["Reason 1", "Reason 2"],
                supporting_docs=[uuid4()],  # Only 1 doc - should fail
                confidence=ConfidenceLevel.LOW,
                novelty_score=0.5,
            )


class TestReportModel:
    """Test Report model."""

    def test_create_report(self) -> None:
        """Test creating a complete report."""
        hyp = Hypothesis(
            statement="Test hypothesis",
            reasoning_chain=["R1", "R2"],
            supporting_docs=[uuid4(), uuid4()],
            confidence=ConfidenceLevel.HIGH,
            novelty_score=0.8,
        )

        report = Report(
            title="GIST Prevention Research Report",
            exec_summary="Summary of findings on GIST prevention factors.",
            detailed_findings="Detailed analysis shows correlation between SSRIs and lower GIST rates.",
            hypotheses=[hyp],
            citations=["Smith et al. (2023)", "Jones et al. (2024)"],
        )

        assert report.title == "GIST Prevention Research Report"
        assert report.hypothesis_count == 1
        assert report.citation_count == 2
        assert "medical advice" in report.medical_disclaimer.lower()

    def test_report_export_markdown(self) -> None:
        """Test markdown export functionality."""
        report = Report(
            title="Test Report",
            exec_summary="Executive summary here.",
            detailed_findings="Detailed findings here.",
            hypotheses=[],
            citations=["Ref 1", "Ref 2"],
        )

        markdown = report.export_markdown()

        assert "# Test Report" in markdown
        assert "## Executive Summary" in markdown
        assert "## References" in markdown
        assert "1. Ref 1" in markdown
        assert report.medical_disclaimer in markdown


# ============================================================================
# Enum Tests
# ============================================================================


class TestEnums:
    """Test enum definitions."""

    def test_session_status_values(self) -> None:
        """Test all session status values."""
        assert SessionStatus.INITIALIZING.value == "initializing"
        assert SessionStatus.COMPLETED.value == "completed"

    def test_document_source_values(self) -> None:
        """Test all document source values."""
        assert DocumentSource.PUBMED.value == "pubmed"
        assert DocumentSource.USER_UPLOAD.value == "user_upload"

    def test_study_design_values(self) -> None:
        """Test all study design values."""
        assert StudyDesign.RCT.value == "rct"
        assert StudyDesign.META_ANALYSIS.value == "meta_analysis"

    def test_confidence_level_values(self) -> None:
        """Test confidence level values."""
        assert ConfidenceLevel.LOW.value == "low"
        assert ConfidenceLevel.HIGH.value == "high"


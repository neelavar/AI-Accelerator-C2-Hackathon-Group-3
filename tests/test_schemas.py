"""Unit tests for Pydantic schemas."""

import pytest
from datetime import datetime

from src.mediscout.schemas import (
    Document,
    AnalysisResult,
    Hypothesis,
    Report,
    QueryValidation,
    RetrievalResult
)


def test_document_creation():
    """Test Document schema."""
    doc = Document(
        id="test_001",
        source="pubmed",
        title="Test Study",
        content="This is test content",
        metadata={"pmid": "12345"},
        relevance_score=0.95
    )
    
    assert doc.id == "test_001"
    assert doc.source == "pubmed"
    assert doc.relevance_score == 0.95


def test_document_source_validation():
    """Test Document source validation."""
    # Valid sources
    for source in ["user", "pubmed", "clinicaltrials", "scholar"]:
        doc = Document(
            id="test",
            source=source,
            title="Test",
            content="Test"
        )
        assert doc.source == source


def test_analysis_result():
    """Test AnalysisResult schema."""
    analysis = AnalysisResult(
        document_id="pmid:12345",
        summary="Test summary",
        study_design="RCT",
        key_findings=["Finding 1", "Finding 2"],
        reliability_score=0.9
    )
    
    assert analysis.document_id == "pmid:12345"
    assert len(analysis.key_findings) == 2
    assert 0 <= analysis.reliability_score <= 1


def test_hypothesis_creation():
    """Test Hypothesis schema."""
    hyp = Hypothesis(
        id="hyp_001",
        statement="Test hypothesis",
        reasoning_chain=["Step 1", "Step 2"],
        supporting_evidence=["pmid:123", "pmid:456"],
        confidence="medium"
    )
    
    assert hyp.confidence in ["low", "medium", "high"]
    assert len(hyp.reasoning_chain) == 2


def test_query_validation():
    """Test QueryValidation schema."""
    validation = QueryValidation(
        is_valid=True,
        refined_query="improved query",
        medical_terms=["metformin", "diabetes"],
        suggestions=[]
    )
    
    assert validation.is_valid is True
    assert len(validation.medical_terms) == 2


def test_retrieval_result():
    """Test RetrievalResult schema."""
    doc1 = Document(id="1", source="user", title="Doc1", content="Content1")
    doc2 = Document(id="2", source="pubmed", title="Doc2", content="Content2")
    
    result = RetrievalResult(
        query="test query",
        user_documents=[doc1],
        pubmed_documents=[doc2],
        total_count=2,
        sources_used=["user", "pubmed"],
        retrieval_time_seconds=1.5
    )
    
    assert result.total_count == 2
    assert len(result.all_documents) == 2


def test_report_creation():
    """Test Report schema."""
    report = Report(
        research_topic="Test topic",
        executive_summary="Summary",
        methods="Methods",
        detailed_findings="Findings",
        contradictions_and_gaps="Gaps",
        sources_cited=["Source 1"],
        document_count=5
    )
    
    assert report.document_count == 5
    assert isinstance(report.generated_at, datetime)


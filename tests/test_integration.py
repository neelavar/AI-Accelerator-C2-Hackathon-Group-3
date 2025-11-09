"""Integration tests for MediScout end-to-end workflow."""

import pytest
from pathlib import Path
import tempfile

from src.mediscout.orchestrator import ResearchOrchestrator
from src.mediscout.config import get_settings


@pytest.fixture
def sample_document():
    """Create a temporary test document."""
    content = """
    Medical Research Study on Diabetes Treatment
    
    This study investigates the efficacy of metformin in type 2 diabetes patients.
    The randomized controlled trial included 500 patients over 12 months.
    
    Results showed a significant reduction in HbA1c levels (p < 0.01).
    The treatment was well-tolerated with minimal side effects.
    
    Conclusion: Metformin is effective for managing type 2 diabetes.
    """ * 5  # Make it longer
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        f.flush()
        yield Path(f.name)
    
    Path(f.name).unlink(missing_ok=True)


@pytest.mark.integration
def test_document_ingestion_workflow(sample_document):
    """Test document ingestion through orchestrator."""
    orchestrator = ResearchOrchestrator()
    retriever = orchestrator.get_retriever()
    
    # Test ingestion
    results = retriever.ingest_documents([str(sample_document)])
    
    assert len(results["successful"]) == 1
    assert results["total_chunks"] > 0
    
    # Verify searchability
    docs = retriever.knowledge_base.search("diabetes metformin", top_k=3)
    assert len(docs) > 0


@pytest.mark.integration
@pytest.mark.slow
def test_full_research_workflow_minimal():
    """Test complete research workflow with minimal setup."""
    settings = get_settings()
    
    # Skip if no API key
    if not settings.has_openrouter_key:
        pytest.skip("OpenRouter API key not configured")
    
    orchestrator = ResearchOrchestrator()
    
    # Simple research query
    result = orchestrator.run_research(
        research_topic="benefits of exercise for health"
    )
    
    # Verify workflow completed
    assert result is not None
    assert result["current_stage"] in ["report_complete", "failed"]
    
    # Check report generation
    if result.get("final_report_markdown"):
        assert len(result["final_report_markdown"]) > 0
        assert "Executive Summary" in result["final_report_markdown"] or "Error" in result["final_report_markdown"]


@pytest.mark.integration
def test_pubmed_search():
    """Test PubMed API integration."""
    from src.mediscout.services.pubmed_client import PubMedClient
    
    client = PubMedClient()
    
    # Search for a common topic
    results = client.search("diabetes treatment", max_results=3)
    
    # Should return some results
    assert isinstance(results, list)
    
    # If results found, verify structure
    if results:
        doc = results[0]
        assert doc.source == "pubmed"
        assert doc.id.startswith("pmid:")
        assert len(doc.title) > 0


@pytest.mark.integration
@pytest.mark.slow
def test_end_to_end_with_document(sample_document):
    """Test complete E2E workflow with document upload."""
    settings = get_settings()
    
    if not settings.has_openrouter_key:
        pytest.skip("OpenRouter API key not configured")
    
    orchestrator = ResearchOrchestrator()
    retriever = orchestrator.get_retriever()
    
    # Step 1: Ingest document
    ingest_results = retriever.ingest_documents([str(sample_document)])
    assert len(ingest_results["successful"]) == 1
    
    # Step 2: Run research
    result = orchestrator.run_research(
        research_topic="efficacy of metformin for diabetes"
    )
    
    # Step 3: Verify results
    assert result is not None
    assert result.get("retrieved_documents") is not None
    
    # Should have retrieved our document
    retrieved_ids = [doc.id for doc in result.get("retrieved_documents", [])]
    assert any("user_" in doc_id for doc_id in retrieved_ids)
    
    # Should have generated a report
    assert result.get("final_report_markdown") is not None


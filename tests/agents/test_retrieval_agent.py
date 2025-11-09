"""
Unit tests for the retrieval agent.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.retrieval_agent import search_web, retrieve_from_kb
from src.schemas import OptimizedQueries
from src.state import ResearchState

@pytest.fixture
def sample_state() -> ResearchState:
    """Provides a sample research state for testing."""
    return {
        "topic": "Cardiovascular disease risk factors",
        "request_id": "test_123",
        "user_docs": [],
        "web_results": [],
        "context": [],
        "validation_result": None,
        "analysis": None,
        "hypotheses": None,
        "report": "",
        "error": None,
    }

def test_search_web(mocker, sample_state):
    """
    Tests the web search function.
    It should use an LLM to optimize the query and then call the pubmed client.
    """
    # 1. Arrange
    # Mock the LLM client for query optimization
    mock_llm_client = MagicMock()
    mock_structured_llm = MagicMock()
    optimized_query_obj = OptimizedQueries(
        pubmed_query="cardiovascular disease risk factors MeSH",
        google_scholar_queries=[] # Not used in this agent
    )
    mock_llm_client.chat.completions.with_structured_output.return_value = mock_structured_llm
    mock_structured_llm.create.return_value = optimized_query_obj

    # Mock the PubMed client
    mock_pubmed_client = MagicMock()
    expected_web_docs = ["doc1 from pubmed", "doc2 from pubmed"]
    mock_pubmed_client.search.return_value = expected_web_docs

    # 2. Act
    result = search_web(sample_state, mock_llm_client, mock_pubmed_client)

    # 3. Assert
    # Assert LLM was called for optimization
    mock_structured_llm.create.assert_called_once()
    
    # Assert PubMed client was called with the optimized query
    mock_pubmed_client.search.assert_called_once_with(optimized_query_obj.pubmed_query)
    
    # Assert the final result is correct
    assert "web_results" in result
    assert result["web_results"] == expected_web_docs

def test_retrieve_from_kb(mocker, sample_state):
    """
    Tests the knowledge base retrieval function.
    It should call the search method of the kb_retriever.
    """
    # 1. Arrange
    mock_kb_retriever = MagicMock()
    expected_kb_docs = ["doc1 from kb", "doc2 from kb"]
    mock_kb_retriever.search.return_value = expected_kb_docs

    # 2. Act
    result = retrieve_from_kb(sample_state, mock_kb_retriever)

    # 3. Assert
    # Assert the kb_retriever's search method was called with the topic
    mock_kb_retriever.search.assert_called_once_with(sample_state["topic"])
    
    # Assert the final result is correct
    assert "user_docs" in result
    assert result["user_docs"] == expected_kb_docs

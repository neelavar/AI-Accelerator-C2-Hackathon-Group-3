"""
Unit tests for the analysis agent.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.analysis_agent import execute_analysis
from src.schemas import CriticalAnalysisOutput, SourceAnalysis
from src.state import ResearchState

@pytest.fixture
def sample_state_with_context() -> ResearchState:
    """Provides a sample research state with context for testing."""
    return {
        "topic": "Cardiovascular disease risk factors",
        "request_id": "test_123",
        "user_docs": ["doc from kb"],
        "web_results": ["doc from web"],
        "context": ["doc from kb", "doc from web"], # Merged context
        "validation_result": None,
        "analysis": None,
        "hypotheses": None,
        "report": "",
        "error": None,
    }

def test_execute_analysis(mocker, sample_state_with_context):
    """
    Tests the analysis agent.
    It should call the LLM with the context and return a structured analysis.
    """
    # 1. Arrange
    mock_llm_client = MagicMock()
    mock_structured_llm = MagicMock()

    # Define the expected output from the mocked LLM
    expected_analysis = CriticalAnalysisOutput(
        analyses=[
            SourceAnalysis(
                source_id="doc_0",
                summary="The KB doc discusses established risk factors.",
                contradictions=None
            ),
            SourceAnalysis(
                source_id="doc_1",
                summary="The web doc highlights a new potential risk factor.",
                contradictions=["Contradicts the established list in doc_0"]
            )
        ]
    )
    
    mock_llm_client.chat.completions.with_structured_output.return_value = mock_structured_llm
    mock_structured_llm.create.return_value = expected_analysis

    # 2. Act
    result = execute_analysis(sample_state_with_context, mock_llm_client)

    # 3. Assert
    # Assert that the structured output method was called with the correct schema
    mock_llm_client.chat.completions.with_structured_output.assert_called_once_with(CriticalAnalysisOutput)
    
    # Assert that the create method was called
    mock_structured_llm.create.assert_called_once()
    
    # Assert that the agent returned the correct dictionary structure
    assert "analysis" in result
    assert result["analysis"] == expected_analysis.model_dump()
    assert len(result["analysis"]["analyses"]) == 2
    assert result["analysis"]["analyses"][1]["contradictions"] is not None

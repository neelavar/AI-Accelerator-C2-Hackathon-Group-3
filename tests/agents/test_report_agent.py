"""
Unit tests for the report building agent.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.report_agent import execute_report_building
from src.state import ResearchState

@pytest.fixture
def sample_state_with_analysis() -> ResearchState:
    """Provides a sample research state with analysis data for testing."""
    return {
        "topic": "Cardiovascular disease risk factors",
        "request_id": "test_123",
        "user_docs": [],
        "web_results": [],
        "context": [],
        "validation_result": None,
        "analysis": {
            "analyses": [
                {"source_id": "doc_0", "summary": "Summary from doc 0.", "contradictions": None},
                {"source_id": "doc_1", "summary": "Summary from doc 1.", "contradictions": ["Contradicts doc_0."]}
            ]
        },
        "hypotheses": None,
        "report": "",
        "error": None,
    }

def test_execute_report_building(mocker, sample_state_with_analysis):
    """
    Tests the report building agent.
    It should call the LLM with the analysis data and return a report string.
    """
    # 1. Arrange
    mock_llm_client = MagicMock()
    
    # Mock the response from the LLM
    expected_report = "# Executive Summary\nThis is a mock report."
    mock_choice = MagicMock()
    mock_choice.message.content = expected_report
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_llm_client.chat.completions.create.return_value = mock_response

    # 2. Act
    result = execute_report_building(sample_state_with_analysis, mock_llm_client)

    # 3. Assert
    # Assert that the LLM was called
    mock_llm_client.chat.completions.create.assert_called_once()
    
    # Assert that the prompt passed to the LLM contains the context
    call_args = mock_llm_client.chat.completions.create.call_args
    prompt = call_args.kwargs['messages'][1]['content']
    assert "Summary from doc 0." in prompt
    assert "Contradicts doc_0." in prompt
    
    # Assert that the agent returned the correct dictionary structure
    assert "report" in result
    assert result["report"] == expected_report

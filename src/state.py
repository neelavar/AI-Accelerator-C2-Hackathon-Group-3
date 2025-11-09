"""
Defines the shared state object for the LangGraph orchestrator.
"""
from typing import TypedDict, List, Optional
from langchain_core.documents import Document

class ResearchState(TypedDict):
    """
    Represents the state of the research process.
    It's an accumulator, with each agent adding to it.
    """
    topic: str
    request_id: str
    
    # Data retrieved from sources
    user_docs: List[Document]
    web_results: List[Document]
    
    # Combined context for analysis
    context: List[Document]

    # Structured outputs from agents
    validation_result: Optional[dict]
    analysis: Optional[dict]
    hypotheses: Optional[dict]
    
    # Final output
    report: str
    
    # Error handling
    error: Optional[str]

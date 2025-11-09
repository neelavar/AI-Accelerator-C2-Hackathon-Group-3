"""
Main orchestrator for the multi-agent research system.
Uses LangGraph to define and manage the agentic workflow.
"""
from unittest.mock import MagicMock
from langgraph.graph import StateGraph, END
from src.state import ResearchState
from src.schemas import QueryValidation, OptimizedQueries, CriticalAnalysisOutput, SourceAnalysis

# Import agent execution functions
from src.agents.validation_agent import execute_validation
from src.agents.retrieval_agent import search_web, retrieve_from_kb
from src.agents.analysis_agent import execute_analysis
from src.agents.report_agent import execute_report_building
from src.constants import (
    VALIDATION_NODE, RETRIEVAL_WEB_NODE, RETRIEVAL_KB_NODE, MERGE_CONTEXTS_NODE,
    VALIDATE_RETRIEVED_DATA_NODE, ANALYSIS_NODE, GENERATE_INSIGHTS_NODE, REPORT_NODE,
    SHOULD_RETRIEVE, HAS_SUFFICIENT_DATA, SHOULD_GENERATE_INSIGHTS
)

# --- Mock Clients (for testing the graph with mocked agent logic) ---

# Define the mock results
validation_result_obj = QueryValidation(is_valid_topic=True, is_injection_attempt=False, reason="Mock")
optimized_query_obj = OptimizedQueries(pubmed_query="test query", google_scholar_queries=[])
analysis_result_obj = CriticalAnalysisOutput(analyses=[SourceAnalysis(source_id="mock_doc", summary="summary", contradictions=["contradiction"])])
report_content = "# Final Report"

# This function will act as the side effect for the mock
def get_mock_for_schema(schema):
    mock_structured_llm = MagicMock()
    if schema == QueryValidation:
        mock_structured_llm.create.return_value = validation_result_obj
    elif schema == OptimizedQueries:
        mock_structured_llm.create.return_value = optimized_query_obj
    elif schema == CriticalAnalysisOutput:
        mock_structured_llm.create.return_value = analysis_result_obj
    else:
        # Default mock if schema not recognized
        mock_structured_llm.create.return_value = MagicMock()
    return mock_structured_llm

# Mock LLM Client
mock_llm_client = MagicMock()
mock_llm_client.chat.completions.with_structured_output.side_effect = get_mock_for_schema

# Mock for report agent's standard chat completion
mock_choice = MagicMock()
mock_choice.message.content = report_content
mock_response = MagicMock()
mock_response.choices = [mock_choice]
mock_llm_client.chat.completions.create.return_value = mock_response

# Mock External Service Clients
mock_pubmed_client = MagicMock()
mock_pubmed_client.search.return_value = ["doc from pubmed"]

mock_kb_retriever = MagicMock()
mock_kb_retriever.search.return_value = ["doc from kb"]


# --- Agent Node Wrappers ---

def validation_node(state: ResearchState):
    print(f"\n--- Node: {VALIDATION_NODE} ---")
    result = execute_validation(state, mock_llm_client)
    return {"validation_result": result.get("validation_result")}

def retrieval_web_node(state: ResearchState):
    print(f"\n--- Node: {RETRIEVAL_WEB_NODE} ---")
    result = search_web(state, mock_llm_client, mock_pubmed_client)
    return {"web_results": result.get("web_results")}

def retrieval_kb_node(state: ResearchState):
    print(f"\n--- Node: {RETRIEVAL_KB_NODE} ---")
    result = retrieve_from_kb(state, mock_kb_retriever)
    return {"user_docs": result.get("user_docs")}

def analysis_node(state: ResearchState):
    print(f"\n--- Node: {ANALYSIS_NODE} ---")
    result = execute_analysis(state, mock_llm_client)
    return {"analysis": result.get("analysis")}

def report_node(state: ResearchState):
    print(f"\n--- Node: {REPORT_NODE} ---")
    result = execute_report_building(state, mock_llm_client)
    return {"report": result.get("report")}

def merge_contexts_node(state: ResearchState):
    print(f"\n--- Node: {MERGE_CONTEXTS_NODE} ---")
    combined_docs = state.get("user_docs", []) + state.get("web_results", [])
    return {"context": combined_docs}

def validate_retrieved_data_node(state: ResearchState):
    print(f"\n--- Node: {VALIDATE_RETRIEVED_DATA_NODE} ---")
    # Simple validation: check if context is not empty
    if not state.get("context"):
        return {"error": "No data retrieved."}
    return {}

def generate_insights_node(state: ResearchState):
    """Placeholder for the Insight Generation Agent."""
    print(f"\n--- Node: {GENERATE_INSIGHTS_NODE} (Placeholder) ---")
    # This would call the insight generation agent
    return {"hypotheses": ["mock hypothesis"]}


# --- Conditional Edges ---

def should_retrieve(state: ResearchState) -> str:
    print(f"\n--- Conditional Edge: {SHOULD_RETRIEVE} ---")
    if state.get("validation_result", {}).get("is_valid_topic"):
        return [RETRIEVAL_WEB_NODE, RETRIEVAL_KB_NODE]
    return END

def has_sufficient_data(state: ResearchState) -> str:
    print(f"\n--- Conditional Edge: {HAS_SUFFICIENT_DATA} ---")
    if state.get("error"):
        return END
    return ANALYSIS_NODE

def should_generate_insights(state: ResearchState) -> str:
    print(f"\n--- Conditional Edge: {SHOULD_GENERATE_INSIGHTS} ---")
    analysis_output = state.get("analysis", {})
    if any(a.get("contradictions") for a in analysis_output.get("analyses", [])):
        return GENERATE_INSIGHTS_NODE
    return REPORT_NODE

# --- Graph Definition ---

def create_workflow():
    workflow = StateGraph(ResearchState)

    workflow.add_node(VALIDATION_NODE, validation_node)
    workflow.add_node(RETRIEVAL_WEB_NODE, retrieval_web_node)
    workflow.add_node(RETRIEVAL_KB_NODE, retrieval_kb_node)
    workflow.add_node(MERGE_CONTEXTS_NODE, merge_contexts_node)
    workflow.add_node(VALIDATE_RETRIEVED_DATA_NODE, validate_retrieved_data_node)
    workflow.add_node(ANALYSIS_NODE, analysis_node)
    workflow.add_node(GENERATE_INSIGHTS_NODE, generate_insights_node)
    workflow.add_node(REPORT_NODE, report_node)

    workflow.set_entry_point(VALIDATION_NODE)
    
    workflow.add_conditional_edges(VALIDATION_NODE, should_retrieve)
    
    workflow.add_edge(RETRIEVAL_WEB_NODE, MERGE_CONTEXTS_NODE)
    workflow.add_edge(RETRIEVAL_KB_NODE, MERGE_CONTEXTS_NODE)
    
    workflow.add_edge(MERGE_CONTEXTS_NODE, VALIDATE_RETRIEVED_DATA_NODE)
    
    workflow.add_conditional_edges(VALIDATE_RETRIEVED_DATA_NODE, has_sufficient_data)
    
    workflow.add_conditional_edges(ANALYSIS_NODE, should_generate_insights)
    
    workflow.add_edge(GENERATE_INSIGHTS_NODE, REPORT_NODE)
    workflow.add_edge(REPORT_NODE, END)

    return workflow.compile()

if __name__ == '__main__':
    app = create_workflow()
    print("Workflow created. Run scripts/test_orchestrator.py to test execution.")
    # To visualize:
    # from IPython.display import Image
    # Image(app.get_graph().draw_mermaid_png())


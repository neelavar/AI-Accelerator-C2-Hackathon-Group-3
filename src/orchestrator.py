"""
Main orchestrator for the multi-agent research system.
Uses LangGraph to define and manage the agentic workflow.
"""
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

# Import required modules
import asyncio
from openai import OpenAI
from src.knowledge_base import KnowledgeBase
from src.services.external_apis import PubMedClient
from src.config import settings
import uuid

# Initialize real clients
llm_client = OpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL
)

# Initialize KnowledgeBase
kb = KnowledgeBase()

# Initialize PubMedClient (no API key needed for basic access)
pubmed_client = PubMedClient()


# --- Agent Node Wrappers ---

def validation_node(state: ResearchState):
    print(f"\n--- Node: {VALIDATION_NODE} ---")
    result = execute_validation(state, llm_client)
    return {"validation_result": result.get("validation_result")}

def retrieval_web_node(state: ResearchState):
    print(f"\n--- Node: {RETRIEVAL_WEB_NODE} ---")
    result = search_web(state, llm_client, pubmed_client)
    return {"web_results": result.get("web_results")}

def retrieval_kb_node(state: ResearchState):
    print(f"\n--- Node: {RETRIEVAL_KB_NODE} ---")
    result = retrieve_from_kb(state, kb)
    return {"user_docs": result.get("user_docs")}

def analysis_node(state: ResearchState):
    print(f"\n--- Node: {ANALYSIS_NODE} ---")
    result = execute_analysis(state, llm_client)
    return {"analysis": result.get("analysis")}

def report_node(state: ResearchState):
    print(f"\n--- Node: {REPORT_NODE} ---")
    result = execute_report_building(state, llm_client)
    return {"report": result.get("report")}

def merge_contexts_node(state: ResearchState):
    print(f"\n--- Node: {MERGE_CONTEXTS_NODE} ---")
    user_docs = state.get("user_docs", []) or []  # Convert None to empty list
    web_results = state.get("web_results", []) or []  # Convert None to empty list
    combined_docs = user_docs + web_results
    print(f"Merged {len(user_docs)} user docs with {len(web_results)} web results")
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
    """
    Creates and configures the research workflow graph.
    The graph includes both synchronous and asynchronous nodes.
    """
    workflow = StateGraph(ResearchState)

    # Add all nodes to the graph
    workflow.add_node(VALIDATION_NODE, validation_node)
    workflow.add_node(RETRIEVAL_WEB_NODE, retrieval_web_node)  # This is an async node
    workflow.add_node(RETRIEVAL_KB_NODE, retrieval_kb_node)
    workflow.add_node(MERGE_CONTEXTS_NODE, merge_contexts_node)
    workflow.add_node(VALIDATE_RETRIEVED_DATA_NODE, validate_retrieved_data_node)
    workflow.add_node(ANALYSIS_NODE, analysis_node)
    workflow.add_node(GENERATE_INSIGHTS_NODE, generate_insights_node)
    workflow.add_node(REPORT_NODE, report_node)

    # Set the entry point
    workflow.set_entry_point(VALIDATION_NODE)
    
    # Configure edges
    workflow.add_conditional_edges(VALIDATION_NODE, should_retrieve)
    
    # Parallel retrieval paths merge at MERGE_CONTEXTS_NODE
    workflow.add_edge(RETRIEVAL_WEB_NODE, MERGE_CONTEXTS_NODE)
    workflow.add_edge(RETRIEVAL_KB_NODE, MERGE_CONTEXTS_NODE)
    
    workflow.add_edge(MERGE_CONTEXTS_NODE, VALIDATE_RETRIEVED_DATA_NODE)
    workflow.add_conditional_edges(VALIDATE_RETRIEVED_DATA_NODE, has_sufficient_data)
    workflow.add_conditional_edges(ANALYSIS_NODE, should_generate_insights)
    workflow.add_edge(GENERATE_INSIGHTS_NODE, REPORT_NODE)
    workflow.add_edge(REPORT_NODE, END)

    print("Workflow configured and ready")
    return workflow

def generate_research_report(topic: str, callback_handler = None) -> str:
    """
    Main interface function to generate a research report.
    Args:
        topic: The research topic to investigate
        callback_handler: Optional callback handler for progress updates
    Returns:
        The generated report as a markdown string
    """
    try:
        # Create workflow
        workflow = create_workflow()
        app = workflow.compile()
        
        # Initialize state
        initial_state = {
            "topic": topic,
            "request_id": str(uuid.uuid4()),
            "fast_llm_model": settings.LLM_FAST_MODEL,
            "smart_llm_model": settings.LLM_THINKING_MODEL,
            "user_docs": [],
            "web_results": [],
            "context": [],
            "validation_result": None,
            "analysis": None,
            "hypotheses": None,
            "report": "",
            "error": None
        }
        
        # Map node names to user-friendly status messages
        step_messages = {
            VALIDATION_NODE: "Validating Research Query",
            RETRIEVAL_KB_NODE: "Retrieving Documents from Knowledge Base",
            RETRIEVAL_WEB_NODE: "Searching Medical Literature (PubMed)",
            MERGE_CONTEXTS_NODE: "Combining Search Results",
            VALIDATE_RETRIEVED_DATA_NODE: "Validating Retrieved Data",
            ANALYSIS_NODE: "Analyzing Research Documents",
            GENERATE_INSIGHTS_NODE: "Generating Research Insights",
            REPORT_NODE: "Building Final Report"
        }
        
        # Execute workflow
        final_state = initial_state  # Initialize with initial state
        for state in app.stream(initial_state):
            # Extract node name and state
            try:
                node_name, node_state = next(iter(state.items()))
                if node_state is not None:  # Only update if we got valid state
                    final_state = node_state
                
                if callback_handler:
                    # Convert node name to user-friendly message
                    status_msg = step_messages.get(node_name, "Processing...")
                    callback_handler.on_chain_start({"name": status_msg}, {})
            except Exception as e:
                print(f"Error processing state update: {str(e)}")
                continue  # Skip problematic updates but don't fail
                
        if not isinstance(final_state, dict):
            raise Exception("Invalid workflow state")
            
        # Get result from final state
        error = final_state.get("error")
        if error:
            raise Exception(error)
            
        report = final_state.get("report")
        if not report:
            # Check if we can determine what went wrong
            validation_result = final_state.get("validation_result")
            if validation_result and not validation_result.get("is_valid_topic"):
                raise Exception(f"Invalid research topic: {validation_result.get('reason', 'Unknown reason')}")
                
            analysis = final_state.get("analysis")
            if not analysis:
                raise Exception("No analysis was generated")
                
            raise Exception("No report was generated. Please try again.")
        
    except Exception as e:
        error_msg = f"Error generating report: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

if __name__ == '__main__':
    app = create_workflow()
    print("Workflow created. Run scripts/test_orchestrator.py to test execution.")
    # To visualize:
    # from IPython.display import Image
    # Image(app.get_graph().draw_mermaid_png())


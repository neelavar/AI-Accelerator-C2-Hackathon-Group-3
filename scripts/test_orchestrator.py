"""
Test script for the LangGraph orchestrator scaffold.

Invokes the workflow with a sample initial state and prints the execution trace.
This verifies that the graph is wired correctly before implementing agent logic.
"""
import sys
import os
import uuid

# Add the project root to the Python path to allow importing from 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import create_workflow
from src.state import ResearchState
from src.constants import (
    VALIDATION_NODE, RETRIEVAL_WEB_NODE, RETRIEVAL_KB_NODE, MERGE_CONTEXTS_NODE,
    VALIDATE_RETRIEVED_DATA_NODE, ANALYSIS_NODE, GENERATE_INSIGHTS_NODE, REPORT_NODE
)

def main():
    """
    Initializes and runs the workflow with a mock state.
    """
    print("\n--- Initializing and running the orchestrator test ---\n")
    
    # Create the workflow
    workflow = create_workflow()

    # Define the initial state for the test run
    initial_state: ResearchState = {
        "topic": "Treatments for Chronic Kidney Disease",
        "request_id": f"test_{uuid.uuid4()}",
        "user_docs": [],
        "web_results": [],
        "context": [],
        "validation_result": None,
        "analysis": None,
        "hypotheses": None,
        "report": "",
        "error": None,
    }

    print(f"Initial State:\n{initial_state}\n")

    # Invoke the workflow
    # The `stream` method lets us see the state changes at each step
    final_state = None
    for event in workflow.stream(initial_state):
        # The event is a dictionary with the node name as the key
        (node_name, node_state), = event.items()
        # Use constants for printing node names
        if node_name == VALIDATION_NODE:
            print(f"--- Output from node: '{VALIDATION_NODE}' ---")
        elif node_name == RETRIEVAL_WEB_NODE:
            print(f"--- Output from node: '{RETRIEVAL_WEB_NODE}' ---")
        elif node_name == RETRIEVAL_KB_NODE:
            print(f"--- Output from node: '{RETRIEVAL_KB_NODE}' ---")
        elif node_name == MERGE_CONTEXTS_NODE:
            print(f"--- Output from node: '{MERGE_CONTEXTS_NODE}' ---")
        elif node_name == VALIDATE_RETRIEVED_DATA_NODE:
            print(f"--- Output from node: '{VALIDATE_RETRIEVED_DATA_NODE}' ---")
        elif node_name == ANALYSIS_NODE:
            print(f"--- Output from node: '{ANALYSIS_NODE}' ---")
        elif node_name == GENERATE_INSIGHTS_NODE:
            print(f"--- Output from node: '{GENERATE_INSIGHTS_NODE}' ---")
        elif node_name == REPORT_NODE:
            print(f"--- Output from node: '{REPORT_NODE}' ---")
        else:
            print(f"--- Output from node: '{node_name}' ---") # Fallback for END or other unexpected nodes
        
        print(node_state)
        print("\n")
        final_state = node_state

    print("\n--- Workflow finished. ---\n")
    print(f"Final State:\n{final_state}")

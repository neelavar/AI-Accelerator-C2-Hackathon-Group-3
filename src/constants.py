"""
Constants for node and edge names in the LangGraph orchestrator.
"""

# Node Names
VALIDATION_NODE = "validation_node"
RETRIEVAL_WEB_NODE = "retrieval_web_node"
RETRIEVAL_KB_NODE = "retrieval_kb_node"
MERGE_CONTEXTS_NODE = "merge_contexts_node"
VALIDATE_RETRIEVED_DATA_NODE = "validate_retrieved_data_node"
ANALYSIS_NODE = "analysis_node"
GENERATE_INSIGHTS_NODE = "generate_insights_node"
REPORT_NODE = "report_node"

# Conditional Edge Keys (functions that return the next node(s))
SHOULD_RETRIEVE = "should_retrieve"
HAS_SUFFICIENT_DATA = "has_sufficient_data"
SHOULD_GENERATE_INSIGHTS = "should_generate_insights"

"""
Agent for validating the user's research query.
"""
from openai import OpenAI
from src.state import ResearchState
from src.schemas import QueryValidation
from src.utils import _load_prompt_template

# Load the prompt template once when the module is loaded
VALIDATION_PROMPT_TEMPLATE = _load_prompt_template("validation_agent_prompt.txt")

def execute_validation(state: ResearchState, llm_client: OpenAI) -> dict:
    """
    Executes the query validation logic.

    Args:
        state: The current research state.
        llm_client: An OpenAI-compatible client.

    Returns:
        A dictionary with the 'validation_result'.
    """
    topic = state["topic"]
    
    # Format the loaded prompt template with the current topic
    prompt = VALIDATION_PROMPT_TEMPLATE.format(topic=topic)
    
    print(f"Validation Agent: Calling LLM for topic '{topic}'")
    
    # In a real implementation, this would be a model instance with structured output enabled.
    # The test will mock this call.
    structured_llm = llm_client.chat.completions.with_structured_output(QueryValidation)
    
    try:
        validation_result = structured_llm.create(
            model="mock-fast-model", # Model name will be managed by config
            messages=[
                {"role": "system", "content": "You are a classification expert."},
                {"role": "user", "content": prompt},
            ]
        )
        return {"validation_result": validation_result.model_dump()}
    except Exception as e:
        print(f"Error during validation: {e}")
        return {"error": "Failed to validate query."}


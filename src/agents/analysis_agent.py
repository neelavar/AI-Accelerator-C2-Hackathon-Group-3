"""
Agent for performing critical analysis on the retrieved context.
"""
from openai import OpenAI
from src.state import ResearchState
from src.schemas import CriticalAnalysisOutput
from src.utils import _load_prompt_template

# Load the prompt template once when the module is loaded
ANALYSIS_PROMPT_TEMPLATE = _load_prompt_template("analysis_agent_prompt.txt")

def execute_analysis(state: ResearchState, llm_client: OpenAI) -> dict:
    """
    Executes the critical analysis logic.
    """
    context_docs = state["context"]
    
    # Format the context for the LLM prompt
    formatted_context = "\n\n---\n\n".join([f"Source ID: doc_{i}\n\n{doc}" for i, doc in enumerate(context_docs)])

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(formatted_context=formatted_context)
    
    print("Analysis Agent: Calling LLM for critical analysis.")
    
    structured_llm = llm_client.chat.completions.with_structured_output(CriticalAnalysisOutput)
    
    try:
        analysis_result = structured_llm.create(
            model="mock-thinking-model", # This would use the high-reasoning model
            messages=[
                {"role": "system", "content": "You are a world-class medical analyst."}, 
                {"role": "user", "content": prompt},
            ]
        )
        return {"analysis": analysis_result.model_dump()}
    except Exception as e:
        print(f"Error during analysis: {e}")
        return {"error": "Failed to perform critical analysis."}


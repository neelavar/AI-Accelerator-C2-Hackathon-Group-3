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
    
    # Process documents in chunks to handle token limits
    chunk_size = 3  # Process 3 documents at a time
    all_analyses = []
    
    for i in range(0, len(context_docs), chunk_size):
        chunk_docs = context_docs[i:i + chunk_size]
        formatted_chunk = "\n\n---\n\n".join([f"Source ID: doc_{j}\n\n{doc}" for j, doc in enumerate(chunk_docs, start=i)])
        
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(formatted_context=formatted_chunk)
        print(f"Analysis Agent: Analyzing chunk {i//chunk_size + 1} of {(len(context_docs) + chunk_size - 1)//chunk_size}")
    
    # Define the function schema for analysis
    tools = [{
        "type": "function",
        "function": {
            "name": "analyze_sources",
            "description": "Analyze medical research sources",
            "parameters": {
                "type": "object",
                "properties": {
                    "analyses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_id": {
                                    "type": "string",
                                    "description": "Identifier for the source"
                                },
                                "summary": {
                                    "type": "string",
                                    "description": "Summary of key findings"
                                },
                                "contradictions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of contradictions found"
                                }
                            },
                            "required": ["source_id", "summary", "contradictions"]
                        }
                    }
                },
                "required": ["analyses"]
            }
        }
    }]
    
    try:
        for i in range(0, len(context_docs), chunk_size):
            chunk_docs = context_docs[i:i + chunk_size]
            formatted_chunk = "\n\n---\n\n".join([f"Source ID: doc_{j}\n\n{doc}" for j, doc in enumerate(chunk_docs, start=i)])
            
            prompt = ANALYSIS_PROMPT_TEMPLATE.format(formatted_context=formatted_chunk)
            
            try:
                response = llm_client.chat.completions.create(
                    model=state.get("smart_llm_model", "gpt-4"),
                    messages=[
                        {"role": "system", "content": "You are a world-class medical analyst."}, 
                        {"role": "user", "content": prompt}
                    ],
                    tools=tools,
                    tool_choice={"type": "function", "function": {"name": "analyze_sources"}}
                )
                
                # Extract the analysis result from the function call
                tool_call = response.choices[0].message.tool_calls[0]
                import json
                chunk_result = json.loads(tool_call.function.arguments)
                all_analyses.extend(chunk_result.get("analyses", []))
                
            except Exception as e:
                print(f"Error analyzing chunk {i//chunk_size + 1}: {str(e)}")
                continue  # Continue with next chunk even if one fails
        
        if not all_analyses:
            return {"error": "Failed to analyze any documents"}
            
        # Combine all analyses
        analysis_result = {"analyses": all_analyses}
        return {"analysis": analysis_result}
    except Exception as e:
        print(f"Error during analysis: {e}")
        return {"error": "Failed to perform critical analysis."}


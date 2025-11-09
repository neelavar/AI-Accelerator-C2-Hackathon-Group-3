"""
Agent for building the final research report.
"""
from openai import OpenAI
from src.state import ResearchState
from src.schemas import CriticalAnalysisOutput # Used for type hinting and context building
from src.utils import _load_prompt_template

# Load the prompt template once when the module is loaded
REPORT_PROMPT_TEMPLATE = _load_prompt_template("report_agent_prompt.txt")

def execute_report_building(state: ResearchState, llm_client: OpenAI) -> dict:
    """
    Executes the report building logic.
    """
    topic = state["topic"]
    analysis = state.get("analysis") # This is a dict from the analysis agent
    
    # In a real scenario, we would have more robust error handling and formatting
    if not analysis:
        return {"error": "Analysis result not found in state."}

    # --- Build the prompt context from the analysis state ---
    detailed_findings = []
    contradictions_gaps = []
    sources = []

    for i, item in enumerate(analysis.get("analyses", [])):
        source_id = item.get('source_id', f'doc_{i}')
        summary = item.get('summary', 'No summary provided.')
        
        detailed_findings.append(f"### Source: {source_id}\n- {summary}")
        sources.append(f"- {source_id}")
        
        if item.get("contradictions"):
            contradictions_gaps.extend(item["contradictions"])

    findings_str = "\n\n".join(detailed_findings)
    contradictions_str = "\n- ".join(contradictions_gaps) if contradictions_gaps else "None identified."
    sources_str = "\n".join(sources)

    prompt = REPORT_PROMPT_TEMPLATE.format(
        topic=topic,
        findings_str=findings_str,
        contradictions_str=contradictions_str,
        sources_str=sources_str
    )
    
    print("Report Builder Agent: Calling LLM to generate final report.")
    
    try:
        response = llm_client.chat.completions.create(
            model=state.get("smart_llm_model", "gpt-4"),  # Use the high-reasoning model from state
            messages=[
                {"role": "system", "content": "You are an expert medical writer."}, 
                {"role": "user", "content": prompt},
            ]
        )
        report_content = response.choices[0].message.content
        return {"report": report_content}
    except Exception as e:
        print(f"Error during report building: {e}")
        return {"error": "Failed to build report."}

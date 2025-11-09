from openai import OpenAI
from src.state import ResearchState
from src.schemas import OptimizedQueries
from src.utils import _load_prompt_template

# Load the prompt template once when the module is loaded
RETRIEVAL_PROMPT_TEMPLATE = _load_prompt_template("retrieval_agent_pubmed_query_prompt.txt")

# These would be imported from other modules developed by Dev 1
# For now, they are conceptual placeholders for mocking.
# from src.knowledge_base import KnowledgeBase
# from src.services.external_apis import PubMedClient

def search_web(state: ResearchState, llm_client: OpenAI, pubmed_client: object) -> dict:
    """
    Performs a web search using external APIs like PubMed.
    It first uses an LLM to optimize the user's topic into a search query.
    """
    topic = state["topic"]
    print(f"Web Retrieval Agent: Optimizing query for topic '{topic}'")

    # --- 1. Optimize Query using LLM ---
    # This is a conceptual representation of using a model with structured output
    prompt = RETRIEVAL_PROMPT_TEMPLATE.format(topic=topic)
    structured_llm = llm_client.chat.completions.with_structured_output(OptimizedQueries)
    
    try:
        query_optimization_result = structured_llm.create(
            model="mock-fast-model",
            messages=[
                {"role": "system", "content": "You are a search query optimization expert."},
                {"role": "user", "content": prompt},
            ]
        )
        optimized_query = query_optimization_result.pubmed_query
        print(f"Web Retrieval Agent: Optimized PubMed query: '{optimized_query}'")

        # --- 2. Call External API ---
        # The pubmed_client itself will be a mock in the unit test.
        print(f"Web Retrieval Agent: Calling PubMed client with query.")
        web_docs = pubmed_client.search(optimized_query)
        
        return {"web_results": web_docs}

    except Exception as e:
        print(f"Error during web search: {e}")
        return {"error": "Failed to perform web search."}


def retrieve_from_kb(state: ResearchState, kb_retriever: object) -> dict:
    """
    Retrieves relevant documents from the local knowledge base (ChromaDB).
    """
    topic = state["topic"]
    print(f"KB Retrieval Agent: Retrieving documents for topic '{topic}'")

    # The kb_retriever will be a mock in the unit test.
    # In the real implementation, it would be an instance of a KnowledgeBase class.
    try:
        user_docs = kb_retriever.search(topic)
        return {"user_docs": user_docs}
    except Exception as e:
        print(f"Error during KB retrieval: {e}")
        return {"error": "Failed to retrieve from knowledge base."}

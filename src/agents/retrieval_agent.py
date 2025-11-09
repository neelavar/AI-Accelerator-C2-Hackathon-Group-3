import asyncio
from openai import OpenAI
from src.state import ResearchState
from src.schemas import OptimizedQueries
from src.utils import _load_prompt_template

# Load the prompt template once when the module is loaded
RETRIEVAL_PROMPT_TEMPLATE = _load_prompt_template("retrieval_agent_pubmed_query_prompt.txt")

# Import real implementations from Dev 1's modules
from src.knowledge_base import KnowledgeBase
from src.services.external_apis import PubMedClient

def search_web(state: ResearchState, llm_client: OpenAI, pubmed_client: PubMedClient) -> dict:
    """
    Performs a web search using external APIs like PubMed.
    It first uses an LLM to optimize the user's topic into a search query.
    """
    # Validate inputs
    if not isinstance(llm_client, OpenAI):
        print("Error: Invalid OpenAI client provided")
        return {"error": "Invalid OpenAI client"}
    
    if not isinstance(pubmed_client, PubMedClient):
        print("Error: Invalid PubMed client provided") 
        return {"error": "Invalid PubMed client"}
        
    # Get and validate topic
    topic = state.get("topic")
    if not topic:
        print("Error: No research topic provided in state")
        return {"error": "No research topic provided"}
        
    if not isinstance(topic, str):
        print("Error: Research topic must be a string")
        return {"error": "Research topic must be a string"}
        
    if len(topic.strip()) == 0:
        print("Error: Research topic cannot be empty") 
        return {"error": "Research topic cannot be empty"}
            
    print(f"Web Retrieval Agent: Optimizing query for topic '{topic}'")
    
    # --- 1. Optimize Query using LLM ---
    try:
        prompt = RETRIEVAL_PROMPT_TEMPLATE.format(topic=topic)
    
        # Define the function schema for query optimization
        tools = [{
            "type": "function",
            "function": {
                "name": "optimize_queries",
                "description": "Optimize search queries for different platforms",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "pubmed_query": {
                            "type": "string",
                            "description": "Optimized search query for PubMed"
                        },
                        "google_scholar_queries": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of optimized queries for Google Scholar"
                        }
                    },
                    "required": ["pubmed_query"]
                }
            }
        }]

        # Call OpenAI API
        response = llm_client.chat.completions.create(
            model=state.get("fast_llm_model", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You are a search query optimization expert."},
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "optimize_queries"}}
        )
            
        # Extract the optimized query 
        tool_call = response.choices[0].message.tool_calls[0]
        import json
        query_result = json.loads(tool_call.function.arguments)
        optimized_query = query_result["pubmed_query"]
            
        if not optimized_query or len(optimized_query.strip()) == 0:
            print("Error: LLM returned empty query")
            return {"error": "Failed to generate search query"}
            
        print(f"Web Retrieval Agent: Optimized PubMed query: '{optimized_query}'")

        # --- 2. Call External API ---
        print("Web Retrieval Agent: Calling PubMed client with query.")
            
        # Create a new event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
            
        try:
            # Fetch PMIDs
            pmids = loop.run_until_complete(pubmed_client._fetch_pubmed_ids(optimized_query, retmax=10))
            if not pmids:
                print("No PubMed articles found for the query")
                return {"web_results": []}
                    
            # Fetch full article details
            web_docs = loop.run_until_complete(pubmed_client._fetch_article_details(pmids))
            if not web_docs:
                print("Failed to fetch article details")
                return {"error": "Failed to fetch article details"}
                
            print(f"Retrieved {len(web_docs)} articles from PubMed")
            return {"web_results": web_docs}
                
        except Exception as e:
            error_msg = f"PubMed API error: {str(e)}"
            print(error_msg)
            return {"error": error_msg}
            
        finally:
            loop.close()
                
    except Exception as e:
        error_msg = f"Error during web search: {str(e)}"
        print(error_msg)
        return {"error": error_msg}
    
    try:
        response = llm_client.chat.completions.create(
            model=state.get("fast_llm_model", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You are a search query optimization expert."},
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "optimize_queries"}}
        )
        
        # Extract the optimized query from the function call
        tool_call = response.choices[0].message.tool_calls[0]
        import json
        query_result = json.loads(tool_call.function.arguments)
        optimized_query = query_result["pubmed_query"]
        print(f"Web Retrieval Agent: Optimized PubMed query: '{optimized_query}'")

        # --- 2. Call External API ---
        print(f"Web Retrieval Agent: Calling PubMed client with query.")
        
        # Create a new event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Fetch PMIDs first
            pmids = loop.run_until_complete(pubmed_client._fetch_pubmed_ids(optimized_query, retmax=10))
            if not pmids:
                print("No PubMed articles found for the query")
                return {"web_results": []}
                
            # Fetch full article details
            web_docs = loop.run_until_complete(pubmed_client._fetch_article_details(pmids))
            print(f"Retrieved {len(web_docs)} articles from PubMed")
        finally:
            loop.close()
        
        return {"web_results": web_docs}

    except Exception as e:
        print(f"Error during web search: {e}")
        return {"error": f"Failed to perform web search: {str(e)}"}


def retrieve_from_kb(state: ResearchState, kb_retriever: KnowledgeBase) -> dict:
    """
    Retrieves relevant documents from the local knowledge base (ChromaDB).
    """
    try:
        topic = state.get("topic")
        if not topic:
            print("Error: No research topic provided in state")
            return {"error": "No research topic provided"}
        
        print(f"KB Retrieval Agent: Retrieving documents for topic '{topic}'")
        
        results = kb_retriever.query_documents(topic)
        if not results:
            print("No relevant documents found in knowledge base")
            return {"kb_results": []}
            
        return {"kb_results": results}
        
    except Exception as e:
        print(f"Error retrieving from knowledge base: {e}")
        return {"error": f"Failed to retrieve from knowledge base: {str(e)}"}

    try:
        # Use the KnowledgeBase search method to find relevant documents
        user_docs = kb_retriever.search(topic, k=5)  # Get top 5 most relevant documents
        print(f"Retrieved {len(user_docs)} documents from knowledge base")
        
        # Check if we found any documents
        if not user_docs:
            print("No relevant documents found in knowledge base")
            return {"user_docs": [], "warning": "No relevant documents found in knowledge base"}
            
        return {"user_docs": user_docs}
    except Exception as e:
        print(f"Error during KB retrieval: {e}")
        return {"error": f"Failed to retrieve from knowledge base: {str(e)}"}

"""
Query Validation Agent for MediScout.

Validates and refines user research queries for optimal results.
"""

from typing import Dict, Any
from loguru import logger

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from mediscout.config import get_settings
from mediscout.schemas import QueryValidation
from mediscout.state import ResearchState


VALIDATION_PROMPT = """You are a medical research query validator and optimizer.

Your task is to analyze the user's research query and:
1. Check if it's a valid medical research question
2. Refine it for better search results (fix spelling, expand abbreviations, add medical context)
3. Extract key medical terms
4. Provide suggestions if the query is unclear

Original query: {query}

Respond in JSON format:
{{
    "is_valid": true/false,
    "refined_query": "improved query text",
    "medical_terms": ["term1", "term2"],
    "suggestions": ["suggestion1 if needed"]
}}

Keep the refined query concise but specific. Extract important medical terms like drugs, diseases, procedures.
"""


class ValidateQueryAgent:
    """Agent for validating and refining research queries."""
    
    def __init__(self):
        """Initialize the validation agent."""
        self.settings = get_settings()
        
        # Initialize LLM with OpenRouter
        self.llm = ChatOpenAI(
            model=self.settings.openrouter_model,
            temperature=0.0,
            api_key=self.settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.prompt = ChatPromptTemplate.from_template(VALIDATION_PROMPT)
        self.parser = JsonOutputParser()
        
        self.chain = self.prompt | self.llm | self.parser
        
        logger.info("Query Validation Agent initialized")
    
    def __call__(self, state: ResearchState) -> Dict[str, Any]:
        """
        Validate and refine the research query.
        
        Args:
            state: Current research state
            
        Returns:
            Updated state with validation results
        """
        query = state["research_topic"]
        logger.info(f"Validating query: '{query}'")
        
        try:
            # Run validation chain
            result = self.chain.invoke({"query": query})
            
            validation = QueryValidation(
                is_valid=result.get("is_valid", True),
                refined_query=result.get("refined_query", query),
                medical_terms=result.get("medical_terms", []),
                suggestions=result.get("suggestions", [])
            )
            
            logger.info(f"Validation complete. Refined: '{validation.refined_query}'")
            
            return {
                "query_validation": validation,
                "refined_query": validation.refined_query,
                "current_stage": "query_validated"
            }
        
        except Exception as e:
            logger.error(f"Query validation failed: {e}")
            # Fallback: use original query
            return {
                "query_validation": QueryValidation(
                    is_valid=True,
                    refined_query=query,
                    medical_terms=[],
                    suggestions=[]
                ),
                "refined_query": query,
                "current_stage": "query_validated"
            }


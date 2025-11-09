"""
Contextual Retriever Agent for MediScout.

Retrieves relevant documents from multiple sources (knowledge base + PubMed).
"""

import time
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger

from mediscout.config import get_settings
from mediscout.knowledge_base import KnowledgeBase
from mediscout.services.pubmed_client import PubMedClient
from mediscout.schemas import Document, RetrievalResult
from mediscout.state import ResearchState


class RetrieverAgent:
    """Agent for multi-source document retrieval."""
    
    def __init__(self):
        """Initialize retriever with knowledge base and API clients."""
        self.settings = get_settings()
        self.knowledge_base = KnowledgeBase()
        self.pubmed_client = PubMedClient()
        
        logger.info("Retriever Agent initialized")
    
    def __call__(self, state: ResearchState) -> Dict[str, Any]:
        """
        Retrieve relevant documents from all sources.
        
        Args:
            state: Current research state
            
        Returns:
            Updated state with retrieved documents
        """
        query = state.get("refined_query") or state["research_topic"]
        logger.info(f"Retrieving documents for query: '{query}'")
        
        start_time = time.time()
        user_docs = []
        pubmed_docs = []
        sources_used = []
        
        try:
            # Retrieve from knowledge base
            logger.info("Searching local knowledge base...")
            user_docs = self.knowledge_base.search(
                query=query,
                top_k=self.settings.top_k_results // 2  # Split quota
            )
            if user_docs:
                sources_used.append("user")
                logger.info(f"Found {len(user_docs)} documents from knowledge base")
        
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
        
        try:
            # Retrieve from PubMed
            logger.info("Searching PubMed...")
            pubmed_docs = self.pubmed_client.search(
                query=query,
                max_results=self.settings.pubmed_max_results
            )
            if pubmed_docs:
                sources_used.append("pubmed")
                logger.info(f"Found {len(pubmed_docs)} documents from PubMed")
        
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
        
        # Combine and sort by relevance
        all_docs = self._combine_and_rank(user_docs, pubmed_docs)
        
        retrieval_time = time.time() - start_time
        
        # Create retrieval result
        retrieval_result = RetrievalResult(
            query=query,
            user_documents=user_docs,
            pubmed_documents=pubmed_docs,
            total_count=len(all_docs),
            sources_used=sources_used,
            retrieval_time_seconds=retrieval_time
        )
        
        logger.info(
            f"Retrieval complete: {len(all_docs)} total documents "
            f"from {len(sources_used)} sources in {retrieval_time:.2f}s"
        )
        
        return {
            "retrieval_result": retrieval_result,
            "retrieved_documents": all_docs,
            "current_stage": "documents_retrieved"
        }
    
    def _combine_and_rank(
        self,
        user_docs: List[Document],
        pubmed_docs: List[Document]
    ) -> List[Document]:
        """
        Combine documents from multiple sources and rank by relevance.
        
        Args:
            user_docs: Documents from knowledge base
            pubmed_docs: Documents from PubMed
            
        Returns:
            Combined and ranked list of documents
        """
        all_docs = user_docs + pubmed_docs
        
        # If we have relevance scores, sort by them
        if all_docs and all_docs[0].relevance_score is not None:
            all_docs.sort(key=lambda d: d.relevance_score or 0.0, reverse=True)
        
        # Limit to top_k
        all_docs = all_docs[:self.settings.top_k_results]
        
        logger.info(f"Ranked and limited to top {len(all_docs)} documents")
        return all_docs
    
    def ingest_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Ingest multiple documents into knowledge base.
        
        Args:
            file_paths: List of file paths to ingest
            
        Returns:
            Ingestion results
        """
        results = {
            "successful": [],
            "failed": [],
            "total_chunks": 0
        }
        
        for file_path in file_paths:
            try:
                chunks, doc_id = self.knowledge_base.ingest_document(Path(file_path))
                results["successful"].append({
                    "file": file_path,
                    "doc_id": doc_id,
                    "chunks": chunks
                })
                results["total_chunks"] += chunks
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                results["failed"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return results


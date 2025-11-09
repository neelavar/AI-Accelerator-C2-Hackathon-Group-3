"""
Streamlit callback handler for LangChain/LangGraph.

Provides real-time updates to Streamlit UI during agent execution.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks.base import BaseCallbackHandler
from loguru import logger
import streamlit as st


class StreamlitCallbackHandler(BaseCallbackHandler):
    """Callback handler that updates Streamlit UI with agent progress."""
    
    def __init__(self, status_container):
        """
        Initialize the callback handler.
        
        Args:
            status_container: Streamlit container for status updates
        """
        super().__init__()
        self.status_container = status_container
        self.current_step = ""
        self.step_count = 0
    
    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a chain starts."""
        chain_name = serialized.get("name", "Unknown")
        
        # Map internal names to user-friendly names
        step_names = {
            "ValidateQueryAgent": "🔍 Validating Research Query",
            "RetrieverAgent": "📚 Retrieving Relevant Documents",
            "CriticalAnalysisAgent": "🔬 Analyzing Medical Literature",
            "ReportBuilderAgent": "📝 Compiling Research Report",
        }
        
        self.current_step = step_names.get(chain_name, f"⚙️ {chain_name}")
        self.step_count += 1
        
        self._update_status()
        logger.info(f"Started: {self.current_step}")
    
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a chain ends."""
        logger.info(f"Completed: {self.current_step}")
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts."""
        self._update_status("🤖 Calling AI model...")
    
    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when LLM ends."""
        self._update_status("✅ AI response received")
    
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool starts."""
        tool_name = serialized.get("name", "tool")
        self._update_status(f"🔧 Using {tool_name}...")
    
    def on_agent_action(
        self,
        action: Any,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when an agent takes an action."""
        self._update_status(f"⚡ Agent action: {action.tool}")
    
    def on_text(
        self,
        text: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when arbitrary text is generated."""
        # Could display partial results here
        pass
    
    def on_error(
        self,
        error: Exception,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Called when an error occurs."""
        logger.error(f"Error in {self.current_step}: {error}")
        self._update_status(f"❌ Error: {str(error)[:100]}")
    
    def _update_status(self, detail: str = ""):
        """Update the Streamlit status display."""
        if self.status_container:
            with self.status_container:
                if detail:
                    st.write(f"**Step {self.step_count}:** {self.current_step}")
                    st.caption(detail)
                else:
                    st.write(f"**Step {self.step_count}:** {self.current_step}")


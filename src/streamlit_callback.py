import streamlit as st
from typing import Any, Dict, List
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class StreamlitCallbackHandler(BaseCallbackHandler):
    """
    A custom callback handler that writes agent activity to a Streamlit container.
    """

    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print the name of the chain that is starting."""
        self.container.write(f"**Running:** {serialized.get('name')}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Do nothing when an LLM ends."""
        pass

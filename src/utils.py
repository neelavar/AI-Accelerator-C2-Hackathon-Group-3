"""
Utility functions for the MediScout application.
"""
import os

def _load_prompt_template(template_name: str) -> str:
    """
    Loads a prompt template from the src/prompts directory.
    """
    current_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(current_dir, "prompts", template_name)
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

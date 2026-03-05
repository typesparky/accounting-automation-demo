from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.domain.models import AgentContext

class BaseSubagent(ABC):
    """
    Abstract base class for all specialized subagents in the workflow.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def execute(self, context: AgentContext) -> AgentContext:
        """
        Execute the agent's logic on the given context.
        Returns the updated context.
        
        Subclasses should handle their own error logging and state updates
        (e.g., setting the context status to FAILED or NEEDS_REVIEW on error).
        """
        pass
        
    def get_structured_prompt(self, additional_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Utility method to generate prompts if the agent is LLM-backed.
        Can be overridden by subclasses.
        """
        params = additional_params or {}
        # Simple default template
        return f"You are {self.name}. {self.description}\nParams: {params}"

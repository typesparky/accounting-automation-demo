import logging
from typing import List
from src.domain.models import AgentContext, WorkflowStatus
from src.agents.base import BaseSubagent

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """
    Manages the execution of a workflow across multiple subagents.
    """
    def __init__(self, agents: List[BaseSubagent]):
        self.agents = agents
        
    def run_workflow(self, context: AgentContext) -> AgentContext:
        """
        Run the context sequentially through the defined agents.
        Stops if an agent sets the status to FAILED or NEEDS_REVIEW.
        """
        context.current_status = WorkflowStatus.IN_PROGRESS
        context.add_log("Workflow started.")
        
        for agent in self.agents:
            context.add_log(f"Passing context to agent: {agent.name}")
            try:
                context = agent.execute(context)
            except Exception as e:
                logger.error(f"Agent {agent.name} failed with error: {e}")
                context.current_status = WorkflowStatus.FAILED
                context.add_log(f"Workflow failed at {agent.name}: {str(e)}")
                return context

            # Check if workflow should halt
            if context.current_status in [WorkflowStatus.FAILED, WorkflowStatus.NEEDS_REVIEW]:
                context.add_log(f"Workflow halted with status: {context.current_status.value}")
                return context
                
        context.current_status = WorkflowStatus.COMPLETED
        context.add_log("Workflow completed successfully.")
        return context

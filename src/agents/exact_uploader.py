from src.agents.base import BaseSubagent
from src.domain.models import AgentContext, WorkflowStatus
from src.domain.interfaces import AccountingPlatformConnector

class ExactUploaderAgent(BaseSubagent):
    """
    Subagent responsible for pushing validated invoice data 
    directly into Exact Online, bypassing manual Blue10 steps.
    """
    
    def __init__(self, connector: AccountingPlatformConnector):
        super().__init__("ExactUploader", "Uploads and posts invoice entries directly to Exact Online.")
        self.connector = connector

    def execute(self, context: AgentContext) -> AgentContext:
        context.add_log("Starting ExactUploaderAgent execution...")
        
        if not self.connector.authenticate():
            context.current_status = WorkflowStatus.FAILED
            context.add_log("Exact authentication failed.")
            return context

        if not context.collected_data.invoice:
            context.current_status = WorkflowStatus.NEEDS_REVIEW
            context.add_log("No validated invoice data found in context. Approval required.")
            return context

        # Post to Exact
        exact_id = self.connector.submit_invoice(context.collected_data)
        context.metadata["exact_id"] = exact_id
        
        context.current_status = WorkflowStatus.COMPLETED
        context.add_log(f"Invoice posted successfully to Exact. entry_id: {exact_id}")
        
        return context

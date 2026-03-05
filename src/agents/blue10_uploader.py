from src.agents.base import BaseSubagent
from src.domain.models import AgentContext, WorkflowStatus
from src.infrastructure.blue10_connector_v2 import Blue10ConnectorV2

class Blue10UploaderAgent(BaseSubagent):
    """
    Subagent responsible for uploading documents to Blue10 
    and ensuring they are correctly classified.
    """
    
    def __init__(self, connector: Blue10ConnectorV2):
        super().__init__("Blue10Uploader", "Uploads and classifies documents in Blue10.")
        self.connector = connector

    def execute(self, context: AgentContext) -> AgentContext:
        context.add_log("Starting Blue10UploaderAgent execution...")
        
        if not self.connector.authenticate():
            context.current_status = WorkflowStatus.FAILED
            context.add_log("Blue10-V2 authentication failed.")
            return context

        if not context.collected_data.email_invoice:
            context.current_status = WorkflowStatus.NEEDS_REVIEW
            context.add_log("No email invoice data found in context.")
            return context

        blue10_id = self.connector.submit_invoice(context.collected_data)
        context.metadata["blue10_id"] = blue10_id
        
        context.current_status = WorkflowStatus.COMPLETED
        context.add_log(f"Document uploaded to Blue10. Remote ID: {blue10_id}")
        
        return context

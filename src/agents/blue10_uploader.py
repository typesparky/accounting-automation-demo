from src.agents.base import BaseSubagent
from src.domain.models import AgentContext, WorkflowStatus
from src.infrastructure.blue10_connector_v2 import Blue10ConnectorV2
from src.infrastructure.knowledge_base import KnowledgeBase

class Blue10UploaderAgent(BaseSubagent):
    """
    Subagent responsible for uploading documents to Blue10 
    and ensuring they are correctly classified.
    """
    
    def __init__(self, connector: Blue10ConnectorV2, kb: KnowledgeBase):
        super().__init__("Blue10Uploader", "Uploads and classifies documents in Blue10.")
        self.connector = connector
        self.kb = kb

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

        # Retrieve template from Knowledge Base
        brand = context.collected_data.email_invoice.brand
        template = self.kb.get_template_for_brand(brand)
        if template:
            context.add_log(f"Applying bookkeeping template for {brand}")
        
        blue10_id = self.connector.submit_invoice(context.collected_data, template=template)
        context.metadata["blue10_id"] = blue10_id
        
        context.current_status = WorkflowStatus.COMPLETED
        context.add_log(f"Document uploaded to Blue10. Remote ID: {blue10_id}")
        
        return context

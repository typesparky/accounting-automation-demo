from src.agents.base import BaseSubagent
from src.domain.models import AgentContext, WorkflowStatus
from src.domain.interfaces import AccountingPlatformConnector

class DataEntryAgent(BaseSubagent):
    """
    Subagent responsible for pushing extracted data into an accounting platform.
    """
    def __init__(self, connector: AccountingPlatformConnector):
        super().__init__(
            name="DataEntryAgent", 
            description="Pushes structured data into the accounting target platform."
        )
        self.connector = connector
        
    def execute(self, context: AgentContext) -> AgentContext:
        context.add_log(f"Starting execution for {self.name}...")
        
        if not context.collected_data or not context.collected_data.invoice:
            context.add_log("No extracted data found to enter.")
            context.current_status = WorkflowStatus.FAILED
            return context
            
        try:
            self.connector.authenticate()
            
            # Additional validation loop: check vendor
            invoice = context.collected_data.invoice
            if invoice.vendor_vat and not self.connector.check_vendor_exists(invoice.vendor_vat):
                context.add_log(f"Vendor VAT {invoice.vendor_vat} not found. Needs manual review.")
                context.current_status = WorkflowStatus.NEEDS_REVIEW
                return context
                
            remote_id = self.connector.submit_invoice(context.collected_data)
            context.metadata["target_system_id"] = remote_id
            context.add_log(f"Successfully entered data. Remote ID: {remote_id}")
            
        except Exception as e:
            context.add_log(f"Failed data entry: {str(e)}")
            context.current_status = WorkflowStatus.FAILED
            
        return context

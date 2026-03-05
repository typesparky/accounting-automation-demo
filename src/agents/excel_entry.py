from typing import Any, Dict
from src.agents.base import BaseSubagent
from src.domain.models import AgentContext, WorkflowStatus
from src.domain.interfaces import SpreadsheetConnector

class ExcelDataEntryAgent(BaseSubagent):
    """
    Subagent responsible for mapping extracted data into an Excel spreadsheet.
    """
    def __init__(self, connector: SpreadsheetConnector):
        super().__init__(
            name="ExcelDataEntryAgent", 
            description="Appends structured data securely into an Excel spreadsheet."
        )
        self.connector = connector
        
    def execute(self, context: AgentContext) -> AgentContext:
        context.add_log(f"Starting execution for {self.name}...")
        
        if not context.collected_data or not context.collected_data.invoice:
            context.add_log("No extracted data found to enter.")
            context.current_status = WorkflowStatus.FAILED
            return context
            
        try:
            # Map standard InvoiceData model to a flat dictionary for Excel row addition
            invoice = context.collected_data.invoice
            
            row_data: Dict[str, Any] = {
                "Invoice Number": invoice.invoice_number,
                "Vendor Date": invoice.date.isoformat() if invoice.date else "Unknown",
                "Vendor Name": invoice.vendor_name,
                "Vendor VAT": invoice.vendor_vat,
                "Total Amount": invoice.total_amount,
                "Currency": invoice.currency,
                "Confidence Score": invoice.confidence_score
            }
            
            # Use connector to append safely
            success = self.connector.append_row(row_data)
            if success:
                context.add_log(f"Successfully appended row for Invoice {invoice.invoice_number} to Excel.")
            else:
                context.add_log("Failed to append row to Excel.")
                context.current_status = WorkflowStatus.FAILED
                
        except Exception as e:
            context.add_log(f"Failed data entry to Excel: {str(e)}")
            context.current_status = WorkflowStatus.FAILED
            
        return context

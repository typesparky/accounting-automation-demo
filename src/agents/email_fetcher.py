from typing import List, Dict, Any
from src.agents.base import BaseSubagent
from src.domain.models import AgentContext, ExtractedData, EmailInvoice, Brand, WorkflowStatus
from src.infrastructure.outlook_connector import OutlookConnector

class EmailFetcherAgent(BaseSubagent):
    """
    Subagent responsible for connecting to Outlook, 
    fetching invoice emails, and preparing them for processing.
    """
    
    def __init__(self, connector: OutlookConnector):
        super().__init__("EmailFetcher", "Fetches invoice attachments from Outlook.")
        self.connector = connector

    def execute(self, context: AgentContext) -> AgentContext:
        context.add_log("Starting EmailFetcherAgent execution...")
        
        if not self.connector.authenticate():
            context.current_status = WorkflowStatus.FAILED
            context.add_log("Outlook authentication failed.")
            return context
            
        emails = self.connector.fetch_emails(filter_query="hasAttachments eq true")
        context.add_log(f"Fetched {len(emails)} emails.")
        
        # In this simplified demo, we'll process the first email found
        if not emails:
            context.add_log("No pending invoice emails found.")
            return context

        email = emails[0]
        # Perform brand classification (Simplified mapping for demo)
        brand = Brand.UNKNOWN
        if "Brand A" in email["subject"] or "vendor-a" in email["sender"]["emailAddress"]["address"]:
            brand = Brand.BRAND_A
        elif "Brand B" in email["subject"] or "vendor-b" in email["sender"]["emailAddress"]["address"]:
            brand = Brand.BRAND_B
        
        attachment = email["attachments"][0]
        local_path = f"/tmp/accounting_workflow/invoices/{attachment['name']}"
        
        self.connector.download_attachment(email["id"], attachment["id"], local_path)
        
        # Populate context with email invoice data
        context.collected_data = ExtractedData(
            source_type="email_invoice",
            email_invoice=EmailInvoice(
                message_id=email["id"],
                sender=email["sender"]["emailAddress"]["address"],
                subject=email["subject"],
                received_at=email["receivedDateTime"],
                attachment_name=attachment["name"],
                brand=brand,
                local_path=local_path
            )
        )
        
        context.add_log(f"Email processed. Brand identified: {brand}")
        return context

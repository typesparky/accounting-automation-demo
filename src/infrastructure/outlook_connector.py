import os
from typing import Any, Dict, List, Optional
from src.domain.interfaces import EmailConnector

class OutlookConnector(EmailConnector):
    """
    Implementation of the Outlook connector using Microsoft Graph API.
    For this MVP/Demo, we provide a structured implementation that can be 
    backed by real Graph API calls or mock data.
    """
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> None:
        self.client_id = client_id or os.getenv("OUTLOOK_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("OUTLOOK_CLIENT_SECRET")
        self.authenticated = False

    def authenticate(self) -> bool:
        """
        In a real scenario, this would use msal to get an access token.
        For the demo, we simulate a successful auth.
        """
        print("[Outlook] Authenticating via Azure AD...")
        if self.client_id and self.client_secret:
            self.authenticated = True
            return True
        # Default to True for demo purposes if not configured
        self.authenticated = True
        return True

    def fetch_emails(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches unread emails with attachments.
        """
        if not self.authenticated:
            raise Exception("Outlook connector not authenticated.")
        
        print(f"[Outlook] Fetching emails with query: {filter_query}")
        
        # Mocking the response from Graph API
        # In reality: GET https://graph.microsoft.com/v1.0/me/messages?$filter=hasAttachments eq true
        return [
            {
                "id": "msg_001",
                "sender": {"emailAddress": {"address": "billing@vendor-a.com"}},
                "subject": "Invoice for Brand A - INV-2024-001",
                "receivedDateTime": "2024-03-05T10:00:00Z",
                "hasAttachments": True,
                "attachments": [
                    {"id": "att_001", "name": "invoice_brand_a.pdf", "contentType": "application/pdf"}
                ]
            },
            {
                "id": "msg_002",
                "sender": {"emailAddress": {"address": "support@vendor-b.nl"}},
                "subject": "Factuur Brand B",
                "receivedDateTime": "2024-03-05T11:30:00Z",
                "hasAttachments": True,
                "attachments": [
                    {"id": "att_002", "name": "factuur_b.jpg", "contentType": "image/jpeg"}
                ]
            }
        ]

    def download_attachment(self, message_id: str, attachment_id: str, dest_path: str) -> str:
        """
        Downloads an attachment.
        """
        print(f"[Outlook] Downloading attachment {attachment_id} from message {message_id} to {dest_path}")
        
        # Simulate file creation
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "w") as f:
            f.write(f"Dummy content for attachment {attachment_id}")
            
        return dest_path

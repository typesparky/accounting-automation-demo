from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from .models import AgentContext, ExtractedData, Brand

class AccountingPlatformConnector(ABC):
    """Interface for connecting to Exact, Blue10, etc."""
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform."""
        pass
        
    @abstractmethod
    def submit_invoice(self, data: ExtractedData) -> str:
        """Submit invoice data to the platform. Returns remote ID."""
        pass
        
    @abstractmethod
    def check_vendor_exists(self, vendor_vat: str) -> bool:
        """Check if a vendor exists in the target system."""
        pass

class EmailConnector(ABC):
    """Interface for connecting to Outlook/Gmail APIs."""
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the email provider."""
        pass
        
    @abstractmethod
    def fetch_emails(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch emails based on a query."""
        pass
        
    @abstractmethod
    def download_attachment(self, message_id: str, attachment_id: str, dest_path: str) -> str:
        """Download an attachment to a local path. Returns path."""
        pass

class DocumentProcessor(ABC):
    """Interface for processing documents (OCR, PDF extraction)."""
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract raw text from a document."""
        pass
        
    @abstractmethod
    def parse_invoice(self, file_path: str) -> ExtractedData:
        """Extract structured data from an invoice."""
        pass

class StorageProvider(ABC):
    """Interface for retrieving rules, state, and knowledge base."""
    
    @abstractmethod
    def get_workflow_state(self, workflow_id: str) -> AgentContext:
        """Retrieve the state of a workflow."""
        pass
        
    @abstractmethod
    def save_workflow_state(self, context: AgentContext) -> None:
        """Persist the workflow state."""
        pass
        
    @abstractmethod
    def get_accounting_rules(self, category: str) -> List[Dict[str, Any]]:
        """Retrieve business rules for a specific category."""
        pass

class SpreadsheetConnector(ABC):
    """Interface for connecting to Excel/CSV spreadsheets securely."""
    
    @abstractmethod
    def load_spreadsheet(self) -> bool:
        """Load the spreadsheet into memory, validating access."""
        pass
        
    @abstractmethod
    def append_row(self, data: Dict[str, Any]) -> bool:
        """Append a new row to the spreadsheet securely."""
        pass
        
    @abstractmethod
    def backup_file(self) -> str:
        """Create a backup of the spreadsheet before modifying."""
        pass

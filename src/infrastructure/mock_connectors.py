import uuid
from typing import Any, Dict
from src.domain.interfaces import AccountingPlatformConnector
from src.domain.models import ExtractedData

class MockExactConnector(AccountingPlatformConnector):
    """
    Mock implementation of the Exact connector for testing.
    """
    def __init__(self) -> None:
        self.mock_db: Dict[str, Any] = {}
        self.authenticated = False

    def authenticate(self) -> bool:
        print("[MockExact] Authenticating...")
        self.authenticated = True
        return True

    def submit_invoice(self, data: ExtractedData) -> str:
        if not self.authenticated:
            raise Exception("Not authenticated with MockExact")
        
        entry_id = str(uuid.uuid4())
        self.mock_db[entry_id] = data.dict()
        print(f"[MockExact] Submitted invoice. Remote ID: {entry_id}")
        return entry_id

    def check_vendor_exists(self, vendor_vat: str) -> bool:
        if not self.authenticated:
            raise Exception("Not authenticated with MockExact")
        
        # Mock logic: exists if VAT starts with 'NL'
        exists = vendor_vat.startswith("NL")
        status = "Exists" if exists else "Not Found"
        print(f"[MockExact] Checking vendor VAT {vendor_vat}: {status}")
        return exists

class MockBlue10Connector(AccountingPlatformConnector):
    """
    Mock implementation of the Blue10 connector for testing.
    """
    def __init__(self) -> None:
        self.authenticated = False

    def authenticate(self) -> bool:
        print("[MockBlue10] Authenticating...")
        self.authenticated = True
        return True

    def submit_invoice(self, data: ExtractedData) -> str:
        if not self.authenticated:
            raise Exception("Not authenticated with MockBlue10")
        
        entry_id = str(uuid.uuid4())
        print(f"[MockBlue10] Submitted to queue. Remote ID: {entry_id}")
        return entry_id

    def check_vendor_exists(self, vendor_vat: str) -> bool:
        return True  # Always true for simple mock

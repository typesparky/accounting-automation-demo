from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class Brand(str, Enum):
    BRAND_A = "Brand A"
    BRAND_B = "Brand B"
    BRAND_C = "Brand C"
    UNKNOWN = "Unknown"

class InvoiceData(BaseModel):
    """Extracted data from an invoice."""
    invoice_number: Optional[str] = None
    date: Optional[datetime] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = Field(default="EUR")
    vendor_name: Optional[str] = None
    vendor_vat: Optional[str] = None
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, description="Overall confidence of the extraction")

class EmailInvoice(BaseModel):
    """Metadata for an invoice captured from an email."""
    message_id: str
    sender: str
    subject: str
    received_at: datetime
    attachment_name: str
    brand: Brand = Field(default=Brand.UNKNOWN)
    local_path: Optional[str] = None

class ExtractedData(BaseModel):
    """Generic payload for data extracted by agents."""
    source_type: str  # e.g., 'invoice', 'receipt', 'bank_statement', 'email'
    raw_text: Optional[str] = None
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    invoice: Optional[InvoiceData] = None
    email_invoice: Optional[EmailInvoice] = None

class AgentContext(BaseModel):
    """Context passed between agents during a workflow."""
    workflow_id: str
    current_status: WorkflowStatus = Field(default=WorkflowStatus.PENDING)
    collected_data: ExtractedData
    metadata: Dict[str, Any] = Field(default_factory=dict)
    history: List[str] = Field(default_factory=list)

    def add_log(self, message: str) -> None:
        self.history.append(f"[{datetime.now().isoformat()}] {message}")

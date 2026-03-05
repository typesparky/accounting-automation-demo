import os
from src.domain.interfaces import DocumentProcessor
from src.domain.models import ExtractedData, InvoiceData

class LocalDocumentProcessor(DocumentProcessor):
    """
    Stub implementation for local Python-based OCR/extraction
    """
    def extract_text(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
        print(f"[LocalDocumentProcessor] Extracting text from {file_path}")
        return "MOCK_TEXT_CONTENT_FROM_PDF"

    def parse_invoice(self, file_path: str) -> ExtractedData:
        print(f"[LocalDocumentProcessor] Parsing invoice from {file_path}")
        
        # Mock structured data
        invoice_data = InvoiceData(
            invoice_number="INV-2026-001",
            total_amount=150.75,
            currency="EUR",
            vendor_name="Mock Vendor B.V.",
            vendor_vat="NL123456789B01",
            confidence_score=0.95
        )
        
        return ExtractedData(
            source_type="invoice_pdf",
            raw_text="MOCK_TEXT",
            structured_data={"file_size": 1024},
            invoice=invoice_data
        )

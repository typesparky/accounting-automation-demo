import pytest
from src.infrastructure.blue10_connector_v2 import Blue10ConnectorV2
from src.domain.models import ExtractedData, EmailInvoice, Brand
from datetime import datetime

def test_blue10_connector_auth():
    connector = Blue10ConnectorV2(api_key="test-key")
    assert connector.authenticate() is True

def test_blue10_connector_upload_classification():
    connector = Blue10ConnectorV2(api_key="test-key")
    connector.authenticate()
    
    data = ExtractedData(
        source_type="email",
        email_invoice=EmailInvoice(
            message_id="msg1",
            sender="billing@vendor-a.com",
            subject="Invoice",
            received_at=datetime.now(),
            attachment_name="inv.pdf",
            brand=Brand.BRAND_A
        )
    )
    
    doc_id = connector.submit_invoice(data)
    assert doc_id is not None
    # In our mock, Brand A maps to COMP-001-A
    # We can check logs if we want, but for now we verify it doesn't crash

import os
import uuid
import pytest
import pandas as pd
from typing import Any
from datetime import datetime

from src.infrastructure.excel_connector import PandasExcelConnector
from src.agents.excel_entry import ExcelDataEntryAgent
from src.domain.models import AgentContext, ExtractedData, InvoiceData, WorkflowStatus

@pytest.fixture
def temp_excel_file(tmp_path: Any) -> Any:
    """Provides a temporary Excel file path for testing."""
    file_path = os.path.join(tmp_path, "test_accounting.xlsx")
    yield file_path
    pass # No need for explicit cleanup; tmp_path handles it

def test_excel_connector_append_and_backup(temp_excel_file: Any) -> None:
    connector = PandasExcelConnector(file_path=temp_excel_file)
    
    # 1. Test append (creates file since it doesn't exist)
    data1 = {"Invoice Number": "INV-001", "Total Amount": 100.0}
    assert connector.append_row(data1) is True
    
    # Verify it was written correctly
    df1 = pd.read_excel(temp_excel_file)
    assert len(df1) == 1
    assert df1.iloc[0]["Invoice Number"] == "INV-001"
    
    # 2. Test append to existing file (should create a backup)
    data2 = {"Invoice Number": "INV-002", "Total Amount": 250.0}
    assert connector.append_row(data2) is True
    
    # Verify new row
    df2 = pd.read_excel(temp_excel_file)
    assert len(df2) == 2
    assert df2.iloc[1]["Invoice Number"] == "INV-002"
    
    # Verify backup was created
    dir_name = os.path.dirname(temp_excel_file)
    backups = [f for f in os.listdir(dir_name) if "backup" in f]
    assert len(backups) >= 1

def test_excel_agent_execution(temp_excel_file: Any) -> None:
    connector = PandasExcelConnector(file_path=temp_excel_file)
    agent = ExcelDataEntryAgent(connector=connector)
    
    # Setup Context
    invoice = InvoiceData(
        invoice_number="INV-2026-999",
        vendor_name="Test Vendor",
        total_amount=55.55,
        currency="USD"
    )
    extracted = ExtractedData(source_type="test", invoice=invoice)
    context = AgentContext(workflow_id=str(uuid.uuid4()), collected_data=extracted)
    
    # Execute
    result_context = agent.execute(context)
    
    # Assert Context updated successfully
    assert result_context.current_status != WorkflowStatus.FAILED
    assert "Successfully appended row" in result_context.history[-1]
    
    # Assert Excel updated correctly
    df = pd.read_excel(temp_excel_file)
    assert len(df) == 1
    assert df.iloc[0]["Invoice Number"] == "INV-2026-999"
    assert df.iloc[0]["Vendor Name"] == "Test Vendor"
    assert df.iloc[0]["Total Amount"] == 55.55
    assert df.iloc[0]["Currency"] == "USD"

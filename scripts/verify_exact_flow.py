import os
import sys

# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestration.email_to_exact_workflow import EmailToExactWorkflow
from src.domain.models import WorkflowStatus, InvoiceData, AgentContext, ExtractedData
import uuid

def run_verification():
    print("--- Starting Email-to-Exact Workflow Verification ---")
    
    # 1. Initialize
    workflow = EmailToExactWorkflow(
        outlook_client_id="demo-id",
        outlook_client_secret="demo-secret"
    )
    
    # 2. Simulate Fetch (Initial Step)
    print("Step 1: Fetching (Simulated)...")
    context = workflow.run()
    
    print(f"Status after Fetch: {context.current_status}")
    if context.current_status == WorkflowStatus.NEEDS_REVIEW:
        print("SUCCESS: Workflow paused for Dashboard Validation.")
    
    # 3. Simulate Dashboard Approval (Approving and Posting)
    print("\nStep 2: Simulating Dashboard Approval...")
    
    # Mock validated data (as if a human edited it in Streamlit)
    invoice_data = InvoiceData(
        invoice_number="VERIFY-999",
        vendor_name="Verified Vendor",
        date="2024-05-15",
        total_amount=500.00,
        currency="EUR",
        vat_amount=105.0,
        vat_number="NL00112233",
        line_items=[]
    )
    context.collected_data.invoice = invoice_data
    
    # Resume workflow
    result_context = workflow.approve_and_post(context)
    
    print("\n--- Workflow Results ---")
    print(f"Final Status: {result_context.current_status}")
    print(f"Exact ID: {result_context.metadata.get('exact_id')}")
    
    if result_context.current_status == WorkflowStatus.COMPLETED:
        print("SUCCESS: Workflow reached completion through direct Exact posting.")
    else:
        print(f"FAILURE: Workflow ended with status {result_context.current_status}")

    print("\n--- Execution Logs ---")
    for log in result_context.history:
        print(log)

if __name__ == "__main__":
    run_verification()

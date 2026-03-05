import os
import sys

# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestration.email_to_blue10_workflow import EmailToBlue10Workflow
from src.domain.models import WorkflowStatus

def run_verification():
    print("--- Starting Email-to-Blue10 Workflow Verification ---")
    
    # Initialize the workflow with dummy credentials
    workflow = EmailToBlue10Workflow(
        outlook_client_id="demo-client-id",
        outlook_client_secret="demo-client-secret",
        blue10_api_key="demo-blue10-key"
    )
    
    # Run the full pipeline
    print("Executing workflow...")
    result_context = workflow.run()
    
    print("\n--- Workflow Results ---")
    print(f"Workflow ID: {result_context.workflow_id}")
    print(f"Status: {result_context.current_status}")
    
    if result_context.current_status == WorkflowStatus.COMPLETED:
        print("SUCCESS: Workflow reached completion.")
    else:
        print(f"FAILURE: Workflow ended with status {result_context.current_status}")
        
    print("\n--- Processed Data ---")
    if result_context.collected_data.email_invoice:
        email_data = result_context.collected_data.email_invoice
        print(f"Brand Identified: {email_data.brand}")
        print(f"Sender: {email_data.sender}")
        print(f"Subject: {email_data.subject}")
        print(f"Local Path: {email_data.local_path}")
    
    print(f"Blue10 Remote ID: {result_context.metadata.get('blue10_id')}")
    
    print("\n--- Full Execution Logs ---")
    for log in result_context.history:
        print(log)

if __name__ == "__main__":
    run_verification()

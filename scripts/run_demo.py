import sys
import os

# Add the project directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
from src.domain.models import AgentContext, WorkflowStatus, ExtractedData
from src.infrastructure.mock_connectors import MockExactConnector, MockBlue10Connector
from src.infrastructure.local_document_processor import LocalDocumentProcessor
from src.agents.extraction import DocumentExtractionAgent
from src.agents.entry import DataEntryAgent
from src.agents.excel_entry import ExcelDataEntryAgent
from src.infrastructure.excel_connector import PandasExcelConnector
from src.orchestration.workflow_engine import WorkflowOrchestrator

def run_demo():
    print("="*50)
    print("Starting Accounting Workflow Automation Demo")
    print("="*50)
    
    # Setup dependencies
    processor = LocalDocumentProcessor()
    
    # Target systems
    exact_connector = MockExactConnector()
    
    # Create an output Excel file in the current directory
    excel_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'demo_output.xlsx'))
    excel_connector = PandasExcelConnector(file_path=excel_file_path)
    
    # Setup agents
    extraction_agent = DocumentExtractionAgent(processor=processor)
    entry_agent_exact = DataEntryAgent(connector=exact_connector)
    entry_agent_excel = ExcelDataEntryAgent(connector=excel_connector)
    
    # Setup workflow
    orchestrator = WorkflowOrchestrator(agents=[extraction_agent, entry_agent_exact, entry_agent_excel])
    
    # Initialize state context
    initial_data = ExtractedData(source_type="file")
    context = AgentContext(
        workflow_id=str(uuid.uuid4()),
        collected_data=initial_data,
        metadata={"file_path": "sample_invoice.pdf"}
    )
    
    print(f"\n[Flow Started] Workflow ID: {context.workflow_id}")
    
    # Run
    final_context = orchestrator.run_workflow(context)
    
    print("\n" + "="*50)
    print("Workflow Execution Log:")
    print("="*50)
    for i, log_entry in enumerate(final_context.history):
        print(f"{i+1}. {log_entry}")
        
    print("\n" + "="*50)
    print(f"Final Status: {final_context.current_status.value}")
    if "target_system_id" in final_context.metadata:
        print(f"Target System ID: {final_context.metadata['target_system_id']}")
    print("="*50)

if __name__ == "__main__":
    run_demo()

from src.orchestration.workflow_engine import WorkflowOrchestrator
from src.infrastructure.outlook_connector import OutlookConnector
from src.infrastructure.mock_connectors import MockExactConnector
from src.agents.email_fetcher import EmailFetcherAgent
from src.agents.exact_uploader import ExactUploaderAgent
from src.domain.models import AgentContext, WorkflowStatus

class EmailToExactWorkflow:
    """
    Workflow for fetching emails and posting directly to Exact Online.
    Includes a 'NEEDS_REVIEW' step for dashboard validation.
    """
    
    def __init__(self, outlook_client_id=None, outlook_client_secret=None):
        self.outlook_connector = OutlookConnector(outlook_client_id, outlook_client_secret)
        self.exact_connector = MockExactConnector() # Use actual connector in production
        
        self.fetcher_agent = EmailFetcherAgent(self.outlook_connector)
        self.uploader_agent = ExactUploaderAgent(self.exact_connector)
        
        # Sequentially run fetcher, then uploader
        self.orchestrator = WorkflowOrchestrator([
            self.fetcher_agent,
            self.uploader_agent
        ])

    def run(self, context=None):
        if context is None:
            import uuid
            from src.domain.models import ExtractedData
            context = AgentContext(
                workflow_id=f"exact-flow-{uuid.uuid4()}",
                collected_data=ExtractedData(source_type="email")
            )
        
        # 1. Fetch
        context = self.fetcher_agent.execute(context)
        if context.current_status == WorkflowStatus.FAILED:
            return context
            
        # 2. Manual/Dashboard Validation Point
        # In this direct flow, we stop for human approval in the Streamlit Dashboard
        # The dashboard will then resume by calling the uploader_agent
        context.add_log("Workflow paused for Dashboard Validation.")
        context.current_status = WorkflowStatus.NEEDS_REVIEW
        
        return context

    def approve_and_post(self, context):
        """
        Called by the Dashboard after the human has reviewed/edited the data.
        """
        context.current_status = WorkflowStatus.IN_PROGRESS
        return self.uploader_agent.execute(context)

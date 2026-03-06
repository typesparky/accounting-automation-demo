import uuid
from src.domain.models import AgentContext, ExtractedData, WorkflowStatus
from src.orchestration.workflow_engine import WorkflowOrchestrator
from src.infrastructure.outlook_connector import OutlookConnector
from src.infrastructure.blue10_connector_v2 import Blue10ConnectorV2
from src.infrastructure.knowledge_base import KnowledgeBase
from src.agents.email_fetcher import EmailFetcherAgent
from src.agents.blue10_uploader import Blue10UploaderAgent

class EmailToBlue10Workflow:
    """
    Specific workflow orchestration for the Outlook-to-Blue10 pipeline.
    """
    
    def __init__(self, outlook_client_id=None, outlook_client_secret=None, blue10_api_key=None, kb_path=None):
        # Initialize connectors and KB
        self.outlook_connector = OutlookConnector(outlook_client_id, outlook_client_secret)
        self.blue10_connector = Blue10ConnectorV2(blue10_api_key)
        self.kb = KnowledgeBase(kb_path)
        
        # Initialize agents
        self.fetcher_agent = EmailFetcherAgent(self.outlook_connector)
        self.uploader_agent = Blue10UploaderAgent(self.blue10_connector, self.kb)
        
        # Initialize general orchestrator
        self.orchestrator = WorkflowOrchestrator([
            self.fetcher_agent,
            self.uploader_agent
        ])

    def run(self) -> AgentContext:
        """
        Executes the full pipeline for any pending emails.
        """
        # Create initial context
        context = AgentContext(
            workflow_id=f"email-flow-{uuid.uuid4()}",
            collected_data=ExtractedData(source_type="email_init")
        )
        
        # Run the workflow
        return self.orchestrator.run_workflow(context)

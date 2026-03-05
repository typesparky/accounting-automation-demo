from src.agents.base import BaseSubagent
from src.domain.models import AgentContext, WorkflowStatus
from src.domain.interfaces import DocumentProcessor

class DocumentExtractionAgent(BaseSubagent):
    """
    Subagent responsible for extracting data from documents using an OCR processor.
    """
    def __init__(self, processor: DocumentProcessor):
        super().__init__(
            name="DocumentExtractionAgent", 
            description="Extracts structured invoice data from PDFs using OCR."
        )
        self.processor = processor
        
    def execute(self, context: AgentContext) -> AgentContext:
        context.add_log(f"Starting execution for {self.name}...")
        try:
            # Assuming metadata has 'file_path'
            file_path = context.metadata.get("file_path", "dummy.pdf")
            extracted_data = self.processor.parse_invoice(file_path)
            
            # Store the result in the context
            context.collected_data = extracted_data
            context.add_log("Successfully extracted document data.")
            
        except Exception as e:
            context.add_log(f"Failed extraction: {str(e)}")
            context.current_status = WorkflowStatus.FAILED
            
        return context

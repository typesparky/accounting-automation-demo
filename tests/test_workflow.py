from src.domain.models import AgentContext, WorkflowStatus, ExtractedData
from src.agents.base import BaseSubagent
from src.orchestration.workflow_engine import WorkflowOrchestrator

class DummyAgentPass(BaseSubagent):
    def __init__(self) -> None:
        super().__init__("DummyPass", "Passes the context unchanged.")
    
    def execute(self, context: AgentContext) -> AgentContext:
        context.add_log("DummyPass executed.")
        return context

class DummyAgentFail(BaseSubagent):
    def __init__(self) -> None:
        super().__init__("DummyFail", "Fails the context.")
    
    def execute(self, context: AgentContext) -> AgentContext:
        context.add_log("DummyFail executed.")
        context.current_status = WorkflowStatus.FAILED
        return context

def test_workflow_orchestrator_success() -> None:
    agent1 = DummyAgentPass()
    agent2 = DummyAgentPass()
    
    orchestrator = WorkflowOrchestrator([agent1, agent2])
    
    context = AgentContext(
        workflow_id="test-1",
        collected_data=ExtractedData(source_type="test")
    )
    
    result = orchestrator.run_workflow(context)
    
    assert result.current_status == WorkflowStatus.COMPLETED
    assert len(result.history) == 6  # start, pass1_msg, pass1_exec, pass2_msg, pass2_exec, end

def test_workflow_orchestrator_fail() -> None:
    agent1 = DummyAgentPass()
    agent2 = DummyAgentFail()
    agent3 = DummyAgentPass()
    
    orchestrator = WorkflowOrchestrator([agent1, agent2, agent3])
    
    context = AgentContext(
        workflow_id="test-2",
        collected_data=ExtractedData(source_type="test")
    )
    
    result = orchestrator.run_workflow(context)
    
    assert result.current_status == WorkflowStatus.FAILED
    # Should halt after agent2, so agent3 is not executed.
    logs = " ".join(result.history)
    assert "DummyFail executed" in logs
    assert "DummyPass executed" in logs

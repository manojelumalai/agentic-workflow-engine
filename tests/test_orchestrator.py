import pytest

from agent_engine.orchestrator import WorkflowEngine
from agent_engine.state import TaskStatus


@pytest.mark.asyncio
async def test_workflow_balance_query():
    engine = WorkflowEngine()
    state = await engine.invoke("What is my balance for ACC-1001?")
    assert state.task_status == TaskStatus.COMPLETED
    assert len(state.messages) >= 2
    assert any("250000" in m.content for m in state.messages)


@pytest.mark.asyncio
async def test_workflow_compliance_routing():
    engine = WorkflowEngine()
    state = await engine.invoke(
        "Run sanctions and AML compliance screening for GLOBAL_PARTNER_PTE_LTD"
    )
    assert state.task_status == TaskStatus.COMPLETED
    assert any("Compliance screening complete" in m.content for m in state.messages)


@pytest.mark.asyncio
async def test_workflow_transfer_requires_approval_and_resumes():
    engine = WorkflowEngine()
    state = await engine.invoke("Please transfer 50000 SGD from ACC-1001 to ACC-CORP-99")

    # Workflow must pause awaiting human approval
    assert state.task_status == TaskStatus.AWAITING_APPROVAL
    assert state.pending_approval is not None
    action_id = state.pending_approval.action_id
    token = state.pending_approval.approval_token

    # Resume with approval
    resumed_state = await engine.resume_approval(
        thread_id=state.thread_id, action_id=action_id, approved=True, token=token
    )
    assert resumed_state.task_status == TaskStatus.COMPLETED
    assert any("Transfer Executed Successfully" in m.content for m in resumed_state.messages)

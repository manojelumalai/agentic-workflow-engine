from agent_engine.safeguards.human_in_loop import ApprovalManager
from agent_engine.state import AgentRole, AgentState, TaskStatus


def test_approval_flow_success():
    manager = ApprovalManager(secret_key="test-secret-key-12345")
    state = AgentState(thread_id="thread-hitl-001")

    payload = {"amount": 50000.0, "source": "ACC-1001", "destination": "ACC-CORP-99"}
    approval = manager.request_approval(
        state=state,
        action_name="execute_bank_transfer",
        payload=payload,
        requested_by=AgentRole.FINANCIAL,
    )

    assert state.task_status == TaskStatus.AWAITING_APPROVAL
    assert approval.action_id.startswith("ACT-")
    assert approval.approval_token is not None

    # Resolve approval with valid token
    success, _msg = manager.resolve_approval(
        state=state, action_id=approval.action_id, approved=True, token=approval.approval_token
    )
    assert success is True
    assert state.task_status == TaskStatus.APPROVED


def test_approval_flow_invalid_token():
    manager = ApprovalManager(secret_key="test-secret-key-12345")
    state = AgentState(thread_id="thread-hitl-002")

    payload = {"amount": 1000.0}
    approval = manager.request_approval(
        state=state,
        action_name="execute_bank_transfer",
        payload=payload,
        requested_by=AgentRole.FINANCIAL,
    )

    success, msg = manager.resolve_approval(
        state=state, action_id=approval.action_id, approved=True, token="invalid-tampered-token"
    )
    assert success is False
    assert "Invalid cryptographic approval token" in msg

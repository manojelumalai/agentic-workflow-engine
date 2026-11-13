from agent_engine.state import AgentRole, AgentState, TaskStatus


def test_agent_state_initialization():
    state = AgentState(thread_id="test-thread-001")
    assert state.thread_id == "test-thread-001"
    assert state.current_agent == AgentRole.SUPERVISOR
    assert state.task_status == TaskStatus.PENDING
    assert len(state.messages) == 0
    assert not state.is_cycle_exceeded()


def test_agent_state_message_addition():
    state = AgentState(thread_id="test-thread-002")
    state.add_message(role="user", content="Check my balance for ACC-1001")
    assert len(state.messages) == 1
    assert state.messages[0].role == "user"
    assert "ACC-1001" in state.messages[0].content


def test_cycle_detection():
    state = AgentState(thread_id="test-thread-003", max_iterations=5)
    state.iteration_count = 5
    assert state.is_cycle_exceeded() is True

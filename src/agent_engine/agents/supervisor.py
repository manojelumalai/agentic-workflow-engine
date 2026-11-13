"""
Supervisor Agent: Orchestrator of Intent Detection and Specialist Routing.
"""

from __future__ import annotations

from agent_engine.state import AgentRole, AgentState, TaskStatus


class SupervisorAgent:
    """
    Decentralized task planner and supervisor. Evaluates workflow progress,
    updates task plans, and dynamically routes between specialized agents.
    """

    def __init__(self) -> None:
        self.role = AgentRole.SUPERVISOR

    async def step(self, state: AgentState) -> tuple[AgentState, AgentRole]:
        state.iteration_count += 1
        state.current_agent = self.role

        if state.is_cycle_exceeded():
            state.task_status = TaskStatus.FAILED
            state.add_message(
                role="system", content="Execution terminated: Maximum iteration cycles exceeded."
            )
            return state, AgentRole.SUPERVISOR

        # Evaluate last user message or agent output
        latest_msg = state.messages[-1].content.lower() if state.messages else ""

        # Router Logic
        if any(
            term in latest_msg
            for term in ["transfer", "send money", "payment", "balance", "fx", "rate"]
        ):
            target_agent = AgentRole.FINANCIAL
            state.next_step = "financial_operations"
            state.task_status = TaskStatus.IN_PROGRESS
            state.add_message(
                role="assistant",
                name=self.role.value,
                content="Routing task to Financial Agent for ledger and payment evaluation.",
            )
        elif any(term in latest_msg for term in ["sanction", "pep", "aml", "compliance", "fraud"]):
            target_agent = AgentRole.COMPLIANCE
            state.next_step = "compliance_screening"
            state.task_status = TaskStatus.IN_PROGRESS
            state.add_message(
                role="assistant",
                name=self.role.value,
                content="Routing query to Compliance Agent for regulatory verification.",
            )
        else:
            target_agent = AgentRole.RESEARCH
            state.next_step = "research_context"
            state.task_status = TaskStatus.IN_PROGRESS
            state.add_message(
                role="assistant",
                name=self.role.value,
                content="Routing query to Research Agent for context retrieval.",
            )

        return state, target_agent

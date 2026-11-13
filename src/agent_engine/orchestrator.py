"""
Workflow Engine: StateGraph Orchestration and Lifecycle Management.
Coordinates agents, conditional branch routing, and human-in-the-loop suspension.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from agent_engine.agents.compliance import ComplianceAgent
from agent_engine.agents.financial import FinancialAgent
from agent_engine.agents.research import ResearchAgent
from agent_engine.agents.supervisor import SupervisorAgent
from agent_engine.mcp.client import MCPClient
from agent_engine.safeguards.human_in_loop import ApprovalManager
from agent_engine.state import AgentRole, AgentState


class WorkflowEngine:
    """
    Main entry point for executing autonomous multi-agent graph workflows.
    Maintains active session checkpointers and safe state transitions.
    """

    def __init__(self) -> None:
        self.mcp_client = MCPClient()
        self.approval_manager = ApprovalManager()

        # Agents
        self.supervisor = SupervisorAgent()
        self.financial = FinancialAgent(self.mcp_client, self.approval_manager)
        self.compliance = ComplianceAgent(self.mcp_client)
        self.research = ResearchAgent(self.mcp_client)

        # Thread memory state store
        self._threads: dict[str, AgentState] = {}

    def get_state(self, thread_id: str) -> AgentState | None:
        return self._threads.get(thread_id)

    async def invoke(self, query: str, thread_id: str | None = None) -> AgentState:
        t_id = thread_id or str(uuid.uuid4())

        if t_id in self._threads:
            state = self._threads[t_id]
            state.add_message(role="user", content=query)
        else:
            state = AgentState(thread_id=t_id)
            state.add_message(role="user", content=query)
            self._threads[t_id] = state

        # Step 1: Supervisor routing
        state, next_agent = await self.supervisor.step(state)

        # Step 2: Specialist execution
        if next_agent == AgentRole.FINANCIAL:
            state, _ = await self.financial.step(state)
        elif next_agent == AgentRole.COMPLIANCE:
            state, _ = await self.compliance.step(state)
        elif next_agent == AgentRole.RESEARCH:
            state, _ = await self.research.step(state)

        return state

    async def resume_approval(
        self, thread_id: str, action_id: str, approved: bool, token: str, reason: str | None = None
    ) -> AgentState:
        if thread_id not in self._threads:
            raise ValueError(f"Thread '{thread_id}' not found.")

        state = self._threads[thread_id]
        success, msg = self.approval_manager.resolve_approval(
            state=state, action_id=action_id, approved=approved, token=token, reason=reason
        )

        if not success:
            raise PermissionError(f"Approval resolution failed: {msg}")

        # If approved, resume the financial agent execution step
        if approved and state.pending_approval:
            state, _ = await self.financial.step(state)

        return state

    async def stream_events(
        self, query: str, thread_id: str | None = None
    ) -> AsyncGenerator[dict, None]:
        t_id = thread_id or str(uuid.uuid4())
        yield {"event": "thread_initialized", "thread_id": t_id}

        state = AgentState(thread_id=t_id)
        state.add_message(role="user", content=query)
        self._threads[t_id] = state

        yield {"event": "agent_start", "agent": AgentRole.SUPERVISOR.value}
        state, next_agent = await self.supervisor.step(state)
        yield {
            "event": "supervisor_routed",
            "target_agent": next_agent.value,
            "next_step": state.next_step,
        }

        yield {"event": "agent_start", "agent": next_agent.value}
        if next_agent == AgentRole.FINANCIAL:
            state, _ = await self.financial.step(state)
        elif next_agent == AgentRole.COMPLIANCE:
            state, _ = await self.compliance.step(state)
        elif next_agent == AgentRole.RESEARCH:
            state, _ = await self.research.step(state)

        yield {
            "event": "workflow_finished",
            "task_status": state.task_status.value,
            "messages": [m.model_dump(mode="json") for m in state.messages],
        }

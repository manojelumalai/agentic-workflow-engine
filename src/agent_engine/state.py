"""
Core State Definitions for Multi-Agent Workflow Engine.
Provides immutable, typed state structures and validation schemas for multi-agent loops.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AgentRole(StrEnum):
    SUPERVISOR = "supervisor"
    FINANCIAL = "financial_agent"
    RESEARCH = "research_agent"
    COMPLIANCE = "compliance_agent"
    HUMAN_APPROVER = "human_approver"


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class ToolCall(BaseModel):
    id: str = Field(description="Unique tool execution identifier")
    name: str = Field(description="Name of the MCP or local tool")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Structured tool arguments")


class ToolResult(BaseModel):
    tool_call_id: str
    output: Any
    is_error: bool = False
    execution_time_ms: float = 0.0


class Message(BaseModel):
    role: str = Field(description="'system', 'user', 'assistant', or 'tool'")
    content: str
    name: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ActionApproval(BaseModel):
    action_id: str
    requested_by: AgentRole
    action_name: str
    payload: dict[str, Any]
    status: TaskStatus = TaskStatus.AWAITING_APPROVAL
    requires_human_approval: bool = True
    approval_token: str | None = None
    rejection_reason: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentState(BaseModel):
    """
    Central state container passed across all agent nodes in the workflow.
    Maintains complete audit trails, tool executions, and state checkpoints.
    """

    thread_id: str = Field(description="Unique correlation ID for the execution session")
    messages: list[Message] = Field(default_factory=list)
    current_agent: AgentRole = AgentRole.SUPERVISOR
    next_step: str | None = None
    task_status: TaskStatus = TaskStatus.PENDING
    plan: list[str] = Field(default_factory=list)
    pending_approval: ActionApproval | None = None
    executed_tools: list[ToolResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    iteration_count: int = 0
    max_iterations: int = 15
    total_tokens_consumed: int = 0

    def add_message(
        self,
        role: str,
        content: str,
        name: str | None = None,
        tool_calls: list[ToolCall] | None = None,
    ) -> None:
        self.messages.append(Message(role=role, content=content, name=name, tool_calls=tool_calls))

    def is_cycle_exceeded(self) -> bool:
        return self.iteration_count >= self.max_iterations

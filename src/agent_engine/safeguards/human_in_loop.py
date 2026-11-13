"""
Human-in-the-Loop (HITL) Checkpointing and Authorization Gateway.
Implements deterministic state halts for sensitive transactions requiring dual-control.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time

from agent_engine.state import ActionApproval, AgentRole, AgentState, TaskStatus


class ApprovalManager:
    """
    Manages cryptographic approval tokens, state suspension, and resume validation.
    Ensures zero unintended autonomous mutations on critical systems.
    """

    def __init__(self, secret_key: str | None = None) -> None:
        self._secret = (secret_key or secrets.token_hex(32)).encode("utf-8")
        self._pending_approvals: dict[str, ActionApproval] = {}

    def _generate_token(self, action_id: str, thread_id: str) -> str:
        msg = f"{action_id}:{thread_id}:{time.time()}".encode()
        return hmac.new(self._secret, msg, hashlib.sha256).hexdigest()

    def request_approval(
        self, state: AgentState, action_name: str, payload: dict, requested_by: AgentRole
    ) -> ActionApproval:
        action_id = f"ACT-{secrets.token_hex(6).upper()}"
        token = self._generate_token(action_id, state.thread_id)

        approval = ActionApproval(
            action_id=action_id,
            requested_by=requested_by,
            action_name=action_name,
            payload=payload,
            status=TaskStatus.AWAITING_APPROVAL,
            requires_human_approval=True,
            approval_token=token,
        )

        state.task_status = TaskStatus.AWAITING_APPROVAL
        state.pending_approval = approval
        self._pending_approvals[action_id] = approval

        state.add_message(
            role="system",
            content=(
                f"Workflow paused. Sensitive action '{action_name}' requires human approval. "
                f"Action ID: {action_id}"
            ),
        )
        return approval

    def resolve_approval(
        self,
        state: AgentState,
        action_id: str,
        approved: bool,
        token: str,
        reason: str | None = None,
    ) -> tuple[bool, str]:
        if action_id not in self._pending_approvals:
            return False, f"Action ID '{action_id}' not found or already processed."

        approval = self._pending_approvals[action_id]

        if approval.approval_token != token:
            return False, "Invalid cryptographic approval token."

        if approved:
            approval.status = TaskStatus.APPROVED
            state.task_status = TaskStatus.APPROVED
            state.add_message(
                role="system",
                content=(
                    f"Action '{approval.action_name}' approved by human operator. "
                    "Resuming execution."
                ),
            )
            del self._pending_approvals[action_id]
            return True, "Action successfully approved."
        else:
            approval.status = TaskStatus.REJECTED
            approval.rejection_reason = reason or "Rejected by operator."
            state.task_status = TaskStatus.REJECTED
            state.add_message(
                role="system",
                content=(
                    f"Action '{approval.action_name}' rejected. Reason: {approval.rejection_reason}"
                ),
            )
            del self._pending_approvals[action_id]
            return True, f"Action rejected: {approval.rejection_reason}"

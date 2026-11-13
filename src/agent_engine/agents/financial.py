"""
Financial Specialist Agent.
Executes ledger queries, calculates FX conversions, and prepares funds transfers.
"""

from __future__ import annotations

import re

from agent_engine.mcp.client import MCPClient
from agent_engine.safeguards.human_in_loop import ApprovalManager
from agent_engine.state import AgentRole, AgentState, TaskStatus


class FinancialAgent:
    """
    Handles financial reasoning, balance audits, and transaction formulation.
    Enforces deterministic approval halts for any money movement.
    """

    def __init__(self, mcp_client: MCPClient, approval_manager: ApprovalManager) -> None:
        self.role = AgentRole.FINANCIAL
        self.mcp = mcp_client
        self.approval = approval_manager

    async def step(self, state: AgentState) -> tuple[AgentState, AgentRole | None]:
        state.iteration_count += 1
        state.current_agent = self.role

        query = state.messages[0].content if state.messages else ""

        # Case 1: Check balance
        if "balance" in query.lower():
            # Extract account ID or default
            acc_match = re.search(r"ACC-[\w-]+", query)
            acc_id = acc_match.group(0) if acc_match else "ACC-1001"
            res = await self.mcp.call_tool(
                "check_account_balance", {"account_id": acc_id, "currency": "SGD"}
            )
            state.executed_tools.append(res)
            state.task_status = TaskStatus.COMPLETED
            state.add_message(
                role="assistant",
                name=self.role.value,
                content=(
                    f"Verified Ledger Balance for {acc_id}: {res.output.get('available_balance')} "
                    f"{res.output.get('currency')} (Status: {res.output.get('status')})."
                ),
            )
            return state, None

        # Case 2: Fund Transfer execution
        if any(term in query.lower() for term in ["transfer", "send"]):
            # Check if we were already approved
            if state.task_status == TaskStatus.APPROVED and state.pending_approval:
                payload = state.pending_approval.payload
                exec_res = await self.mcp.call_tool("execute_bank_transfer", payload)
                state.executed_tools.append(exec_res)
                state.task_status = TaskStatus.COMPLETED
                state.pending_approval = None
                state.add_message(
                    role="assistant",
                    name=self.role.value,
                    content=(
                        "Transfer Executed Successfully. Confirmation ID: "
                        f"{exec_res.output.get('transaction_id')}. "
                        f"Message: {exec_res.output.get('message')}"
                    ),
                )
                return state, None

            # Parse transfer details
            source_acc = "ACC-1001"
            dest_acc = "ACC-CORP-99"
            amount = 50000.00  # Default test transfer
            currency = "SGD"

            # Sensitive action: Request Human In The Loop approval
            payload = {
                "source_account": source_acc,
                "destination_account": dest_acc,
                "amount": amount,
                "currency": currency,
            }
            approval = self.approval.request_approval(
                state=state,
                action_name="execute_bank_transfer",
                payload=payload,
                requested_by=self.role,
            )
            state.add_message(
                role="assistant",
                name=self.role.value,
                content=(
                    f"Prepared transfer of {amount} {currency} from {source_acc} to {dest_acc}. "
                    f"Dual-control authorization required. Action ID: {approval.action_id}."
                ),
            )
            return state, None

        # Fallback
        state.task_status = TaskStatus.COMPLETED
        state.add_message(
            role="assistant",
            name=self.role.value,
            content="Financial operation evaluated. No further action needed.",
        )
        return state, None

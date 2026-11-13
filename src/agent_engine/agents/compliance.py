"""
Compliance & Regulatory Screening Agent.
"""

from __future__ import annotations

from agent_engine.mcp.client import MCPClient
from agent_engine.state import AgentRole, AgentState, TaskStatus


class ComplianceAgent:
    """
    Executes automated sanctions screening, PEP checks, and AML verification.
    """

    def __init__(self, mcp_client: MCPClient) -> None:
        self.role = AgentRole.COMPLIANCE
        self.mcp = mcp_client

    async def step(self, state: AgentState) -> tuple[AgentState, AgentRole | None]:
        state.iteration_count += 1
        state.current_agent = self.role

        entity_name = "GLOBAL_PARTNER_PTE_LTD"
        country_code = "SG"

        res = await self.mcp.call_tool(
            "query_compliance_database", {"entity_name": entity_name, "country_code": country_code}
        )
        state.executed_tools.append(res)
        state.task_status = TaskStatus.COMPLETED

        risk_score = res.output.get("aml_risk_score", 0)
        status = res.output.get("status", "PASS")

        state.add_message(
            role="assistant",
            name=self.role.value,
            content=(
                f"Compliance screening complete for {entity_name}. Status: {status} "
                f"(AML Risk Score: {risk_score}/100)."
            ),
        )
        return state, None

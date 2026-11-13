"""
Research and Context Retrieval Agent.
"""

from __future__ import annotations

from agent_engine.mcp.client import MCPClient
from agent_engine.state import AgentRole, AgentState, TaskStatus


class ResearchAgent:
    """
    Enriches user query with factual context, knowledge base lookups, and FX market rates.
    """

    def __init__(self, mcp_client: MCPClient) -> None:
        self.role = AgentRole.RESEARCH
        self.mcp = mcp_client

    async def step(self, state: AgentState) -> tuple[AgentState, AgentRole | None]:
        state.iteration_count += 1
        state.current_agent = self.role

        # Sample context enrichment: fetch market FX rate
        res = await self.mcp.call_tool(
            "fetch_market_fx_rates", {"base_currency": "USD", "target_currency": "SGD"}
        )
        state.executed_tools.append(res)
        state.task_status = TaskStatus.COMPLETED

        rate = res.output.get("rate")
        state.add_message(
            role="assistant",
            name=self.role.value,
            content=(
                f"Context enriched: Current USD/SGD spot market rate is {rate} "
                f"(spread {res.output.get('spread_bps')} bps)."
            ),
        )
        return state, None

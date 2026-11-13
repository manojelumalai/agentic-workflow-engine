"""
Basic Agent Flow Example.
Demonstrates autonomous supervisor intent classification and context enrichment.
"""

import asyncio

from agent_engine.orchestrator import WorkflowEngine


async def main():
    engine = WorkflowEngine()

    print("--- 1. Querying Account Balance ---")
    query_1 = "Can you please check the available balance for account ACC-1001?"
    state_1 = await engine.invoke(query_1)
    print(f"Status: {state_1.task_status.value}")
    print(f"Agent Responded: {state_1.current_agent.value}")
    print(f"Output: {state_1.messages[-1].content}\n")

    print("--- 2. General Market Context Retrieval ---")
    # Note: the supervisor router sends "fx"/"rate" phrasing to the financial agent (see
    # agents/supervisor.py), so this query intentionally avoids those keywords to reach
    # the research agent, which always enriches context with the current USD/SGD FX rate.
    query_2 = "Can you give me some general market context ahead of my upcoming transaction?"
    state_2 = await engine.invoke(query_2)
    print(f"Status: {state_2.task_status.value}")
    print(f"Agent Responded: {state_2.current_agent.value}")
    print(f"Output: {state_2.messages[-1].content}\n")

    print("--- 3. Regulatory Sanctions Screening ---")
    query_3 = "Screen entity SANCTIONED_CORP against global PEP and AML watchlists."
    state_3 = await engine.invoke(query_3)
    print(f"Status: {state_3.task_status.value}")
    print(f"Output: {state_3.messages[-1].content}\n")


if __name__ == "__main__":
    asyncio.run(main())

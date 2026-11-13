"""
Financial Transfer with Human-In-The-Loop Approval Checkpoint Example.
Demonstrates state suspension for high-value fund movements and cryptographic resumption.
"""

import asyncio

from agent_engine.orchestrator import WorkflowEngine


async def main():
    engine = WorkflowEngine()

    print("--- 1. Submitting High-Value Fund Transfer Request ---")
    query = "Initiate an emergency transfer of 50,000 SGD from ACC-1001 to ACC-CORP-99."
    state = await engine.invoke(query)

    print(f"Task Status: {state.task_status.value}")
    print(f"Agent Message: {state.messages[-1].content}")

    if state.pending_approval:
        approval = state.pending_approval
        print("\n[!] WORKFLOW HALTED: Human-In-The-Loop Checkpoint Active")
        print(f"    Action Name:   {approval.action_name}")
        print(f"    Action ID:     {approval.action_id}")
        print(f"    Payload:       {approval.payload}")
        print(f"    HMAC Token:    {approval.approval_token[:16]}... (Truncated)")

        # Simulate human operator review and approval
        print("\n--- 2. Dual-Control Operator Approves Transaction ---")
        resumed_state = await engine.resume_approval(
            thread_id=state.thread_id,
            action_id=approval.action_id,
            approved=True,
            token=approval.approval_token,
        )

        print(f"Resumed Task Status: {resumed_state.task_status.value}")
        print(f"Final Confirmation:  {resumed_state.messages[-1].content}")


if __name__ == "__main__":
    asyncio.run(main())

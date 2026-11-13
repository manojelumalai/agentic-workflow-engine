"""
FastAPI Application Entry Point for Agentic Workflow Engine.
"""

from __future__ import annotations

import json
import os
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent_engine.orchestrator import WorkflowEngine
from agent_engine.state import AgentState

app = FastAPI(
    title="Agentic Workflow Engine API",
    version="1.0.0",
    description=(
        "Enterprise multi-agent orchestration engine with a state-graph runtime, "
        "Model Context Protocol (MCP) tools, and human-in-the-loop safeguards"
    ),
)

# Origins are opt-in via env var (comma-separated); an empty list never combines
# a wildcard with credentials. Set CORS_ALLOWED_ORIGINS for browser-based clients.
_cors_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=bool(_cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = WorkflowEngine()


class InvokeRequest(BaseModel):
    query: str = Field(description="User prompt or intent to execute")
    thread_id: str | None = Field(default=None, description="Optional existing session thread ID")


class ApprovalRequest(BaseModel):
    thread_id: str
    action_id: str
    approved: bool
    token: str
    reason: str | None = None


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "HEALTHY", "version": "1.0.0"}


@app.post("/v1/agents/invoke", response_model=dict[str, Any])
async def invoke_agent(req: InvokeRequest) -> dict[str, Any]:
    try:
        state: AgentState = await engine.invoke(query=req.query, thread_id=req.thread_id)
        return {
            "thread_id": state.thread_id,
            "status": state.task_status.value,
            "current_agent": state.current_agent.value,
            "pending_approval": (
                state.pending_approval.model_dump(mode="json") if state.pending_approval else None
            ),
            "messages": [m.model_dump(mode="json") for m in state.messages],
            "executed_tools": [t.model_dump(mode="json") for t in state.executed_tools],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/v1/approvals/resume")
async def resume_approval(req: ApprovalRequest) -> dict[str, Any]:
    try:
        state: AgentState = await engine.resume_approval(
            thread_id=req.thread_id,
            action_id=req.action_id,
            approved=req.approved,
            token=req.token,
            reason=req.reason,
        )
        return {
            "thread_id": state.thread_id,
            "status": state.task_status.value,
            "messages": [m.model_dump(mode="json") for m in state.messages],
        }
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err)) from val_err
    except PermissionError as perm_err:
        raise HTTPException(status_code=403, detail=str(perm_err)) from perm_err
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/v1/agents/stream")
async def stream_agent(query: str, thread_id: str | None = None) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        async for event in engine.stream_events(query=query, thread_id=thread_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

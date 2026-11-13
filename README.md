# Agentic Workflow Engine 🤖⚡

[![CI](https://github.com/manojelumalai/agentic-workflow-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/manojelumalai/agentic-workflow-engine/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11 | 3.12 | 3.13](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196.svg)](https://conventionalcommits.org)

A state-managed **multi-agent orchestration engine** featuring supervisor-based routing, a standardized **Model Context Protocol (MCP)**-style tool registry, and cryptographic **Human-in-the-Loop (HITL)** safeguards, built as a reference implementation for high-stakes workflows (FinTech, banking operations, autonomous agent pipelines).

Designed to address a core enterprise AI problem: **probabilistic agent reasoning paired with deterministic, audited execution.**

> **This is a reference/demo implementation**, not a production system. All "bank" balances, FX rates, transfer settlement, and compliance screening are deterministic in-memory mocks — see [Design notes / limitations](#-design-notes--limitations) for what to replace before any real deployment.

---

## 🏛️ Architecture Overview

```
                      +-----------------------------+
                      |   User / Client Interface   |
                      +--------------+--------------+
                                     |  HTTP / SSE
                                     v
                      +-----------------------------+
                      |    FastAPI Gateway Server   |
                      +--------------+--------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                      State-Graph Workflow Orchestrator                   |
|                                                                          |
|                   +-----------------------------------+                  |
|                   |         Supervisor Agent          |                  |
|                   |  - Intent Decomposition           |                  |
|                   |  - Dynamic Route Dispatching      |                  |
|                   +-----+-------------------+---------+                  |
|                         |                   |                            |
|             +-----------+                   +-----------+                |
|             v                                           v                |
|  +--------------------+                       +--------------------+     |
|  |  Financial Agent   |                       |  Compliance Agent  |     |
|  | - Ledger Queries   |                       | - Sanctions / PEP  |     |
|  | - Transfer Logic   |                       | - AML Risk Scoring |     |
|  +----------+---------+                       +----------+---------+     |
|             |                                            |               |
|             +-------------------+------------------------+               |
|                                 |                                        |
|                                 v                                        |
|                +---------------------------------+                       |
|                |   Human-in-the-Loop Checkpoint  |                       |
|                | - Dual-Control Approval Gateway |                       |
|                | - Cryptographic Token Hashing   |                       |
|                +----------------+----------------+                       |
+---------------------------------|----------------------------------------+
                                  |
                                  v
+--------------------------------------------------------------------------+
|               Model Context Protocol (MCP) Tool Subsystem                |
|                                                                          |
|  [check_balance]    [fetch_fx_rates]    [execute_transfer]   [aml_query] |
+--------------------------------------------------------------------------+
```

---

## ✨ Key Capabilities

1. **State-Graph Runtime:**
   - Central `AgentState` (Pydantic) schema tracks complete message history, tool executions, and per-thread checkpoints.
   - Cycle detection (`max_iterations`) prevents infinite agent loops and run-away inference costs.

2. **Model Context Protocol (MCP)-Style Tool Registry:**
   - Standardized tool registration, parameter schemas, and per-call latency telemetry.
   - Tool handlers are decoupled from agent prompts for modular maintenance. Handlers in this repo are deterministic mocks (see limitations below).

3. **Deterministic Human-in-the-Loop (HITL) Safeguards:**
   - High-value or state-mutating actions (e.g. fund transfers) automatically pause the execution graph.
   - Generates an HMAC-SHA256 authorization token requiring explicit sign-off before resumption.

4. **FastAPI Service & Server-Sent Events:**
   - Async endpoints supporting one-shot invocation (`POST /v1/agents/invoke`) and real-time streaming (`GET /v1/agents/stream`).

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)

### 1. Install

```bash
git clone https://github.com/manojelumalai/agentic-workflow-engine.git
cd agentic-workflow-engine
make install
```

### 2. Run checks (lint, type-check, tests with coverage)

```bash
make check
```

### 3. Launch the API server

```bash
make run
# Uvicorn running on http://0.0.0.0:8080
```

---

## 📡 API Usage Examples

The server listens on port `8080` (see `make run` / `Dockerfile`). Output below was captured by running the app in-process via `httpx.ASGITransport` (`uv run python -c "..."`) — a `curl` call to a running `make run` server returns the same JSON shape.

### 1. Check Account Balance (Autonomous Resolution)

```bash
curl -X POST http://localhost:8080/v1/agents/invoke \
  -H "Content-Type: application/json" \
  -d '{"query": "Please check available balance for account ACC-1001"}'
```

**Response:**
```json
{
  "thread_id": "3afa2603-fbcb-4ecf-9e45-c81eb37827e8",
  "status": "completed",
  "current_agent": "financial_agent",
  "pending_approval": null,
  "messages": [
    {
      "role": "user",
      "content": "Please check available balance for account ACC-1001"
    },
    {
      "role": "assistant",
      "name": "supervisor",
      "content": "Routing task to Financial Agent for ledger and payment evaluation."
    },
    {
      "role": "assistant",
      "name": "financial_agent",
      "content": "Verified Ledger Balance for ACC-1001: 250000.0 SGD (Status: ACTIVE)."
    }
  ],
  "executed_tools": [
    {
      "tool_call_id": "596d3284-c10f-4182-ad6e-181b384f0f6a",
      "output": {
        "account_id": "ACC-1001",
        "available_balance": 250000.0,
        "currency": "SGD",
        "status": "ACTIVE",
        "as_of": "2026-11-13T00:00:00Z"
      },
      "is_error": false,
      "execution_time_ms": 0.006
    }
  ]
}
```

### 2. Fund Transfer (Triggers Human-in-the-Loop Approval)

```bash
curl -X POST http://localhost:8080/v1/agents/invoke \
  -H "Content-Type: application/json" \
  -d '{"query": "Transfer 50000 SGD from ACC-1001 to ACC-CORP-99"}'
```

**Response (halted for dual-control):**
```json
{
  "thread_id": "cca58731-f682-4a35-9053-b81545e51875",
  "status": "awaiting_approval",
  "current_agent": "financial_agent",
  "pending_approval": {
    "action_id": "ACT-33C5BB83A0B4",
    "requested_by": "financial_agent",
    "action_name": "execute_bank_transfer",
    "payload": {
      "source_account": "ACC-1001",
      "destination_account": "ACC-CORP-99",
      "amount": 50000.0,
      "currency": "SGD"
    },
    "status": "awaiting_approval",
    "requires_human_approval": true,
    "approval_token": "<64-char hex HMAC-SHA256 token>",
    "rejection_reason": null,
    "timestamp": "2026-11-13T03:00:58.159719Z"
  },
  "messages": ["..."],
  "executed_tools": []
}
```

### 3. Approve and Resume Execution

```bash
curl -X POST http://localhost:8080/v1/approvals/resume \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "cca58731-f682-4a35-9053-b81545e51875",
    "action_id": "ACT-33C5BB83A0B4",
    "approved": true,
    "token": "<approval_token from the previous response>"
  }'
```

**Response:**
```json
{
  "thread_id": "cca58731-f682-4a35-9053-b81545e51875",
  "status": "completed",
  "messages": [
    "...",
    {
      "role": "system",
      "content": "Action 'execute_bank_transfer' approved by human operator. Resuming execution."
    },
    {
      "role": "assistant",
      "name": "financial_agent",
      "content": "Transfer Executed Successfully. Confirmation ID: TXN-3EBA4F936D0D. Message: Payment cleared via FAST/MEPS network."
    }
  ]
}
```

---

## 🧩 Design notes / limitations

This repository demonstrates the orchestration, HITL, and MCP-style tooling *patterns*; it does not integrate a real LLM, bank, or compliance provider. Specifically:

- **No LLM is called.** `SupervisorAgent` routes on keyword matching (`agents/supervisor.py`), and each specialist agent (`agents/financial.py`, `agents/compliance.py`, `agents/research.py`) runs fixed, rule-based logic — there is no prompt, model call, or reasoning step. To plug in a real model, replace the `step()` bodies with calls to your LLM provider (e.g. via `httpx`, already a dependency) and keep the same `AgentState` contract.
- **Tool handlers are deterministic mocks.** `MCPClient._handle_check_balance`, `_handle_fetch_fx_rates`, `_handle_execute_transfer`, and `_handle_compliance_check` (`mcp/client.py`) return hardcoded/lookup-table data — no real ledger, FX feed, payment rail, or sanctions database is called. Swap these handlers for real HTTP/gRPC calls to your providers; the `MCPToolRegistry` execution path (parameter validation, timing, error capture) is reusable as-is.
- **State is in-memory only.** `WorkflowEngine._threads` and `ApprovalManager._pending_approvals` are plain `dict`s with no persistence — restarting the process loses every in-flight thread and pending approval. For production, back these with a database or durable store.
- **The HITL signing key is ephemeral by default.** `ApprovalManager()` generates a random secret per process (`secrets.token_hex(32)`) unless you pass `secret_key` explicitly; tokens issued before a restart will no longer validate. Supply a stable secret (e.g. from a secrets manager) for any deployment that survives restarts.
- **"MCP" here means an MCP-shaped local tool registry**, not the official Model Context Protocol SDK/transport — there is no `mcp` package dependency. The registration/validation/execution shape mirrors MCP's tool model so it can be swapped for a real MCP client later.
- **CORS is locked down by default.** `CORS_ALLOWED_ORIGINS` (comma-separated) must be set for the API to allow any browser origin; with no origins configured, credentialed wildcard CORS is never enabled.

---

## 🛠️ Project Structure

```
agentic-workflow-engine/
├── src/agent_engine/
│   ├── state.py              # Typed Pydantic AgentState and message schemas
│   ├── orchestrator.py       # State-graph orchestration & event streaming
│   ├── agents/
│   │   ├── supervisor.py     # Keyword-based intent routing
│   │   ├── financial.py      # Ledger reasoning & transaction prep
│   │   ├── compliance.py     # Sanctions, PEP & AML screening
│   │   └── research.py       # Market FX and factual context retrieval
│   ├── mcp/
│   │   ├── client.py         # MCP-style tool client with mock handlers
│   │   └── registry.py       # Tool registration & async execution
│   ├── safeguards/
│   │   └── human_in_loop.py  # HMAC token generator & approval checkpoint
│   └── api/
│       └── app.py            # FastAPI async REST & SSE endpoints
├── tests/                    # pytest suite (uv run pytest --cov)
├── examples/                 # Runnable usage examples (uv run python examples/<file>.py)
├── Dockerfile
└── docker-compose.yml
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, commit conventions, and the PR checklist. Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## 🔒 Security

See [SECURITY.md](SECURITY.md) to report vulnerabilities.

## 📄 License

[MIT License](LICENSE). Author: **Manoj Elumalai** ([LinkedIn](https://www.linkedin.com/in/manojelumalai)).

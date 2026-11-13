# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-13

### Added

- Initial public release: state-graph multi-agent orchestration engine (`WorkflowEngine`) with supervisor routing to financial, compliance, and research agents.
- Model Context Protocol (MCP)-style tool registry and client with mock account balance, FX rate, fund transfer, and compliance screening tools.
- Human-in-the-loop (HITL) approval gateway with HMAC-SHA256 approval tokens for sensitive actions.
- FastAPI service exposing `/health`, `/v1/agents/invoke`, `/v1/approvals/resume`, and `/v1/agents/stream`.
- Test suite (`pytest`) covering state, orchestrator, MCP client, and HITL approval flows.
- Project tooling: `ruff`, `mypy` (strict), `pytest-cov`, `pre-commit`, Dockerfile, and CI workflow (lint, test matrix, docker build).

[Unreleased]: https://github.com/manojelumalai/agentic-workflow-engine/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/manojelumalai/agentic-workflow-engine/releases/tag/v1.0.0

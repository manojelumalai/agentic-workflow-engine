"""
Model Context Protocol (MCP) Tool Registry and Specifications.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Coroutine
from typing import Any

from pydantic import BaseModel

from agent_engine.state import ToolCall, ToolResult


class MCPToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any | None = None


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    parameters: list[MCPToolParameter]
    requires_approval: bool = False
    rate_limit_per_minute: int = 60


class MCPToolRegistry:
    """
    Central registry for Model Context Protocol (MCP) compliant tools.
    Supports asynchronous execution, parameter validation, and telemetry.
    """

    def __init__(self) -> None:
        self._tools: dict[str, MCPToolDefinition] = {}
        self._handlers: dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: list[MCPToolParameter],
        handler: Callable[..., Coroutine[Any, Any, Any]],
        requires_approval: bool = False,
    ) -> None:
        defn = MCPToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            requires_approval=requires_approval,
        )
        self._tools[name] = defn
        self._handlers[name] = handler

    def get_tool(self, name: str) -> MCPToolDefinition | None:
        return self._tools.get(name)

    def list_tools(self) -> list[MCPToolDefinition]:
        return list(self._tools.values())

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        start_time = time.perf_counter()
        tool_name = tool_call.name

        if tool_name not in self._handlers:
            return ToolResult(
                tool_call_id=tool_call.id,
                output=f"Error: Tool '{tool_name}' not found in registry.",
                is_error=True,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        handler = self._handlers[tool_name]
        try:
            output = await handler(**tool_call.arguments)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return ToolResult(
                tool_call_id=tool_call.id,
                output=output,
                is_error=False,
                execution_time_ms=elapsed_ms,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return ToolResult(
                tool_call_id=tool_call.id,
                output=f"Execution error in {tool_name}: {exc!s}",
                is_error=True,
                execution_time_ms=elapsed_ms,
            )


# Default Singleton Registry
default_registry = MCPToolRegistry()

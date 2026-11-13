"""
Model Context Protocol (MCP) Client and Built-in Enterprise Tool Handlers.
"""

from __future__ import annotations

import uuid
from typing import Any

from agent_engine.mcp.registry import MCPToolParameter, MCPToolRegistry, default_registry
from agent_engine.state import ToolCall, ToolResult


class MCPClient:
    """
    Client for interacting with MCP-compatible tool services.
    Encapsulates tool execution, permission gating, and logging.
    """

    def __init__(self, registry: MCPToolRegistry = default_registry) -> None:
        self.registry = registry
        self._init_builtin_tools()

    def _init_builtin_tools(self) -> None:
        # 1. Account balance check tool
        self.registry.register(
            name="check_account_balance",
            description="Fetch current ledger balance and currency for a customer account.",
            parameters=[
                MCPToolParameter(
                    name="account_id", type="string", description="Unique bank account identifier"
                ),
                MCPToolParameter(
                    name="currency",
                    type="string",
                    description="Currency code (e.g. SGD, USD, MYR)",
                    default="SGD",
                ),
            ],
            handler=self._handle_check_balance,
            requires_approval=False,
        )

        # 2. FX Rate tool
        self.registry.register(
            name="fetch_market_fx_rates",
            description="Retrieve real-time foreign exchange market conversion rates.",
            parameters=[
                MCPToolParameter(
                    name="base_currency", type="string", description="Base ISO currency"
                ),
                MCPToolParameter(
                    name="target_currency", type="string", description="Target ISO currency"
                ),
            ],
            handler=self._handle_fetch_fx_rates,
            requires_approval=False,
        )

        # 3. High-Value Fund Transfer (Sensitive Tool - Requires Approval)
        self.registry.register(
            name="execute_bank_transfer",
            description="Execute real-time domestic or cross-border payment between accounts.",
            parameters=[
                MCPToolParameter(
                    name="source_account", type="string", description="Originating account ID"
                ),
                MCPToolParameter(
                    name="destination_account",
                    type="string",
                    description="Beneficiary account ID",
                ),
                MCPToolParameter(name="amount", type="number", description="Transaction amount"),
                MCPToolParameter(name="currency", type="string", description="Currency ISO code"),
            ],
            handler=self._handle_execute_transfer,
            requires_approval=True,
        )

        # 4. Compliance & AML screening tool
        self.registry.register(
            name="query_compliance_database",
            description=(
                "Perform sanctions screening, PEP checks, and AML risk assessment on counterparty."
            ),
            parameters=[
                MCPToolParameter(
                    name="entity_name",
                    type="string",
                    description="Full legal name of person or company",
                ),
                MCPToolParameter(
                    name="country_code", type="string", description="2-letter ISO country code"
                ),
            ],
            handler=self._handle_compliance_check,
            requires_approval=False,
        )

    async def _handle_check_balance(self, account_id: str, currency: str = "SGD") -> dict[str, Any]:
        # Deterministic mock reflecting enterprise banking data
        balances = {"ACC-1001": 250000.00, "ACC-1002": 15000.50, "ACC-CORP-99": 4820000.00}
        bal = balances.get(account_id, 10000.00)
        return {
            "account_id": account_id,
            "available_balance": bal,
            "currency": currency.upper(),
            "status": "ACTIVE",
            "as_of": "2026-11-13T00:00:00Z",
        }

    async def _handle_fetch_fx_rates(
        self, base_currency: str, target_currency: str
    ) -> dict[str, Any]:
        rates = {
            ("USD", "SGD"): 1.345,
            ("SGD", "MYR"): 3.480,
            ("USD", "MYR"): 4.680,
            ("SGD", "USD"): 0.743,
        }
        pair = (base_currency.upper(), target_currency.upper())
        rate = rates.get(pair, 1.0)
        return {
            "base": base_currency.upper(),
            "target": target_currency.upper(),
            "rate": rate,
            "spread_bps": 12,
        }

    async def _handle_execute_transfer(
        self, source_account: str, destination_account: str, amount: float, currency: str
    ) -> dict[str, Any]:
        tx_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        return {
            "transaction_id": tx_id,
            "status": "SETTLED",
            "source": source_account,
            "destination": destination_account,
            "amount": amount,
            "currency": currency.upper(),
            "message": "Payment cleared via FAST/MEPS network.",
        }

    async def _handle_compliance_check(self, entity_name: str, country_code: str) -> dict[str, Any]:
        restricted_names = ["SANCTIONED_CORP", "TERROR_FINANCE_LTD"]
        is_flagged = any(bad in entity_name.upper() for bad in restricted_names)
        return {
            "entity": entity_name,
            "country": country_code.upper(),
            "aml_risk_score": 95 if is_flagged else 12,
            "status": "REJECT" if is_flagged else "PASS",
            "requires_enhanced_due_diligence": is_flagged,
        }

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        call = ToolCall(id=str(uuid.uuid4()), name=name, arguments=arguments)
        return await self.registry.execute(call)

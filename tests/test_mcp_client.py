import pytest

from agent_engine.mcp.client import MCPClient


@pytest.mark.asyncio
async def test_mcp_check_balance():
    client = MCPClient()
    res = await client.call_tool(
        "check_account_balance", {"account_id": "ACC-1001", "currency": "SGD"}
    )
    assert res.is_error is False
    assert res.output["account_id"] == "ACC-1001"
    assert res.output["available_balance"] == 250000.00
    assert res.output["currency"] == "SGD"


@pytest.mark.asyncio
async def test_mcp_compliance_screening():
    client = MCPClient()
    # Test valid entity
    res = await client.call_tool(
        "query_compliance_database", {"entity_name": "ACME_CORP", "country_code": "SG"}
    )
    assert res.is_error is False
    assert res.output["status"] == "PASS"

    # Test sanctioned entity
    res_sanctioned = await client.call_tool(
        "query_compliance_database",
        {"entity_name": "SANCTIONED_CORP", "country_code": "SG"},
    )
    assert res_sanctioned.is_error is False
    assert res_sanctioned.output["status"] == "REJECT"
    assert res_sanctioned.output["aml_risk_score"] == 95


@pytest.mark.asyncio
async def test_mcp_unknown_tool():
    client = MCPClient()
    res = await client.call_tool("non_existent_tool", {})
    assert res.is_error is True
    assert "not found" in res.output

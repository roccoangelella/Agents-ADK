# tests/test_core_tools.py
import pytest
from mcp.shared.memory import create_connected_server_and_client_session
from mcp_server_template.server import app
from mcp_server_template.schemas import ServerStatusResponse

pytestmark = pytest.mark.asyncio


async def test_server_status_tool():
    """
    Tests the 'server_status' tool to ensure it returns the correct structured response.
    """
    async with create_connected_server_and_client_session(app._mcp_server) as client:
        result = await client.call_tool("server_status", {})
        assert not result.isError, f"Tool call returned an error: {result.content}"
        assert result.structuredContent is not None
        status = ServerStatusResponse(**result.structuredContent)
        assert status.server_name == "DevServer"
        assert status.tools_available > 0


async def test_greet_tool():
    """
    Tests the 'greet' tool to ensure it returns the correct greeting.
    """
    async with create_connected_server_and_client_session(app._mcp_server) as client:
        result = await client.call_tool("greet", {"name": "World"})
        assert not result.isError, f"Tool call returned an error: {result.content}"
        assert len(result.content) == 1
        assert result.content[0].text == "Hello World, hope you are having a great day!"


async def test_greet_tool_empty_name():
    """
    Tests that the 'greet' tool returns an error when the name is empty.
    """
    async with create_connected_server_and_client_session(app._mcp_server) as client:
        result = await client.call_tool("greet", {"name": ""})
        assert result.isError
        assert "Name cannot be empty." in result.content[0].text


async def test_intentional_error_tool():
    """
    Tests the 'intentional_error' tool to ensure it returns an error.
    """
    async with create_connected_server_and_client_session(app._mcp_server) as client:
        result = await client.call_tool("intentional_error", {})
        assert result.isError
        assert "This is a simulated error." in result.content[0].text

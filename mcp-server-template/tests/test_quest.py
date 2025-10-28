# tests/test_quest.py
import pytest
from pydantic import AnyUrl

from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import GetPromptResult, TextContent, TextResourceContents

# Import the app instance which has all primitives registered
from mcp_server_template.app import app

pytestmark = pytest.mark.asyncio

async def test_full_quest_end_to_end():
    """
    Tests the entire 'treasure hunt' workflow, ensuring that an agent
    can use resources and tools in sequence to achieve the final goal.
    """
    async with create_connected_server_and_client_session(app._mcp_server) as client:
        # --- Step 1: Get the first key from the resource template ---
        uri_key1 = "document://archive/007"
        result1 = await client.read_resource(AnyUrl(uri_key1))
        content1 = result1.contents[0]
        assert isinstance(content1, TextResourceContents)
        assert content1.text == "key 1: abaco42"
        key1 = content1.text.split(": ")[1]

        # --- Step 2: Get the second key from the first tool ---
        result2 = await client.call_tool("get_second_key", {})
        content2 = result2.content[0]
        assert isinstance(content2, TextContent)
        assert content2.text == "key 2: gatto_matto"
        key2 = content2.text.split(": ")[1]

        # --- Step 3: Use the second key to get the third key ---
        result3 = await client.call_tool("use_second_key", {"key2": key2})
        content3 = result3.content[0]
        assert isinstance(content3, TextContent)
        assert content3.text == "key 3: 123stella"
        key3 = content3.text.split(": ")[1]

        # --- Step 4: Use all three keys to get the secret phrase ---
        result4 = await client.call_tool(
            "use_all_keys",
            {"key1": key1, "key2": key2, "key3": key3}
        )
        content4 = result4.content[0]
        assert isinstance(content4, TextContent)
        assert content4.text == "the meaning of MCP is long live collapsed chickens"

async def test_prompts_are_registered_and_work():
    """
    Tests that the new prompts are correctly registered and return the expected structure.
    """
    async with create_connected_server_and_client_session(app._mcp_server) as client:
        # Check that prompts are listed
        list_result = await client.list_prompts()
        prompt_names = {p.name for p in list_result.prompts}
        assert "vampire_story_prompt" in prompt_names
        assert "summarize_conversation_prompt" in prompt_names
        assert "roleplay_character_prompt" in prompt_names

        # Test the role-playing prompt for its multi-message structure
        result = await client.get_prompt(
            "roleplay_character_prompt",
            {"character": "Sherlock Holmes", "context": "the case of the missing canary"}
        )
        assert isinstance(result, GetPromptResult)
        assert len(result.messages) == 2
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"
        assert "Sherlock Holmes" in result.messages[0].content.text

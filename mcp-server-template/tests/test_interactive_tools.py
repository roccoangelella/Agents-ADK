# tests/test_interactive_tools.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp.server.fastmcp import Context
from mcp.types import ElicitResult, CreateMessageResult, TextContent

from mcp_server_template.tools.interactive_tools import confirm_action, generate_haiku
from mcp_server_template.schemas import ConfirmationSchema


@pytest.mark.asyncio
async def test_confirm_action_accepted():
    """Test confirm_action tool when user accepts."""
    # Mock context with elicit method
    mock_ctx = AsyncMock(spec=Context)
    
    # Mock confirmation data
    confirmation_data = MagicMock()
    confirmation_data.confirm = True
    
    # Mock elicit result for accepted action
    mock_elicit_result = MagicMock(spec=ElicitResult)
    mock_elicit_result.action = "accept"
    mock_elicit_result.data = confirmation_data
    
    mock_ctx.elicit.return_value = mock_elicit_result
    
    action_description = "delete all temporary files"
    result = await confirm_action(action_description=action_description, ctx=mock_ctx)
    
    # Verify elicit was called with correct parameters
    mock_ctx.elicit.assert_called_once()
    call_args = mock_ctx.elicit.call_args
    assert action_description in call_args.kwargs['message']
    assert call_args.kwargs['schema'] == ConfirmationSchema
    
    # Verify result
    assert "Action confirmed" in result
    assert action_description in result


@pytest.mark.asyncio
async def test_confirm_action_declined():
    """Test confirm_action tool when user declines."""
    mock_ctx = AsyncMock(spec=Context)
    
    # Mock confirmation data with decline
    confirmation_data = MagicMock()
    confirmation_data.confirm = False
    
    mock_elicit_result = MagicMock(spec=ElicitResult)
    mock_elicit_result.action = "accept"
    mock_elicit_result.data = confirmation_data
    
    mock_ctx.elicit.return_value = mock_elicit_result
    
    action_description = "format hard drive"
    result = await confirm_action(action_description=action_description, ctx=mock_ctx)
    
    # Verify result
    assert "Action cancelled" in result
    assert action_description in result


@pytest.mark.asyncio
async def test_confirm_action_cancelled():
    """Test confirm_action tool when user cancels."""
    mock_ctx = AsyncMock(spec=Context)
    
    # Mock elicit result for cancelled action
    mock_elicit_result = MagicMock(spec=ElicitResult)
    mock_elicit_result.action = "cancel"
    mock_elicit_result.data = None
    
    mock_ctx.elicit.return_value = mock_elicit_result
    
    action_description = "send email"
    result = await confirm_action(action_description=action_description, ctx=mock_ctx)
    
    # Verify result
    assert "Action cancelled" in result
    assert action_description in result


@pytest.mark.asyncio
async def test_generate_haiku_success():
    """Test generate_haiku tool with successful generation."""
    mock_ctx = AsyncMock(spec=Context)
    
    # Mock session and sampling result
    mock_session = AsyncMock()
    mock_ctx.session = mock_session
    
    # Mock successful haiku generation
    expected_haiku = "Cherry blossoms fall\nGentle breeze carries petals\nSpring's fleeting beauty"
    
    mock_content = MagicMock(spec=TextContent)
    mock_content.type = "text"
    mock_content.text = expected_haiku
    
    mock_sampling_result = MagicMock(spec=CreateMessageResult)
    mock_sampling_result.content = mock_content
    
    mock_session.create_message.return_value = mock_sampling_result
    
    topic = "cherry blossoms"
    result = await generate_haiku(topic=topic, ctx=mock_ctx)
    
    # Verify create_message was called correctly
    mock_session.create_message.assert_called_once()
    call_args = mock_session.create_message.call_args
    assert call_args.kwargs['max_tokens'] == 100
    
    # Check that the message contains the topic
    messages = call_args.kwargs['messages']
    assert len(messages) == 1
    assert topic in messages[0].content.text
    
    # Verify result
    assert result == expected_haiku


@pytest.mark.asyncio
async def test_generate_haiku_non_text_response():
    """Test generate_haiku tool when LLM doesn't return text."""
    mock_ctx = AsyncMock(spec=Context)
    
    # Mock session
    mock_session = AsyncMock()
    mock_ctx.session = mock_session
    
    # Mock non-text content
    mock_content = MagicMock()
    mock_content.type = "image"  # Not text
    
    mock_sampling_result = MagicMock(spec=CreateMessageResult)
    mock_sampling_result.content = mock_content
    
    mock_session.create_message.return_value = mock_sampling_result
    
    topic = "mountains"
    result = await generate_haiku(topic=topic, ctx=mock_ctx)
    
    # Verify error handling
    assert "Error: Could not generate haiku" in result


@pytest.mark.asyncio
async def test_generate_haiku_with_various_topics():
    """Test generate_haiku tool with different topics."""
    mock_ctx = AsyncMock(spec=Context)
    
    mock_session = AsyncMock()
    mock_ctx.session = mock_session
    
    # Mock successful response
    mock_content = MagicMock(spec=TextContent)
    mock_content.type = "text"
    mock_content.text = "A beautiful haiku"
    
    mock_sampling_result = MagicMock(spec=CreateMessageResult)
    mock_sampling_result.content = mock_content
    
    mock_session.create_message.return_value = mock_sampling_result
    
    topics = ["ocean", "technology", "coding", "winter"]
    
    for topic in topics:
        result = await generate_haiku(topic=topic, ctx=mock_ctx)
        
        # Verify the topic was included in the prompt
        call_args = mock_session.create_message.call_args
        messages = call_args.kwargs['messages']
        assert topic in messages[0].content.text
        
        # Verify we got a result
        assert result == "A beautiful haiku"


@pytest.mark.asyncio
async def test_confirm_action_no_data():
    """Test confirm_action tool when elicit returns no data."""
    mock_ctx = AsyncMock(spec=Context)
    
    mock_elicit_result = MagicMock(spec=ElicitResult)
    mock_elicit_result.action = "accept"
    mock_elicit_result.data = None
    
    mock_ctx.elicit.return_value = mock_elicit_result
    
    action_description = "backup database"
    result = await confirm_action(action_description=action_description, ctx=mock_ctx)
    
    # Should treat no data as cancelled
    assert "Action cancelled" in result
    assert action_description in result
# tests/test_advanced_tools.py
import pytest
from unittest.mock import AsyncMock
from mcp.server.fastmcp import Context

from mcp_server_template.tools.advanced_tools import long_running_task
from mcp_server_template.schemas import TaskStatusResponse


@pytest.mark.asyncio
async def test_long_running_task():
    """Test the long_running_task tool with a small number of steps."""
    # Mock context
    mock_ctx = AsyncMock(spec=Context)
    mock_ctx.request_id = "test-123"
    mock_ctx.info = AsyncMock()
    mock_ctx.report_progress = AsyncMock()
    
    # Test with 2 steps to keep test fast
    steps = 2
    result = await long_running_task(steps=steps, ctx=mock_ctx)
    
    # Verify result structure
    assert isinstance(result, TaskStatusResponse)
    assert result.status == "Completed"
    assert result.steps_completed == steps
    assert result.duration_seconds > 0
    
    # Verify context methods were called
    assert mock_ctx.info.call_count == steps
    assert mock_ctx.report_progress.call_count == steps
    
    # Verify progress calls were made correctly
    progress_calls = mock_ctx.report_progress.call_args_list
    for i, call in enumerate(progress_calls):
        args, kwargs = call
        assert kwargs['progress'] == i + 1
        assert kwargs['total'] == steps
        assert f"step {i + 1}" in kwargs['message'].lower()


@pytest.mark.asyncio
async def test_long_running_task_single_step():
    """Test the long_running_task tool with a single step."""
    mock_ctx = AsyncMock(spec=Context)
    mock_ctx.request_id = "test-456"
    mock_ctx.info = AsyncMock()
    mock_ctx.report_progress = AsyncMock()
    
    result = await long_running_task(steps=1, ctx=mock_ctx)
    
    assert isinstance(result, TaskStatusResponse)
    assert result.status == "Completed"
    assert result.steps_completed == 1
    assert result.duration_seconds > 0
    
    # Should have exactly one call each
    assert mock_ctx.info.call_count == 1
    assert mock_ctx.report_progress.call_count == 1


@pytest.mark.asyncio
async def test_long_running_task_zero_steps():
    """Test the long_running_task tool with zero steps."""
    mock_ctx = AsyncMock(spec=Context)
    mock_ctx.request_id = "test-789"
    mock_ctx.info = AsyncMock()
    mock_ctx.report_progress = AsyncMock()
    
    result = await long_running_task(steps=0, ctx=mock_ctx)
    
    assert isinstance(result, TaskStatusResponse)
    assert result.status == "Completed"
    assert result.steps_completed == 0
    assert result.duration_seconds >= 0
    
    # Should have no calls for zero steps
    assert mock_ctx.info.call_count == 0
    assert mock_ctx.report_progress.call_count == 0


@pytest.mark.asyncio
async def test_long_running_task_progress_values():
    """Test that progress values are correctly calculated."""
    mock_ctx = AsyncMock(spec=Context)
    mock_ctx.request_id = "test-progress"
    mock_ctx.info = AsyncMock()
    mock_ctx.report_progress = AsyncMock()
    
    steps = 3
    await long_running_task(steps=steps, ctx=mock_ctx)
    
    # Check that progress values go from 1 to steps
    progress_calls = mock_ctx.report_progress.call_args_list
    for i, call in enumerate(progress_calls):
        args, kwargs = call
        expected_progress = i + 1
        assert kwargs['progress'] == expected_progress
        assert kwargs['total'] == steps
        assert kwargs['progress'] <= steps
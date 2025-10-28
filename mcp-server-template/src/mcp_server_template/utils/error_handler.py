# src/mcp_server_template/utils/error_handler.py
import functools
import logging
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

T_Callable = Callable[..., Coroutine[Any, Any, Any]]

def handle_tool_errors(func: T_Callable) -> T_Callable:
    """
    Decorator that catches and logs exceptions in tool functions,
    then re-raises them to be handled by the FastMCP framework.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception:
            tool_name = func.__name__
            logger.exception(f"Error executing tool '{tool_name}'")
            # Re-raise the exception to let FastMCP handle the error response.
            raise
    return wrapper

# src/mcp_server_template/app.py
import logging
from mcp.server.fastmcp import FastMCP
from .config import settings

logger = logging.getLogger(__name__)

# This central 'app' instance is imported by all primitive modules.
# Decorators used in those modules register the primitives here.
app = FastMCP(
    name=settings.SERVER_NAME,
    instructions="A server built from the modular MCP template."
)

logger.info(f"FastMCP app '{settings.SERVER_NAME}' created.")

# src/mcp_server_template/server.py
import logging
logger = logging.getLogger(__name__)

# 1. Import and load settings first.
from .config import settings

# 2. Setup logging based on the loaded settings.
from .logging_config import setup_logging
setup_logging(settings)

# 3. Import the central app instance.
from .app import app

# 4. Import primitive packages to trigger their registration.
#    The __init__.py files in these packages will automatically
#    import all modules within them.
#    This server will work even if some of these directories are empty.
try:
    from . import tools
except ImportError:
    logging.warning("No 'tools' package found or it is empty.")
try:
    from . import resources
except ImportError:
    logging.warning("No 'resources' package found or it is empty.")
try:
    from . import prompts
except ImportError:
    logging.warning("No 'prompts' package found or it is empty.")

def main() -> None:
    """
    Main entry point to run the MCP server.
    """
    logger.info(f"Starting MCP server '{settings.SERVER_NAME}'...")
    # FastMCP's run() method handles the stdio transport by default.
    app.run()

if __name__ == "__main__":
    main()

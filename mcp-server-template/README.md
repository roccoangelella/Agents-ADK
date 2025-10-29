# MCP Server Template (Python)

This project is a robust and well-structured template for creating Python-based MCP (Model Context Protocol) servers using the `FastMCP` framework. It serves as a comprehensive starting point, demonstrating best practices for configuration, logging, error handling, and modular design.

## Features

-   **Modern Framework**: Built on `FastMCP` for clean, Pythonic, and decorator-based code.
-   **Modular by Design**: Primitives (Tools, Resources, Prompts) are organized into separate packages. Adding a new primitive is as simple as adding a new Python file.
-   **Automatic Discovery**: The server automatically discovers and registers all primitives defined in the `tools/`, `resources/`, and `prompts/` directories.
-   **Configuration-Driven**: Server settings like name and log level are managed via a `.env` file and validated at startup with Pydantic.
-   **Robust Error Handling**: A central decorator catches tool exceptions, preventing server crashes and ensuring graceful error reporting to the client.
-   **Advanced Logging**: Dual logging to a colored console (for development) and a rotating file (for persistence), configured via `.env`.
-   **Structured Data**: Includes examples of using Pydantic models for structured tool inputs and outputs.
-   **Test Suite**: Comes with a `pytest` suite demonstrating how to test primitives in-memory.

## Project Structure

```
mcp-server-template/
├── src/
│   └── mcp_server_template/
│       ├── app.py              # Central FastMCP app instance
│       ├── server.py           # Main server entry point
│       ├── config.py           # Pydantic settings management
│       ├── logging_config.py   # Logging setup
│       ├── schemas.py          # Pydantic data models
│       ├── utils/
│       │   └── error_handler.py# Centralized error handling decorator
│       ├── tools/              # Package for tool modules
│       │   └── __init__.py     # Enables auto-discovery
│       ├── resources/          # Package for resource modules
│       └── prompts/            # Package for prompt modules
├── tests/
├── .env.example                # Environment file template
├── logs/                       # Directory for log files
└── pyproject.toml              # Poetry project configuration
```

## Installation

This project is managed with [Poetry](https://python-poetry.org/).

1.  **Clone the repository**:
    ```bash
    git clone <your-repository-url>
    cd mcp-server-template
    ```

2.  **Install dependencies**:
    This command will create a virtual environment and install all necessary packages.
    ```bash
    poetry install
    ```

3.  **Configure your environment**:
    Copy the example environment file and customize it if needed.
    ```bash
    cp .env.example .env
    ```

## Usage

### 1. Running with the MCP Inspector (Recommended for Debugging)

The MCP Inspector is the best tool for testing your server in isolation.

```bash
poetry run mcp dev src/mcp_server_template/server.py
```

This command starts the server and opens a web interface where you can manually call tools, read resources, and get prompts.

### 2. Running the Server Directly

You can run the server directly for integration with an MCP client like Claude Desktop.

```bash
poetry run python src/mcp_server_template/server.py
```

### 3. Running Automated Tests

To verify that all primitives are working as expected, run the test suite:

```bash
poetry run pytest
```

## How to Extend the Template

This template is designed for easy extension.

-   **To Add a New Tool**: Create a new file (e.g., `my_new_tool.py`) inside the `src/mcp_server_template/tools/` directory. Import the `app` instance and the error handler, then define your tool with the ` @app.tool()` decorator. It will be registered automatically.

    ```python
    # src/mcp_server_template/tools/my_new_tool.py
    from ..app import app
    from ..utils.error_handler import handle_tool_errors

    @app.tool() @handle_tool_errors
    async def my_new_feature(param: str) -> str:
        # Your logic here
        return f"Processed {param}"
    ```

-   **To Add a New Resource or Prompt**: Follow the same pattern, adding a new file to the `resources/` or `prompts/` directory respectively.

-   **To Add a New Pydantic Schema**: Define your `BaseModel` in `src/mcp_server_template/schemas.py` and import it where needed.
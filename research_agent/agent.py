from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url='http://127.0.0.1:8080/mcp')
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions by launching your tools',
    tools=[mcp_toolset]
)

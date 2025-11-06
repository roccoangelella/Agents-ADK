from fastmcp import FastMCP
from utils.rag import retrieve
mcp=FastMCP(
    name='My MCP Server'
)

@mcp.tool()
def _retrieve(prompt:str):
    """ Calls a retrieval function to retrieve files content from vector db """
    chunks_text=""
    for chunk in retrieve(prompt):
        chunks_text+=chunk
    return chunks_text

if __name__=='__main__':
    mcp.run(
        transport="streamable-http",
        port=8080,
        host="127.0.0.1",
        log_level="INFO"
    )

#python -m MCP_server.server
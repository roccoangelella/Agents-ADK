from fastmcp import FastMCP


mcp=FastMCP(
    name='My MCP Server'
)



if __name__=='__main__':
    mcp.run(
        transport="streamable-http",
        port=8080,
        host="127.0.0.1",
        log_level="INFO"
    )

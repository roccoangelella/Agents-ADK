from fastmcp import FastMCP
from utils.rag import retrieve
import os

mcp=FastMCP(
    name='My MCP Server'
)

@mcp.tool()
def retrieve_text(prompt: str)->str:
    """
    Retrieves relevant text chunks from a vector database 
    based on the user's prompt. Use this tool to find specific 
    information to answer a question.
    """
    chunks_text=""
    for chunk in retrieve(prompt):
        chunks_text+=chunk
    return chunks_text

@mcp.tool()
def search_file_name()->list[str]:
    """
    Gets a list of all available file paths from the DOCS folder.
    Launch only if the user specified a file name or explicitly mentioned a file in his prompt, as this list will be used by the LLM to select the correct file.
    """
    filenames=[]
    for dirpath,_,files in list(os.walk('./DOCS')):
        for file in files:
            if file.endswith(('.pdf','.txt','.doc','.docx','.epub','.odt','.pptx')):
                full_path=os.path.join(dirpath, file)
                norm_full_path=full_path.replace(os.path.sep, '/')
                filenames.append(norm_full_path)
    if not filenames:
        print("[Debug] No files found in ./DOCS directory.")
        return []
    return filenames

if __name__=='__main__':
    mcp.run(
        transport="streamable-http",
        port=8081,
        host="127.0.0.1",
        log_level="INFO"
    )

#python -m MCP_server.server
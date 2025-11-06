# Agents-ADK

This repository contains an agent, an MCP server, a FastAPI backend, and a small frontend built with Vite + React.

## Quick frontend setup (Windows PowerShell)

From the repository root run:

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`, so the frontend sends requests to `/api/query` which maps to the backend `POST /query` endpoint.

## Running backend & MCP server (examples)

Start the FastAPI backend (run from repo root):

```powershell
# In a separate terminal, start the FastAPI backend (uvicorn)
# adjust the module path if needed
uvicorn backend_fastapi.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the MCP server (if needed):

```powershell
# In another terminal
python -m MCP_server.server
```

If you see CORS or connection errors, ensure the backend is running on port 8000 and that no firewall is blocking local connections.

## Troubleshooting
- If the frontend shows a white screen: open the browser devtools (F12) and check console/network for errors.
- If `/api/query` returns 422 or similar, confirm the backend `POST /query` accepts JSON body {"query": "..."}.
- If the MCP tools are not detected, ensure the MCP server is running on port 8080 and that the agent is pointed to `http://127.0.0.1:8080/mcp`.

---
Edited to add a minimal Vite + React frontend and instructions.
#### Launch
taskkill /IM python.exe /F; honcho start
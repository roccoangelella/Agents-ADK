"""
Modulo didattico per i tool di base di un server MCP.

Questo file contiene esempi dei tool più semplici ma fondamentali, che dimostrano
i concetti di base:
1.  Introspezione del server.
2.  Gestione di input e output.
3.  Output strutturato tramite Pydantic.
4.  Gestione centralizzata degli errori.
"""
import logging
from mcp.server.fastmcp import Context
from ..app import app
from ..schemas import ServerStatusResponse
from ..utils.error_handler import handle_tool_errors

logger = logging.getLogger(__name__)

# --- ESEMPIO DIDATTICO: Introspezione del Server e Output Strutturato ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare come un tool possa accedere allo stato del proprio server e come
#   restituire dati complessi in un formato strutturato e prevedibile.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Output Strutturato**: Il protocollo MCP incoraggia l'uso di output strutturati
#     (JSON) piuttosto che testo libero. Questo tool restituisce un modello Pydantic
#     (`ServerStatusResponse`), che FastMCP serializza automaticamente in JSON.
#     Il client riceve così dati facili da analizzare programmaticamente.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Separazione dei Modelli (Schemas)**: La definizione di `ServerStatusResponse`
#     è in un file separato (`schemas.py`), mantenendo la definizione dei dati
#     disaccoppiata dalla logica di business. Questo è un buon pattern per la
#     manutenibilità.
#
@app.tool()
@handle_tool_errors
async def server_status(ctx: Context) -> ServerStatusResponse:
    """
    Restituisce lo stato corrente e le statistiche del server, come il numero
    di tool, risorse e prompt disponibili.
    """
    logger.info(f"Executing 'server_status' (Request ID: {ctx.request_id})")
    
    # PATTERN: Accesso all'istanza App.
    # L'oggetto 'app' di FastMCP è il punto centrale dove sono registrati tutti
    # i primitivi. Un tool può ispezionarlo per fornire metadati su se stesso.
    return ServerStatusResponse(
        server_name=app.name,
        instructions=app.instructions,
        tools_available=len(app._tool_manager.list_tools()),
        resources_available=len(app._resource_manager.list_resources()),
        resource_templates=len(app._resource_manager.list_templates()),
        prompts_available=len(app._prompt_manager.list_prompts()),
    )

# --- ESEMPIO DIDATTICO: Tool di Base con Input ---
#
# [SCOPO DIDATTICO]:
#   Illustrare il modo più semplice per creare un tool che accetta parametri.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Generazione Automatica di `inputSchema`**: FastMCP analizza la firma della
#     funzione Python (inclusi i type hint come `name: str`) e genera
#     automaticamente il JSON Schema per il campo `inputSchema` del tool.
#     Questo astrae la complessità della specifica MCP.
#
@app.tool()
@handle_tool_errors
async def greet(name: str) -> str:
    """
    Invia un saluto personalizzato utilizzando il nome fornito come parametro.
    """
    logger.info(f"Executing 'greet' for '{name}'")
    if not name:
        # PATTERN: Validazione di Business Logic.
        # Oltre alla validazione dei tipi fatta da FastMCP, i tool dovrebbero
        # implementare la propria logica di validazione.
        raise ValueError("Name cannot be empty.")
    return f"Hello {name}, hope you are having a great day!"

# --- ESEMPIO DIDATTICO: Gestione Centralizzata degli Errori ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare un pattern robusto per la gestione delle eccezioni nei tool.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Risposte di Errore**: Se un tool fallisce, il server deve comunicarlo
#     al client tramite una risposta di errore JSON-RPC standard. FastMCP
#     gestisce automaticamente la formattazione dell'errore se un'eccezione
#     non viene catturata all'interno del tool.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Decoratore per la Gestione degli Errori**: Invece di usare un blocco
#     try/except in ogni tool, abbiamo creato un decoratore (`@handle_tool_errors`).
#     Questo centralizza la logica di logging degli errori e garantisce un
#     comportamento coerente in tutto il server, rendendo il codice dei tool
#     più pulito e focalizzato sulla logica di business.
#
@app.tool()
@handle_tool_errors
async def intentional_error() -> str:
    """
    Un tool progettato per fallire sempre, al fine di dimostrare come
    il server gestisce e riporta gli errori al client.
    """
    logger.warning("Executing 'intentional_error' tool.")
    raise RuntimeError("This is a simulated error.")
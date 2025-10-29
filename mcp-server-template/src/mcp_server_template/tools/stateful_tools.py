"""
Modulo didattico per dimostrare la gestione dello stato in un server MCP.

Questo file contiene esempi di tool che non sono stateless, ma mantengono
informazioni tra una chiamata e l'altra all'interno della stessa sessione client.
Questo è il concetto fondamentale che distingue un semplice server di tool da un
server "comportamentale" o "agentico".
"""
import logging
from datetime import datetime, timezone

from mcp.server.fastmcp import Context

from ..app import app
from ..schemas import SessionInfoResponse
from ..state import state_manager
from ..utils.error_handler import handle_tool_errors

logger = logging.getLogger(__name__)

# --- ESEMPIO DIDATTICO: Gestione dello Stato di Sessione ---
#
# [SCOPO DIDATTICO]:
#   Introdurre il concetto FONDAMENTALE di stato di sessione lato server.
#   Un server comportamentale deve "ricordare" le interazioni passate
#   con un client per poter modificare il suo comportamento futuro.
#
# [CONCETTO MCP ILLUSTRATO]:
#   Il protocollo MCP è fondamentalmente stateless a livello di trasporto (HTTP).
#   Tuttavia, il SDK fornisce un oggetto `Context` (`ctx`) per ogni richiesta,
#   che contiene un riferimento alla sessione di connessione. Questo tool dimostra
#   come usare un identificatore univoco di quella sessione per associare
#   i dati a un client specifico in un gestore di stato esterno (`StateManager`).
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Singleton**: Lo `state_manager` è un'istanza unica che agisce come
#     un database in-memory per tutti gli stati di sessione.
#   - **Dependency Injection**: Il framework FastMCP inietta l'oggetto `Context`
#     nel tool, fornendo l'accesso necessario per identificare la sessione.
#
@app.tool(title="Get Session Info")
@handle_tool_errors
async def session_info(ctx: Context) -> SessionInfoResponse:
    """
    Recupera informazioni sulla sessione corrente, incluso un contatore
    che si incrementa ad ogni chiamata. Utile per il debug e per verificare
    la continuità della sessione.
    """
    # PATTERN: Chiave di Sessione In-Memory.
    # Per identificare una sessione in modo univoco all'interno del server,
    # usiamo l'indirizzo di memoria dell'oggetto `session` (`id()`).
    # Questo è un metodo robusto e semplice per lo stato in-memory.
    session_key = id(ctx.request_context.session)
    logger.info(f"Executing 'session_info' for session_key: {session_key}")

    # L'interazione con lo StateManager disaccoppia la logica di gestione dello stato
    # dalla logica del tool stesso.
    state_manager.increment_call_count(session_key)
    session_state = state_manager.get_or_create_session(session_key)

    duration = (datetime.now(timezone.utc) - session_state.created_at).total_seconds()

    # PATTERN: Output Strutturato.
    # La restituzione di un modello Pydantic garantisce un output JSON strutturato,
    # validato e auto-documentante, più facile da elaborare per un client.
    return SessionInfoResponse(
        session_id=str(session_state.session_key),
        created_at=session_state.created_at,
        call_count=session_state.call_count,
        session_duration_seconds=round(duration, 2),
    )
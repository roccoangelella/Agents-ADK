"""
Modulo didattico per la gestione di task asincroni e complessi.

Questo file contiene esempi di tool che simulano operazioni a lunga esecuzione,
mostrando come gestire la comunicazione asincrona e fornire feedback all'utente
tramite le notifiche di avanzamento di MCP.
"""
import asyncio
import logging
import time

from mcp.server.fastmcp import Context

from ..app import app
from ..schemas import TaskStatusResponse
from ..utils.error_handler import handle_tool_errors

logger = logging.getLogger(__name__)

# --- ESEMPIO DIDATTICO: Notifiche di Avanzamento per Task Asincroni ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare come un tool possa gestire un'operazione che richiede tempo
#   senza bloccare il server e fornendo al contempo un feedback in tempo reale
#   al client.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Notifiche di Avanzamento (`notifications/progress`)**: Il protocollo MCP
#     prevede un meccanismo di notifica "out-of-band" (fuori banda). Il server
#     può inviare messaggi di avanzamento al client senza attendere la fine
#     dell'esecuzione del tool. La funzione `ctx.report_progress()` astrae
#     la creazione di questi messaggi.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Funzione Asincrona (`async def`)**: L'uso di `async def` è fondamentale.
#     Permette al tool di cedere il controllo al loop di eventi del server
#     durante le attese (simulate qui con `asyncio.sleep`), consentendo al
#     server di gestire altre richieste contemporaneamente.
#   - **Feedback Continuo**: Inviare aggiornamenti a intervalli regolari
#     migliora drasticamente l'esperienza utente per operazioni lunghe,
#     evitando che il client pensi che il server si sia bloccato.
#
@app.tool(title="Long Running Task")
@handle_tool_errors
async def long_running_task(steps: int, ctx: Context) -> TaskStatusResponse:
    """
    Simula un'operazione a lunga esecuzione (es. un'analisi dati)
    e invia aggiornamenti di avanzamento periodici al client.
    """
    logger.info(f"Executing 'long_running_task' for {steps} steps.")
    start_time = time.monotonic()
    
    for i in range(steps):
        # Simula una parte del lavoro
        await asyncio.sleep(1)
        
        # Invia un log informativo visibile nei log del client (es. Claude Desktop)
        await ctx.info(f"Processing step {i + 1}/{steps}...")
        
        # MCP Concept: Notifica di Avanzamento.
        # Questa chiamata invia un messaggio `notifications/progress` al client.
        # È una chiamata "fire-and-forget"; il server non attende una risposta
        # e prosegue immediatamente con l'esecuzione.
        await ctx.report_progress(
            progress=i + 1,
            total=steps,
            message=f"Completed step {i + 1} of {steps}",
        )

    duration = time.monotonic() - start_time
    logger.info(f"Task completed in {duration:.2f} seconds.")
    
    return TaskStatusResponse(
        status="Completed",
        duration_seconds=round(duration, 2),
        steps_completed=steps
    )
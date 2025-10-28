"""
Modulo didattico per tool di utilità stateless.

Questo file contiene esempi di tool "puri": ricevono un input, eseguono
un'operazione senza effetti collaterali (side-effects) e restituiscono un output.
Sono un ottimo esempio di come esporre semplici funzionalità di calcolo o
trasformazione dati tramite MCP.

Il focus principale qui è dimostrare l'uso di Pydantic per definire
output strutturati, una best practice fondamentale in MCP.
"""
import logging
from datetime import datetime, timezone

from ..app import app
from ..schemas import CharCountResponse, CurrentTimeResponse, SumResponse
from ..utils.error_handler import handle_tool_errors

logger = logging.getLogger(__name__)

# --- ESEMPIO DIDATTICO: Output Strutturato con Pydantic ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare come definire e restituire un output strutturato complesso
#   utilizzando un modello Pydantic.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Output Strutturato (`structuredContent`)**: Il protocollo MCP (versione 2025-06-18
#     e successive) supporta un campo `structuredContent` nella risposta di un tool.
#     FastMCP popola automaticamente questo campo quando un tool restituisce un'istanza
#     di un modello Pydantic.
#   - **Generazione Automatica di `outputSchema`**: FastMCP analizza il type hint
#     del valore di ritorno della funzione (es. `-> SumResponse`) e genera
#     automaticamente il JSON Schema corrispondente nel campo `outputSchema`
#     del tool. Questo permette al client di sapere in anticipo quale struttura
#     di dati aspettarsi.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Data Transfer Object (DTO)**: I modelli Pydantic come `SumResponse` agiscono
#     come DTO, definendo un contratto dati chiaro tra il server e il client.
#     Questo migliora la robustezza e la manutenibilità dell'integrazione.
#
@app.tool()
@handle_tool_errors
async def sum(a: float, b: float) -> SumResponse:
    """
    Somma due valori numerici e restituisce un output strutturato
    contenente gli operandi e il risultato.
    """
    result = a + b
    logger.info(f"Executing 'sum': {a} + {b} = {result}")
    
    # MCP Concept: Restituendo un'istanza di SumResponse, FastMCP genererà
    # sia il `content` testuale (per retrocompatibilità) sia il `structuredContent`
    # JSON, che è il modo preferito per i client moderni di ricevere dati.
    return SumResponse(a=a, b=b, sum=result)

# --- ESEMPIO DIDATTICO: Input Semplice, Output Strutturato ---
#
# [SCOPO DIDATTICO]:
#   Rinforzare il concetto di output strutturato con un altro esempio pratico.
#
@app.tool()
@handle_tool_errors
async def count_characters(word: str) -> CharCountResponse:
    """
    Conta i caratteri nella stringa fornita e restituisce la stringa
    originale e la sua lunghezza in un formato strutturato.
    """
    length = len(word)
    logger.info(f"Executing 'count_characters': '{word}' -> {length}")
    return CharCountResponse(word=word, length=length)

# --- ESEMPIO DIDATTICO: Tool senza Input, Output Strutturato ---
#
# [SCOPO DIDATTICO]:
#   Mostrare un tool che non richiede parametri di input ma fornisce comunque
#   un output strutturato ricco di informazioni.
#
@app.tool()
@handle_tool_errors
async def current_time() -> CurrentTimeResponse:
    """
    Restituisce la data e l'ora correnti del server in diversi formati
    (ISO UTC, ISO locale, e timestamp Unix), all'interno di un
    oggetto strutturato.
    """
    # PATTERN: Gestione dei fusi orari.
    # È una best practice lavorare con datetime "aware" (consapevoli del fuso orario),
    # specialmente in UTC, per evitare ambiguità.
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone()
    
    payload = CurrentTimeResponse(
        iso_utc=now_utc.isoformat(),
        iso_local=now_local.isoformat(),
        epoch=int(now_utc.timestamp()),
    )
    logger.info(f"Executing 'current_time': {payload.model_dump_json()}")
    return payload
"""
Modulo didattico per dimostrare le funzionalità di comunicazione bidirezionale di MCP.

A differenza dei tool standard (dove la comunicazione è solo client -> server),
i tool in questo modulo mostrano come il server possa inviare le proprie richieste
al client durante l'esecuzione di un tool. Le due principali modalità sono:

1. Elicitazione: Chiedere un input all'utente tramite il client.
2. Sampling: Chiedere all'LLM del client di generare del testo.
"""
import logging

from mcp.server.fastmcp import Context
from mcp.types import SamplingMessage, TextContent

from ..app import app
from ..schemas import ConfirmationSchema
from ..utils.error_handler import handle_tool_errors

logger = logging.getLogger(__name__)

# --- ESEMPIO DIDATTICO: Elicitazione (Server -> Client -> Utente) ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare come un tool possa richiedere attivamente un input o una conferma
#   all'utente, mettendo in pausa la propria esecuzione.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Elicitazione**: Questa è una delle funzionalità più potenti di MCP.
#     Il server invia una richiesta `elicitation/create` al client utilizzando
#     la funzione `ctx.elicit()`. Il client (es. Claude Desktop) è responsabile
#     di gestire questa richiesta, tipicamente mostrando un'interfaccia utente
#     (un pop-up, un form) per raccogliere la risposta.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Flusso di Controllo Asincrono**: La chiamata `await ctx.elicit()` sospende
#     l'esecuzione del tool lato server. Il tool riprenderà solo quando il client
#     avrà inviato una risposta. Questo pattern è essenziale per i workflow interattivi.
#   - **Schema di Risposta**: Lo `schema` Pydantic (`ConfirmationSchema`) definisce
#     il "contratto" per i dati che il server si aspetta di ricevere dall'utente.
#
@app.tool(title="Confirm Action")
@handle_tool_errors
async def confirm_action(action_description: str, ctx: Context) -> str:
    """
    Chiede all'utente una conferma esplicita prima di procedere con un'azione.
    Utile per operazioni importanti o potenzialmente irreversibili.
    """
    logger.info(f"Executing 'confirm_action' for: {action_description}")

    # MCP Concept: Elicitation.
    # La chiamata `await ctx.elicit()` invia una richiesta `elicitation/create`
    # *al client*. Il client gestirà l'interazione con l'utente.
    result = await ctx.elicit(
        message=f"Please confirm if you want to proceed with this action: '{action_description}'",
        schema=ConfirmationSchema,
    )

    # La risposta `ElicitationResult` contiene la scelta dell'utente ('accept', 'decline', 'cancel')
    # e, in caso di 'accept', i dati validati secondo lo schema fornito.
    if result.action == "accept" and result.data and result.data.confirm:
        logger.info(f"User confirmed action: {action_description}")
        return f"Action confirmed: '{action_description}' will proceed."
    else:
        logger.warning(f"User cancelled or declined action: {action_description}")
        return f"Action cancelled: '{action_description}' will not proceed."

# --- ESEMPIO DIDATTICO: Sampling (Server -> Client -> LLM) ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare come un tool possa sfruttare le capacità generative dell'LLM
#   del client per eseguire compiti complessi.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Sampling**: Il server può inviare una richiesta `sampling/createMessage`
#     al client utilizzando `ctx.session.create_message()`. Questa richiesta
#     contiene un prompt e parametri di generazione (es. `max_tokens`).
#     Il client inoltrerà questa richiesta al suo LLM (es. Claude) e restituirà
#     il testo generato al server.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Delega Computazionale**: Invece di avere una propria logica complessa o
#     un proprio LLM, il server delega il compito di generazione al client.
#     Questo rende il tool leggero e potente, sfruttando l'intelligenza già
#     presente nel sistema.
#
@app.tool(title="Generate Haiku")
@handle_tool_errors
async def generate_haiku(topic: str, ctx: Context) -> str:
    """
    Chiede all'LLM del client di generare un haiku su un dato argomento.
    """
    logger.info(f"Executing 'generate_haiku' for topic: {topic}")

    prompt = f"Write a short, creative haiku about '{topic}'."
    
    # MCP Concept: Sampling.
    # Il server invia una richiesta `sampling/createMessage` al client.
    sampling_result = await ctx.session.create_message(
        messages=[SamplingMessage(role="user", content=TextContent(type="text", text=prompt))],
        max_tokens=100,
    )

    if sampling_result.content.type == "text":
        haiku = sampling_result.content.text
        logger.info(f"LLM generated haiku: {haiku}")
        return haiku
    
    logger.error("LLM did not return text content for haiku generation.")
    return "Error: Could not generate haiku."
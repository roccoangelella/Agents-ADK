"""
Modulo didattico per dimostrare un workflow multi-step stateless.

Questi tool implementano una semplice "caccia al tesoro" (quest) che richiede
all'LLM di chiamare più tool in una sequenza specifica per raggiungere un obiettivo.

Questo modulo è un esempio chiave per illustrare un workflow dove lo **stato
viene interamente gestito dal client (l'LLM)**. Il server non ha memoria
delle chiavi già scoperte; si affida all'LLM per conservare e riutilizzare
le informazioni ottenute dalle chiamate precedenti.
"""
import logging

from ..app import app
from ..utils.error_handler import handle_tool_errors

logger = logging.getLogger(__name__)

# --- Costanti del Quest ---
# In un'applicazione reale, queste potrebbero provenire da un file di configurazione o da un database.
KEY_1_VALUE = "abaco42"
KEY_2_FULL = "key 2: gatto_matto"
KEY_2_VALUE = "gatto_matto"
KEY_3_FULL = "key 3: 123stella"
KEY_3_VALUE = "123stella"
SECRET_PHRASE = "the meaning of MCP is long live collapsed chickens"

# --- ESEMPIO DIDATTICO: Tool per un Workflow Stateless ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare il primo passo di un workflow che si basa su chiamate multiple e sequenziali.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Tool come Blocchi di un Workflow**: I tool possono essere progettati per essere
#     i singoli passaggi di un processo più complesso. L'orchestrazione di questi
#     passaggi è affidata all'intelligenza dell'LLM client.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Statelessness**: Questo tool è completamente stateless. Non sa se l'utente
#     ha già ottenuto altre chiavi o se è la prima volta che viene chiamato.
#     Restituisce sempre lo stesso valore, lasciando al client la responsabilità
#     di memorizzare il risultato.
#
@app.tool(title="Get Second Key")
@handle_tool_errors
async def get_second_key() -> str:
    """
    Restituisce la seconda chiave segreta necessaria per completare il quest.
    Questo tool non richiede parametri.
    """
    logger.info("Executing 'get_second_key'.")
    return KEY_2_FULL

# --- ESEMPIO DIDATTICO: Tool con Logica di Validazione Semplice ---
#
# [SCOPO DIDATTICO]:
#   Mostrare un tool che richiede un input (ottenuto da un passo precedente)
#   per sbloccare l'informazione successiva.
#
@app.tool(title="Use Second Key")
@handle_tool_errors
async def use_second_key(key2: str) -> str:
    """
    Accetta la seconda chiave come input e, se corretta, restituisce la terza chiave.
    """
    logger.info("Executing 'use_second_key' with provided key.")
    # Anche questo tool è stateless. La validazione dipende solo dall'input immediato.
    if key2 == KEY_2_VALUE:
        return KEY_3_FULL
    else:
        return "Wrong key 2. Try again."

# --- ESEMPIO DIDATTICO: Tool Finale di un Workflow ---
#
# [SCOPO DIDATTICO]:
#   Illustrare il passo conclusivo di un workflow, che aggrega i risultati
#   dei passi precedenti.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Orchestrazione da parte dell'LLM**: Questo tool si aspetta che l'LLM abbia
#     raccolto e memorizzato correttamente le tre chiavi dai passi precedenti
#     (la prima da una risorsa, le altre due da altri tool) e le fornisca
#     tutte insieme. Questo evidenzia il ruolo dell'LLM come orchestratore
#     di un piano complesso.
#
@app.tool(title="Use All Keys")
@handle_tool_errors
async def use_all_keys(key1: str, key2: str, key3: str) -> str:
    """
    Accetta tutte e tre le chiavi e, se sono corrette, restituisce la frase segreta finale.
    """
    logger.info("Executing 'use_all_keys' with three keys.")
    if (key1 == KEY_1_VALUE and
        key2 == KEY_2_VALUE and
        key3 == KEY_3_VALUE):
        return SECRET_PHRASE
    else:
        return "One or more keys are wrong. Try again."
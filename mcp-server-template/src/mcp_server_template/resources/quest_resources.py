"""
Modulo didattico per dimostrare le Risorse in MCP.

Questo file contiene esempi di due tipi fondamentali di Risorse:
1.  **Risorsa Statica**: Un URI fisso che restituisce sempre lo stesso contenuto.
2.  **Risorsa Template (Dinamica)**: Un URI parametrico che restituisce contenuti
    diversi in base ai parametri forniti.

Le risorse sono il meccanismo primario con cui un server espone dati
"read-only" a un client MCP.
"""
import logging
from typing import Dict

from ..app import app

logger = logging.getLogger(__name__)

# --- Dati di Esempio ---
# Questa struttura dati simula un piccolo database o un archivio di documenti
# a cui la nostra risorsa template può accedere.
SECRET_ARCHIVE: Dict[str, str] = {
    "007": "key 1: abaco42",
    "42": "The answer is within you, but it's the wrong one.",
    "314": "Pi begins here, but it doesn't end.",
    "101": "This is room 101; what you're looking for is not here.",
    "867": "For a good time, call Jenny.",
    "5309": "This number has no special meaning.",
    "2046": "A story of unspoken love and missed connections.",
    "1984": "Big Brother is watching this document.",
    "2001": "I'm sorry, Dave. I'm afraid I can't give you that key.",
    "1337": "Only true hackers can find meaning here.",
}

# --- ESEMPIO DIDATTICO: Risorsa Statica ---
#
# [SCOPO DIDATTICO]:
#   Illustrare il tipo più semplice di risorsa: una risorsa statica con un URI fisso.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Risorsa Statica**: Una risorsa è definita "statica" quando il suo URI non
#     contiene parametri. Ogni richiesta a `info://missione/guida` restituirà
#     sempre lo stesso contenuto. È ideale per esporre documenti, guide, o
#     file di configurazione.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Funzione senza Parametri**: La funzione decorata da `@app.resource` non
#     accetta argomenti, poiché l'URI è fisso e non ci sono parametri da estrarre.
#
@app.resource("info://missione/guida", title="Mission Guide")
def mission_guide() -> str:
    """
    Fornisce una guida statica che spiega lo scopo del 'quest' di questo server.
    """
    logger.info("Accessing static resource 'mission_guide'")
    return (
        "Welcome, Agent. Your mission is to uncover the secret phrase. "
        "You will need to find three keys by interacting with this server's primitives. "
        "Start by searching the document archive for document '007'. "
        "Use all available tools and prompts to guide you. Good luck."
    )

# --- ESEMPIO DIDATTICO: Risorsa Template (Dinamica) ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare una risorsa dinamica il cui contenuto dipende da un parametro
#   passato nell'URI.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Risorsa Template**: L'URI `document://archive/{document_id}` contiene un
#     segnaposto (`{document_id}`). FastMCP riconosce questo come un template.
#     Quando un client richiede un URI come `document://archive/007`, il framework
#     estrae il valore `007` e lo passa come argomento alla funzione `document_archive`.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Corrispondenza Parametri**: Il nome del segnaposto nell'URI (`{document_id}`)
#     deve corrispondere esattamente al nome del parametro nella firma della funzione
#     Python (`document_id: str`). FastMCP si occupa di collegarli e di convertire
#     il tipo (se specificato).
#
@app.resource("document://archive/{document_id}", title="Secret Archive")
def document_archive(document_id: str) -> str:
    """
    Restituisce il contenuto di un documento segreto in base all'ID fornito.
    Questo è un esempio di risorsa dinamica.
    """
    logger.info(f"Accessing resource template 'document_archive' with ID: {document_id}")
    
    # La logica della funzione utilizza il parametro estratto dall'URI per
    # cercare i dati e restituire un contenuto specifico.
    return SECRET_ARCHIVE.get(
        document_id,
        f"The document with ID '{document_id}' is sealed or non-existent."
    )
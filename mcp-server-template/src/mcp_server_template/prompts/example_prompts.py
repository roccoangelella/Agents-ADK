"""
Modulo didattico per dimostrare l'uso dei Prompt in MCP.

Questo file contiene esempi che illustrano come creare e utilizzare i Prompt,
uno dei tre primitivi fondamentali del Model Context Protocol. I Prompt sono
modelli di interazione riutilizzabili, tipicamente controllati dall'utente
tramite l'interfaccia del client (es. comandi slash, menu).

Gli esempi coprono:
1.  Un prompt di base con parametri.
2.  Un prompt avanzato che utilizza il "few-shot prompting".
3.  Un prompt semplice senza parametri.
"""
import logging
from mcp.server.fastmcp.prompts.base import AssistantMessage, Message, UserMessage
from ..app import app

logger = logging.getLogger(__name__)

# --- ESEMPIO DIDATTICO: Prompt di Base con Parametri ---
#
# [SCOPO DIDATTICO]:
#   Illustrare come creare un prompt personalizzabile che accetta input
#   dall'utente per guidare la generazione dell'LLM.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Prompt con Argomenti**: Il protocollo MCP definisce che i prompt possono
#     avere degli argomenti. FastMCP astrae questo concetto analizzando la firma
#     della funzione Python. I parametri `character` e `food` diventano
#     automaticamente gli argomenti che il client MCP (es. Claude Desktop)
#     mostrerà all'utente in un form.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Ingegneria del Prompt (Prompt Engineering)**: La funzione non esegue logica
#     complessa, ma costruisce dinamicamente una stringa di istruzioni (il prompt)
#     per l'LLM. Questo è un pattern centrale nell'IA generativa: usare il linguaggio
#     naturale per programmare il comportamento del modello.
#
@app.prompt(title="Vampire Story")
def vampire_story_prompt(character: str, food: str) -> Message:
    """
    Genera un'istruzione per l'LLM affinché racconti una storia ambigua
    su un vampiro, utilizzando i parametri forniti per personalizzarla.
    """
    logger.info(f"Creating prompt for story about '{character}' and '{food}'")
    
    # MCP Concept: Il valore di ritorno è una `UserMessage`. Questo imposta il
    # contesto iniziale della conversazione come se l'utente avesse scritto
    # questo testo.
    return UserMessage(
        f"You are an enigmatic storyteller. Write a short, very ambiguous and suggestive story in Italian, "
        f"starring a vampire named '{character}' and his relationship with '{food}'. "
        f"Use a melancholic and decadent tone."
    )

# --- ESEMPIO DIDATTICO: Prompt Semplice (Senza Parametri) ---
#
# [SCOPO DIDATTICO]:
#   Mostrare il caso d'uso più semplice di un prompt: un'azione fissa che
#   non richiede input dall'utente.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Prompt senza Argomenti**: Se la funzione Python non ha parametri, FastMCP
#     crea un prompt che il client può eseguire con un solo click, senza
#     richiedere all'utente di compilare alcun campo.
#
@app.prompt(title="Summarize Conversation")
def summarize_conversation_prompt() -> Message:
    """
    Genera un'istruzione per l'LLM affinché riassuma la conversazione corrente.
    """
    logger.info("Creating prompt for conversation summary.")
    return UserMessage("Please, concisely summarize all the key points of our conversation so far.")

# --- ESEMPIO DIDATTICO: Prompt Avanzato (Few-Shot Prompting) ---
#
# [SCOPO DIDATTICO]:
#   Dimostrare una tecnica avanzata di prompt engineering, il "few-shot prompting",
#   per guidare il comportamento dell'LLM in modo molto più preciso.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Prompt a Messaggi Multipli**: Un prompt non è limitato a una singola
#     istruzione. Può restituire una lista di messaggi (`list[Message]`) che
#     simulano un breve scambio di conversazione.
#   - **Ruoli Diversi (`UserMessage`, `AssistantMessage`)**: Includendo messaggi
#     con ruoli diversi, si fornisce all'LLM un esempio concreto (`shot`) di
#     come dovrebbe rispondere. Questo è molto più efficace che descrivere
#     il comportamento a parole.
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Few-Shot Prompting**: Questo è un pattern fondamentale. Fornendo uno o più
#     esempi di interazione (i "shots"), si "insegna" all'LLM il formato, il tono
#     e lo stile di risposta desiderati, migliorando drasticamente l'affidabilità
#     e la coerenza del modello.
#
@app.prompt(title="Impersonate Character")
def roleplay_character_prompt(character: str, context: str) -> list[Message]:
    """
    Fornisce un esempio "few-shot" per istruire l'LLM a impersonare un
    personaggio specifico, dimostrando un prompt multi-messaggio.
    """
    logger.info(f"Creating few-shot prompt for character '{character}'")
    
    # MCP Concept: La lista di messaggi viene inserita nel contesto della conversazione
    # in sequenza. L'ultimo messaggio è tipicamente quello a cui l'LLM deve rispondere.
    return [
        UserMessage(f"You are now {character}. How would you answer this question: {context}?"),
        AssistantMessage(f"Ah, an interesting question! In the shoes of {character}, my perspective is...")
    ]
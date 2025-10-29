"""
Modulo didattico per esporre in modo sicuro il file system locale come risorsa.

Questo file contiene un esempio di risorsa template che interagisce con il
file system del server. Dimostra un caso d'uso molto comune per i server MCP
locali e, soprattutto, introduce concetti di sicurezza fondamentali per
prevenire vulnerabilità.
"""
import base64
import json
import logging
from pathlib import Path

from ..app import app
from ..utils.error_handler import handle_tool_errors

logger = logging.getLogger(__name__)

# --- ESEMPIO DIDATTICO: Risorsa Template per il File System con Sandboxing ---
#
# [SCOPO DIDATTICO]:
#   Illustrare come un server MCP possa esporre dinamicamente il contenuto del
#   file system in modo sicuro, prevenendo accessi non autorizzati.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Risorsa Template Dinamica**: L'URI `filesystem://list/{encoded_path}`
#     è un template. Il client può richiedere il contenuto di qualsiasi directory
#     sostituendo `{encoded_path}` con un valore specifico.
#   - **Interazione con l'Ambiente**: Le risorse, come i tool, possono interagire
#     con l'ambiente del server (in questo caso, il file system).
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Sandboxing di Sicurezza**: Questo è il pattern più importante dimostrato qui.
#     Per prevenire attacchi di "Path Traversal" (es. un client che richiede
#     `../../.ssh/id_rsa`), il codice confina l'accesso a una singola directory
#     radice sicura (`SAFE_ROOT_DIR`). Qualsiasi tentativo di accedere a un percorso
#     al di fuori di questa "sandbox" viene bloccato.
#   - **Codifica Base64 per i Parametri**: Il percorso nell'URI viene codificato in
#     Base64 (url-safe). Questo è un trucco utile per passare in modo sicuro
#     stringhe che potrebbero contenere caratteri problematici per un URI, come `/` o `\`.
#
@app.resource("filesystem://list/{encoded_path}", title="List Directory Contents")
@handle_tool_errors
async def list_directory_contents(encoded_path: str) -> str:
    """
    Elenca il contenuto di una directory specificata all'interno di un'area sicura.
    Il percorso della directory deve essere codificato in Base64 (url-safe).
    Restituisce una lista di file e cartelle in formato JSON.
    """
    # PATTERN: Definizione di una "Sandbox".
    # Definiamo una directory radice sicura. Qualsiasi accesso al di fuori di questa
    # directory sarà negato. In questo esempio, usiamo la directory 'Documenti'
    # dell'utente, un'area generalmente sicura.
    SAFE_ROOT_DIR = Path.home() / "Documents"
    
    logger.info(f"Accessing resource template 'list_directory_contents' with encoded path: {encoded_path}")

    try:
        # Decodifica il percorso da Base64. Usiamo la variante url-safe.
        decoded_path_str = base64.urlsafe_b64decode(encoded_path).decode('utf-8')
        
        # Costruisce il percorso completo e lo risolve per normalizzarlo (es. rimuove i '..')
        requested_path = (SAFE_ROOT_DIR / decoded_path_str).resolve()
        
        # PATTERN: Validazione di Sicurezza (Path Traversal).
        # Questo è il controllo di sicurezza cruciale. Verifichiamo che il percorso
        # normalizzato e assoluto sia ancora un figlio della nostra directory sicura.
        # Se un utente prova a usare '..' per risalire l'albero delle directory,
        # `resolve()` calcolerà il percorso finale e questo controllo fallirà.
        if SAFE_ROOT_DIR not in requested_path.parents and requested_path != SAFE_ROOT_DIR:
            raise SecurityException(f"Access denied: Path '{decoded_path_str}' is outside the allowed directory.")

        if not requested_path.is_dir():
            raise FileNotFoundError(f"The specified path is not a valid directory: {decoded_path_str}")

        # Elenca il contenuto della directory
        contents = {
            "directories": [d.name for d in requested_path.iterdir() if d.is_dir()],
            "files": [f.name for f in requested_path.iterdir() if f.is_file()],
        }
        
        logger.info(f"Successfully listed contents for: {requested_path}")
        
        # Restituisce il risultato come stringa JSON.
        return json.dumps(contents, indent=2)

    except (FileNotFoundError, SecurityException) as e:
        logger.error(f"Error accessing directory '{encoded_path}': {e}")
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception(f"An unexpected error occurred for encoded path: {encoded_path}")
        return json.dumps({"error": "An unexpected error occurred while listing the directory."})

class SecurityException(Exception):
    """Eccezione personalizzata per errori di sicurezza specifici del sandboxing."""
    pass
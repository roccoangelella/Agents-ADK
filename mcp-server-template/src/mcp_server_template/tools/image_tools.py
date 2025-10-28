"""
Modulo didattico per la gestione e manipolazione di immagini.

Questo file dimostra come un server MCP possa interagire con il file system
per leggere un file, elaborarlo e scrivere un nuovo file come risultato.
"""
import logging
from pathlib import Path

from PIL import Image as PILImage

from ..app import app
from ..utils.error_handler import handle_tool_errors

logger = logging.getLogger(__name__)

# --- ESEMPIO DIDATTICO: Interazione con il File System (Lettura e Scrittura) ---
#
# [SCOPO DIDATTICO]:
#   Mostrare un ciclo completo di elaborazione di un file che include la scrittura
#   di un nuovo file sul disco del server.
#
# [CONCETTO MCP ILLUSTRATO]:
#   - **Tool con Effetti Collaterali (Side Effects)**: A differenza delle Risorse (che
#     dovrebbero essere read-only), i Tool sono il meccanismo corretto per eseguire
#     azioni che modificano lo stato del server o del suo ambiente, come scrivere un file.
#   - **Restituzione di un Riferimento**: Invece di restituire i dati binari dell'immagine,
#     il tool restituisce il percorso del nuovo file. L'LLM può quindi usare questo
#     percorso in chiamate successive ad altri tool (es. un tool per condividere file).
#
# [PATTERN DI PROGETTAZIONE]:
#   - **Costruzione Sicura dei Percorsi**: Utilizziamo la libreria `pathlib` per manipolare
#     i percorsi in modo sicuro e indipendente dal sistema operativo. Il metodo `.with_suffix()`
#     è un modo robusto per cambiare l'estensione di un file.
#   - **Avvertenza sulla Sicurezza**: Il codice include un commento esplicito sulla
#     necessità di sandboxing in un'applicazione reale per prevenire attacchi di
#     Path Traversal, dove un input malevolo potrebbe portare alla scrittura di file
#     in percorsi di sistema sensibili.
#
@app.tool(title="Convert Image to WebP and Save")
@handle_tool_errors
async def convert_image_to_webp(image_path: str) -> str:
    """
    Converte un'immagine dal percorso specificato in formato WebP e la salva
    nella stessa directory con la nuova estensione. Restituisce il percorso
    del nuovo file creato.
    """
    logger.info(f"Executing 'convert_image_to_webp' for path: '{image_path}'")

    # PATTERN: Validazione e Sicurezza dell'Input.
    # Verifichiamo che il percorso esista e sia un file.
    p_input = Path(image_path).resolve()
    if not p_input.is_file():
        raise FileNotFoundError(f"The specified image path does not exist or is not a file: {image_path}")

    # Costruisce il percorso di output nella stessa directory, cambiando l'estensione.
    # es. /percorso/immagine.jpg -> /percorso/immagine.webp
    p_output = p_input.with_suffix('.webp')

    # AVVERTENZA SULLA SICUREZZA (per LLM Sviluppatore):
    # In un'applicazione di produzione, la scrittura su disco basata su input
    # esterni è un'operazione ad alto rischio. Sarebbe necessario implementare
    # un meccanismo di "sandboxing" per garantire che la scrittura avvenga
    # solo all'interno di una directory pre-approvata e sicura, per prevenire
    # attacchi di Path Traversal (es. `image_path = "../../../etc/passwd"`).

    # Apri, converti e salva l'immagine
    with PILImage.open(p_input) as img:
        # Il salvataggio ora avviene su un percorso disco fisico.
        img.save(p_output, format='WEBP')

    logger.info(f"Successfully converted '{p_input}' and saved to '{p_output}'")

    # Restituisce una stringa di conferma con il percorso del nuovo file.
    return f"Image successfully converted and saved to: {p_output}"
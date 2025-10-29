# src/mcp_server_template/state.py
import logging
from datetime import datetime, timezone
from typing import Dict

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class SessionState(BaseModel):
    """
    A Pydantic model to hold the state for a single client session.
    """
    session_key: int  # Usiamo la chiave numerica (id dell'oggetto sessione)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    call_count: int = 0

class StateManager:
    """
    Manages the state of all active client sessions.
    """
    def __init__(self):
        # La chiave del dizionario ora è un intero
        self._sessions: Dict[int, SessionState] = {}
        logger.info("StateManager initialized.")

    def get_or_create_session(self, session_key: int) -> SessionState:
        """
        Retrieves the state for a given session key, creating it if it doesn't exist.
        """
        if session_key not in self._sessions:
            logger.info(f"Creating new session state for session_key: {session_key}")
            self._sessions[session_key] = SessionState(session_key=session_key)
        return self._sessions[session_key]

    def increment_call_count(self, session_key: int) -> None:
        """
        Increments the tool call counter for a specific session.
        """
        session = self.get_or_create_session(session_key)
        session.call_count += 1
        logger.debug(f"Incremented call count for session {session_key} to {session.call_count}")

# Create a singleton instance of the StateManager.
state_manager = StateManager()
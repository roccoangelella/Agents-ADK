# src/mcp_server_template/schemas.py
from datetime import datetime
from pydantic import BaseModel, Field

class ServerStatusResponse(BaseModel):
    """
    Structured response model for the server_status tool.
    """
    server_name: str
    instructions: str | None
    tools_available: int
    resources_available: int
    resource_templates: int
    prompts_available: int

class SumResponse(BaseModel):
    """
    Structured output for the 'sum' tool.
    """
    a: float
    b: float
    sum: float

class CharCountResponse(BaseModel):
    """
    Structured output for the 'count_characters' tool.
    """
    word: str
    length: int

class CurrentTimeResponse(BaseModel):
    """
    Structured output for the 'current_time' tool.
    """
    iso_utc: str
    iso_local: str
    epoch: int

# --- NUOVI SCHEMI PER I TOOL AGGIUNTI ---

class SessionInfoResponse(BaseModel):
    """
    Structured output for the 'session_info' tool.
    Describes the state of the current client session.
    """
    session_id: str
    created_at: datetime
    call_count: int
    session_duration_seconds: float

class ConfirmationSchema(BaseModel):
    """
    Schema for the elicitation request in the 'confirm_action' tool.
    """
    confirm: bool = Field(description="Confirm the action by typing 'true' or 'false'.")

class TaskStatusResponse(BaseModel):
    """
    Structured output for the 'long_running_task' tool.
    """
    status: str
    duration_seconds: float
    steps_completed: int
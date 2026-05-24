from typing import Any

from pydantic import BaseModel, Field


class IntentData(BaseModel):
    intent: str = Field(default="unknown", examples=["complaint"])
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, examples=[0.87])
    entities: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    user_id: str | int = Field(examples=["user_001"])
    message: str = Field(min_length=1, examples=["Nu imi merge aplicatia"])
    intent_data: IntentData | None = None


class ChatResponse(BaseModel):
    user_id: str
    message: str
    response: str
    intent: str
    confidence: float
    entities: dict[str, Any]
    was_filtered: bool
    llm_provider: str
    llm_error: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    model: str
    has_groq_key: bool
    mock_mode: bool


class ResetResponse(BaseModel):
    user_id: str
    cleared: bool

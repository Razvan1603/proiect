from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import ChatRequest, ChatResponse, HealthResponse, IntentData, IntentRequest, ResetResponse
from app.services.chat_orchestrator import process_chat
from app.services.dialogue_service import LLMServiceError, clear_history, get_history, interaction_log
from app.services.intent_classifier import IntentServiceError
from app.services.intent_service import detect_intent

app = FastAPI(
    title="Social Media Support Chatbot API",
    description="Backend FastAPI pentru Sarcina 3: API, orchestrare si demo Streamlit.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["status"])
def root() -> dict[str, str]:
    return {
        "message": "Social Media Support Chatbot API",
        "docs": "/docs",
        "chat_endpoint": "/chat",
    }


@app.get("/health", response_model=HealthResponse, tags=["status"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="chatbot-api",
        model=settings.groq_model,
        has_groq_key=bool(settings.groq_api_key),
        mock_mode=False,
    )


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return process_chat(request)
    except IntentServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/intent", response_model=IntentData, tags=["intent"])
def intent(request: IntentRequest) -> IntentData:
    try:
        return detect_intent(request.message)
    except IntentServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/reset/{user_id}", response_model=ResetResponse, tags=["chat"])
def reset_conversation(user_id: str) -> ResetResponse:
    clear_history(user_id)
    return ResetResponse(user_id=user_id, cleared=True)


@app.get("/history/{user_id}", tags=["debug"])
def history(user_id: str) -> dict[str, object]:
    messages = get_history(user_id)
    return {"user_id": user_id, "messages": messages, "count": len(messages)}


@app.get("/logs", tags=["debug"])
def logs() -> dict[str, object]:
    return {"count": len(interaction_log), "items": interaction_log}

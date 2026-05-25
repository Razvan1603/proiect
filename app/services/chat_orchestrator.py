from app.schemas import ChatRequest, ChatResponse, IntentData
from app.services.dialogue_service import generate_response
from app.services.intent_service import detect_intent


def process_chat(request: ChatRequest) -> ChatResponse:
    user_id = str(request.user_id)
    intent_data: IntentData = request.intent_data or detect_intent(request.message)
    result = generate_response(
        user_id=user_id,
        user_message=request.message,
        intent_data=intent_data,
    )

    return ChatResponse(
        user_id=user_id,
        message=request.message,
        response=result["response"],
        intent=result["intent"],
        confidence=result["confidence"],
        entities=result["entities"],
        intent_scores=result["intent_scores"],
        was_filtered=result["was_filtered"],
        llm_provider=result["llm_provider"],
        llm_error=result["llm_error"],
    )

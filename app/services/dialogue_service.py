from datetime import datetime
from typing import Any

from app.config import settings
from app.schemas import IntentData

try:
    from groq import Groq
except ImportError:
    Groq = None


CONFIDENCE_THRESHOLD = 0.5
FALLBACK_RESPONSE = (
    "Imi pare rau, nu am putut procesa cererea ta. "
    "Te rog contacteaza suportul nostru direct."
)

INTENT_HINTS = {
    "complaint": "Utilizatorul are o problema sau reclamatie. Fii empatic si ofera o solutie concreta.",
    "question": "Utilizatorul pune o intrebare. Raspunde direct, clar si util.",
    "greeting": "Utilizatorul saluta. Raspunde prietenos si intreaba cu ce il poti ajuta.",
    "feedback_positive": "Utilizatorul este multumit. Multumeste-i si inchide conversatia pozitiv.",
    "small_talk": "Utilizatorul face conversatie casual. Raspunde natural si scurt, apoi readu discutia spre suport.",
    "presentation": "Utilizatorul se prezinta. Saluta-l pe nume daca apare si intreaba cu ce il poti ajuta.",
    "help": "Utilizatorul cere ajutor. Cere detalii concrete si ofera primul pas util.",
    "farewell": "Utilizatorul isi ia ramas bun. Raspunde scurt si politicos.",
    "unknown": "Mesajul nu este clar. Cere politicos clarificari.",
}

conversation_histories: dict[str, list[dict[str, str]]] = {}
interaction_log: list[dict[str, Any]] = []


class LLMServiceError(RuntimeError):
    """Raised when the configured LLM cannot generate a response."""


def get_history(user_id: str) -> list[dict[str, str]]:
    return conversation_histories.get(user_id, [])


def update_history(user_id: str, role: str, content: str) -> None:
    conversation_histories.setdefault(user_id, [])
    conversation_histories[user_id].append({"role": role, "content": content})
    conversation_histories[user_id] = conversation_histories[user_id][-settings.max_history :]


def clear_history(user_id: str) -> None:
    conversation_histories[user_id] = []


def build_system_prompt(intent_data: IntentData) -> str:
    base = (
        "Te numesti Bob si esti un asistent de suport pentru o platforma de social media. "
        "Raspunzi intotdeauna in limba romana, scurt, clar si prietenos. "
        "Nu inventa informatii; daca nu stii raspunsul, spune ca vei escalada problema."
    )

    if intent_data.confidence >= CONFIDENCE_THRESHOLD and intent_data.intent in INTENT_HINTS:
        base += f"\n\nContextul mesajului: {INTENT_HINTS[intent_data.intent]}"

    if intent_data.entities:
        entities_text = ", ".join(f"{key}: {value}" for key, value in intent_data.entities.items())
        base += f"\n\nInformatii detectate din mesaj: {entities_text}."

    return base


def _call_groq(system_prompt: str, messages: list[dict[str, str]]) -> str:
    if settings.use_mock_llm:
        raise LLMServiceError("USE_MOCK_LLM este activat. Seteaza USE_MOCK_LLM=false pentru Groq.")
    if not settings.groq_api_key:
        raise LLMServiceError("Lipseste GROQ_API_KEY in fisierul .env.")
    if Groq is None:
        raise LLMServiceError("Pachetul groq nu este instalat.")

    client = Groq(api_key=settings.groq_api_key)
    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "system", "content": system_prompt}, *messages],
            temperature=0.7,
            max_tokens=700,
        )
        return response.choices[0].message.content
    except Exception as exc:
        raise LLMServiceError(f"Groq nu a putut genera raspunsul: {exc}") from exc


def post_process(response: str) -> dict[str, Any]:
    if not response or not response.strip():
        return {"text": FALLBACK_RESPONSE, "was_filtered": True}

    response = response.strip()
    was_filtered = False
    if len(response) > settings.max_response_length:
        response = response[: settings.max_response_length].rsplit(" ", 1)[0] + "..."
        was_filtered = True

    return {"text": response, "was_filtered": was_filtered}


def log_interaction(
    user_id: str,
    user_message: str,
    intent_data: IntentData,
    response: str,
    was_filtered: bool,
    llm_provider: str,
) -> None:
    interaction_log.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user_id": user_id,
            "user_message": user_message,
            "intent": intent_data.intent,
            "confidence": intent_data.confidence,
            "response": response,
            "was_filtered": was_filtered,
            "llm_provider": llm_provider,
        }
    )


def generate_response(user_id: str, user_message: str, intent_data: IntentData) -> dict[str, Any]:
    system_prompt = build_system_prompt(intent_data)
    update_history(user_id, "user", user_message)

    raw_response = _call_groq(system_prompt, get_history(user_id))
    result = post_process(raw_response)
    update_history(user_id, "assistant", result["text"])

    if intent_data.intent == "farewell":
        clear_history(user_id)

    log_interaction(
        user_id=user_id,
        user_message=user_message,
        intent_data=intent_data,
        response=result["text"],
        was_filtered=result["was_filtered"],
        llm_provider="groq",
    )

    return {
        "response": result["text"],
        "intent": intent_data.intent,
        "confidence": intent_data.confidence,
        "entities": intent_data.entities,
        "intent_scores": intent_data.intent_scores,
        "was_filtered": result["was_filtered"],
        "llm_provider": "groq",
        "llm_error": None,
    }

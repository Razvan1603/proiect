from app.schemas import IntentData


def detect_intent_mock(text: str) -> IntentData:
    """Temporary Sarcina 1 adapter. Replace this with the real model call."""
    text_lower = text.lower()

    if any(word in text_lower for word in ["problema", "problemă", "nu merge", "eroare", "blocat", "403"]):
        return IntentData(
            intent="complaint",
            confidence=0.88,
            entities={"issue": "eroare aplicatie"},
        )

    if any(word in text_lower for word in ["buna", "bună", "salut", "hello", "hey"]):
        return IntentData(intent="greeting", confidence=0.95, entities={})

    if any(word in text_lower for word in ["cum", "ce", "unde", "cand", "când", "?"]):
        return IntentData(intent="question", confidence=0.82, entities={})

    if any(word in text_lower for word in ["multumesc", "mulțumesc", "mersi", "super", "perfect"]):
        return IntentData(intent="feedback_positive", confidence=0.91, entities={})

    if any(word in text_lower for word in ["pa", "la revedere", "bye"]):
        return IntentData(intent="farewell", confidence=0.93, entities={})

    return IntentData(intent="unknown", confidence=0.40, entities={})

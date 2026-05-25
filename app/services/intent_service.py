from app.schemas import IntentData
from app.services.intent_classifier import predict_intent


def detect_intent(text: str) -> IntentData:
    """Real Sarcina 1 adapter: BERT model loaded from model_final/model.safetensors."""
    return predict_intent(text)

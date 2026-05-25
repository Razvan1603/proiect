from pathlib import Path
from typing import Any

from app.schemas import IntentData, IntentScore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "model_final"
MODEL_WEIGHTS = MODEL_DIR / "model.safetensors"

DATASET_LABEL_TO_INTENT = {
    "RECLAMATIE": "complaint",
    "MULTUMIRE": "feedback_positive",
    "SALUT": "greeting",
    "SMALL_TALK": "small_talk",
    "INTREBARE": "question",
    "PREZENTARE": "presentation",
    "HELP": "help",
}

TRANSFORMER_LABEL_TO_DATASET_LABEL = {
    "LABEL_0": "RECLAMATIE",
    "LABEL_1": "MULTUMIRE",
    "LABEL_2": "SALUT",
    "LABEL_3": "SMALL_TALK",
    "LABEL_4": "INTREBARE",
    "LABEL_5": "PREZENTARE",
    "LABEL_6": "HELP",
}


class IntentServiceError(RuntimeError):
    """Raised when the BERT intent classifier cannot be loaded."""


def _normalize_for_entities(text: str) -> str:
    return " ".join(text.lower().replace(",", " ").split())


def extract_entities(text: str) -> dict[str, Any]:
    normalized = _normalize_for_entities(text)
    entities: dict[str, Any] = {}

    platforms = {
        "instagram": ["instagram", "insta"],
        "facebook": ["facebook", "fb"],
        "tiktok": ["tiktok"],
        "whatsapp": ["whatsapp", "wapp"],
        "email": ["email", "mail"],
    }
    for platform, keywords in platforms.items():
        if any(keyword in normalized for keyword in keywords):
            entities["platform"] = platform
            break

    issue_patterns = {
        "login": ["login", "loga", "autentific", "parola", "403"],
        "cont blocat": ["cont blocat", "blocat", "banat", "suspendat"],
        "livrare": ["livrare", "colet", "comanda", "curier", "produs"],
        "plata": ["plata", "bani", "card", "factura", "refund"],
        "retur": ["retur", "returnez", "schimb", "garantie"],
        "eroare aplicatie": ["eroare", "bug", "nu merge", "crash", "aplicatia"],
    }
    detected_issues = [
        issue for issue, keywords in issue_patterns.items() if any(keyword in normalized for keyword in keywords)
    ]
    if detected_issues:
        entities["issue"] = detected_issues[0]
        if len(detected_issues) > 1:
            entities["related_issues"] = detected_issues[1:]

    return entities


class BertIntentClassifier:
    def __init__(self, model_dir: Path = MODEL_DIR):
        if not MODEL_WEIGHTS.exists():
            raise IntentServiceError(
                "Lipseste model_final/model.safetensors. Pune fisierul BERT in model_final."
            )

        try:
            from transformers import pipeline
            import safetensors  # noqa: F401
            import torch  # noqa: F401
        except ImportError as exc:
            raise IntentServiceError(
                "Lipsesc dependintele pentru model.safetensors. Ruleaza: pip install -r requirements.txt"
            ) from exc

        try:
            self.pipe = pipeline(
                "text-classification",
                model=str(model_dir),
                tokenizer=str(model_dir),
                top_k=None,
            )
        except Exception as exc:
            raise IntentServiceError(f"Modelul BERT din model_final nu a putut fi incarcat: {exc}") from exc

    def predict(self, text: str) -> IntentData:
        raw_scores = self.pipe(text)
        scores = raw_scores[0] if raw_scores and isinstance(raw_scores[0], list) else raw_scores
        best = max(scores, key=lambda item: item["score"])

        transformer_label = str(best["label"])
        dataset_label = TRANSFORMER_LABEL_TO_DATASET_LABEL.get(transformer_label, transformer_label)
        intent_scores = []
        for item in sorted(scores, key=lambda score_item: score_item["score"], reverse=True):
            item_label = str(item["label"])
            item_dataset_label = TRANSFORMER_LABEL_TO_DATASET_LABEL.get(item_label, item_label)
            intent_scores.append(
                IntentScore(
                    intent=DATASET_LABEL_TO_INTENT.get(item_dataset_label, "unknown"),
                    label=item_dataset_label,
                    confidence=round(float(item["score"]), 4),
                )
            )

        entities = extract_entities(text)
        entities["model_label"] = dataset_label
        entities["model_backend"] = "bert_safetensors"

        return IntentData(
            intent=DATASET_LABEL_TO_INTENT.get(dataset_label, "unknown"),
            confidence=round(float(best["score"]), 4),
            entities=entities,
            intent_scores=intent_scores,
        )


_classifier: BertIntentClassifier | None = None


def get_classifier() -> BertIntentClassifier:
    global _classifier
    if _classifier is None:
        _classifier = BertIntentClassifier()
    return _classifier


def predict_intent(text: str) -> IntentData:
    return get_classifier().predict(text)

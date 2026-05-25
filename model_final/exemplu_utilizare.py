from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.intent_service import detect_intent


def get_intent(text: str) -> dict:
    return detect_intent(text).model_dump()


if __name__ == "__main__":
    print(get_intent("De ce nu functioneaza aplicatia asta"))

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    use_mock_llm: bool = _env_flag("USE_MOCK_LLM", default=False)
    max_history: int = int(os.getenv("MAX_HISTORY", "10"))
    max_response_length: int = int(os.getenv("MAX_RESPONSE_LENGTH", "500"))


settings = Settings()

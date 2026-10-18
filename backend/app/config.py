from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-6-astra"
    guide_database_path: Path = BACKEND_ROOT / "data" / "windows_troubleshooting.db"
    allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_guides_in_context: int = 5
    serve_draft_guides: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allow_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Telegram
    telegram_bot_token: str
    telegram_owner_chat_id: int  # your personal chat id — bot only serves you

    # LLM (Anthropic Claude by default)
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-6"

    # HeadHunter
    hh_access_token: str | None = None  # only needed to actually submit responses
    hh_resume_id: str | None = None  # your resume id on hh.ru, needed to apply
    hh_area_id: int = 1  # 1 = Moscow

    # SuperJob (optional)
    superjob_api_key: str | None = None
    superjob_login_token: str | None = None

    # App behaviour
    search_interval_minutes: int = 30
    min_match_score_to_notify: int = 60
    database_url: str = "sqlite+aiosqlite:///./jobhunter.db"
    log_level: str = "INFO"


settings = Settings()  # type: ignore[call-arg]

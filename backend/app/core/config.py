from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocuEntitySeek API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"
    
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "docuentityseek"
    db_user: str = "docuentityseek_app"
    db_password: str = ""

    sql_echo: bool = False

    development_user_email: str = "demo@docuentityseek.local"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
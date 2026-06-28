from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET = "change-me-in-production-use-a-long-random-secret"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "AI Anfragen-Assistent"
    environment: str = "development"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "ai_agent_platform"

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_base_url: str | None = None
    openai_organization: str | None = None
    openai_timeout: float = 60.0
    agent_max_iterations: int = 8

    jwt_secret_key: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: str = "http://localhost:3000"
    notification_provider: str = "logging"
    resend_api_key: str = ""
    notification_from_email: str = ""
    frontend_base_url: str | None = None
    public_api_base_url: str = "http://localhost:8000"
    widget_stale_after_hours: int = 168
    landing_demo_max_user_messages: int = 6
    vapi_webhook_secret: str = ""
    self_serve_registration_enabled: bool = False

    @computed_field
    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def validate_production_settings(settings: Settings) -> None:
    if settings.is_development:
        return

    errors: list[str] = []
    if settings.jwt_secret_key == DEFAULT_JWT_SECRET or len(settings.jwt_secret_key) < 32:
        errors.append("JWT_SECRET_KEY must be a unique secret with at least 32 characters")
    if not settings.openai_api_key:
        errors.append("OPENAI_API_KEY is required when APP_ENV is not development")
    if settings.notification_provider.lower() != "resend":
        errors.append("NOTIFICATION_PROVIDER must be 'resend' in production")
    if not settings.resend_api_key.strip():
        errors.append("RESEND_API_KEY is required in production")
    if not settings.notification_from_email.strip():
        errors.append("NOTIFICATION_FROM_EMAIL is required in production")
    if not (settings.frontend_base_url or "").strip():
        errors.append("FRONTEND_BASE_URL is required in production")

    if errors:
        message = "Production configuration is invalid:\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        raise RuntimeError(message)


@lru_cache
def get_settings() -> Settings:
    return Settings()

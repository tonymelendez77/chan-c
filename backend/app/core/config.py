from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/chanc"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/chanc"
    SECRET_KEY: str = "change-me"
    ENVIRONMENT: str = "development"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WEBHOOK_SECRET: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    # Cece's personal WhatsApp for bot-to-admin notifications
    CECE_WHATSAPP_NUMBER: str = ""
    VAPI_API_KEY: str = ""
    VAPI_PHONE_NUMBER_ID: str = ""
    ANTHROPIC_API_KEY: str = ""
    CONFIDENCE_THRESHOLD: float = 0.7
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://chan-c.vercel.app",
        "https://chan-c.gt",
    ]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

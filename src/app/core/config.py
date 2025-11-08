import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "TallyAI"
    DEBUG: bool = True
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tallyai.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecret")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TALLY_HOST: str = os.getenv("TALLY_HOST", "65.0.33.244")
    TALLY_PORT: int = int(os.getenv("TALLY_PORT", "9000"))

settings = Settings()

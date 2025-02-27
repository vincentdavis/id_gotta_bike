"""Main bot file."""

from pydantic_settings import BaseSettings


# Load environment variables from .env file
class Settings(BaseSettings):
    """Application settings that can be loaded from environment variables."""

    ENVIRONMENT: str = "LOCAL"
    LOGFIRE_ENVIRONMENT: str = "LOCAL"
    DEBUG: bool = False
    LOGFIRE_TOKEN: str | None = None  # Needs to be set on remote servers
    API_URL: str = "http://127.0.0.1:8000/api_v1/discord"
    API_KEY: str = ""
    DISCORD_BOT_TOKEN: str

    class Config:  # noqa: D106
        env_file = ".env"

    @classmethod
    def set_environment(cls, overwrite=False):  # noqa: D102
        import os

        for key, value in cls().model_dump().items():
            if value is not None:
                if overwrite:
                    os.environ[key] = str(value)
                elif not overwrite and key in os.environ:
                    continue
                else:
                    os.environ.setdefault(key, str(value))


settings = Settings()
settings.set_environment()

import logfire  # noqa: E402

logfire.configure()

from src.bot.client import init_bot  # noqa: E402

init_bot()

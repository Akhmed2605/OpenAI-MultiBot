"""Zentraler Ladevorgang der Konfiguration aus Umgebungsvariablen."""

from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_token: str | None
    discord_token: str | None
    openai_api_key: str
    openai_model: str

    @classmethod
    def load(cls) -> "Settings":
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        discord_token = os.getenv("DISCORD_BOT_TOKEN")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if not openai_api_key:
            raise RuntimeError("OPENAI_API_KEY wird benötigt. Bitte in der .env-Datei hinterlegen.")

        if not (telegram_token or discord_token):
            raise RuntimeError(
                "Mindestens ein Plattform-Token (TELEGRAM_BOT_TOKEN oder DISCORD_BOT_TOKEN) "
                "muss gesetzt sein."
            )

        return cls(
            telegram_token=telegram_token,
            discord_token=discord_token,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
        )


settings = Settings.load()

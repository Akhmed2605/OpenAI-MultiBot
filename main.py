"""Einstiegspunkt zum Starten des Telegram- oder Discord-Bots."""

from __future__ import annotations
import argparse
import sys
from bots import config, discord_bot, telegram_bot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chatbot auf Basis von OpenAI.")
    parser.add_argument(
        "--platform",
        choices=["telegram", "discord"],
        required=True,
        help="Welcher Client gestartet werden soll.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = config.settings

    if args.platform == "telegram":
        if not settings.telegram_token:
            sys.exit("TELEGRAM_BOT_TOKEN ist nicht gesetzt.")
        telegram_bot.run(settings.telegram_token)

    elif args.platform == "discord":
        if not settings.discord_token:
            sys.exit("DISCORD_BOT_TOKEN ist nicht gesetzt.")
        discord_bot.run(settings.discord_token)

    else:  # pragma: no cover - argparse validation keeps us safe
        sys.exit(f"Unbekannte Plattform {args.platform}")


if __name__ == "__main__":
    main()

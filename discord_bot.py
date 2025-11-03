"""Discord-Bot mit freien Antworten sowie den Befehlen !ask/!reset."""

from __future__ import annotations
from typing import Optional
import discord
from discord.ext import commands
from .openai_client import ask_openai, reset_conversation

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    description="Discord Fragen-Bot"
)


async def _send_answer(
    channel: discord.abc.MessageableChannel,
    question: str,
    author: discord.abc.User | discord.Member
) -> None:
    async with channel.typing():
        try:
            answer = await ask_openai(
                question,
                conversation_id=channel.id,
                user_label=getattr(author, "display_name", author.name),
            )
        except Exception as exc:  # pragma: no cover - defensive logging surface
            await channel.send(f"OpenAI-Fehler: {exc}")
            return

    await channel.send(answer)


@bot.command(name="ask")
async def ask_command(ctx: commands.Context, *, question: Optional[str] = None) -> None:
    if not question:
        await ctx.send("Verwendung: !ask <deine Frage>")
        return
    await _send_answer(ctx.channel, question, ctx.author)


@bot.command(name="reset", help="Setzt den Gesprächsverlauf für diesen Kanal zurück")
async def reset_command(ctx: commands.Context) -> None:
    reset_conversation(ctx.channel.id)
    await ctx.send("Der Gesprächsverlauf für diesen Kanal wurde gelöscht.")


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    content = (message.content or "").strip()

    if content and not content.startswith(bot.command_prefix):
        await _send_answer(message.channel, content, message.author)

    await bot.process_commands(message)


def run(token: str) -> None:
    bot.run(token)

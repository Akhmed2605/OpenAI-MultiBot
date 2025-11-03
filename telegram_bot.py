"""Telegram-Bot mit Gesprächsverlauf."""

from __future__ import annotations
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from .openai_client import ask_openai, reset_conversation


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hallo! Schreibe einfach deine Frage in den Chat, dann frage ich das OpenAI-Modell. "
        "Verwende /reset, um eine neue Unterhaltung ohne Kontext zu beginnen."
    )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_conversation(update.effective_chat.id)
    await update.message.reply_text("Der Verlauf wurde gelöscht. Lass uns neu beginnen!")


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = " ".join(context.args).strip()
    if not question:
        await update.message.reply_text("Verwendung: /ask <deine Frage>")
        return
    await _handle_question(update, question)


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = (update.message.text or "").strip()
    if not message_text:
        return
    await _handle_question(update, message_text)


async def _handle_question(update: Update, question: str) -> None:
    thinking_msg = await update.message.reply_text("Ich denke nach ...", quote=True)
    user_label = update.effective_user.full_name or update.effective_user.username
    chat_id = update.effective_chat.id
    try:
        answer = await ask_openai(
            question,
            conversation_id=chat_id,
            user_label=user_label,
        )
    except Exception as exc:  # pragma: no cover - defensive logging surface
        await thinking_msg.edit_text(f"Fehler bei der Anfrage an OpenAI: {exc}")
        return
    await thinking_msg.edit_text(answer)


def run(token: str) -> None:
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    application.run_polling()

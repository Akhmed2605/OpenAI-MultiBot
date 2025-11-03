"""Schlanke Hülle rund um die OpenAI-API mit asynchronen Hilfsfunktionen."""

from __future__ import annotations
import asyncio
import os
from collections import defaultdict, deque
from functools import partial
from typing import Deque, Dict, List
from openai import OpenAI
from .config import settings

SYSTEM_PROMPT = os.getenv(
    "ASK_SYSTEM_PROMPT",
    "Du bist ein hilfsbereiter und prägnanter Assistent, der mit Nutzerinnen und Nutzern spricht. "
    "Behalte den Kontext der Unterhaltung im Blick.",
)

MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "5"))

_client = OpenAI(api_key=settings.openai_api_key)
_conversations: Dict[str, Deque[dict[str, str]]] = defaultdict(deque)


def _conversation_key(conversation_id: int | str | None) -> str | None:
    if conversation_id is None:
        return None
    return str(conversation_id)


def reset_conversation(conversation_id: int | str) -> None:
    key = _conversation_key(conversation_id)
    if key is not None:
        _conversations.pop(key, None)


def _build_messages(conversation_key: str | None, prompt: str, user_label: str | None) -> List[dict[str, str]]:
    messages: List[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_key is not None:
        messages.extend(_conversations.get(conversation_key, ()))
    user_content = prompt if not user_label else f"{user_label}: {prompt}"
    messages.append({"role": "user", "content": user_content})
    return messages


def _store_turn(conversation_key: str, user_text: str, assistant_text: str) -> None:
    history = _conversations[conversation_key]
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": assistant_text})
    max_messages = MAX_HISTORY_TURNS * 2
    while len(history) > max_messages:
        history.popleft()


def _sync_completion(messages: List[dict[str, str]]) -> str:
    response = _client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.2,
    )
    message = response.choices[0].message.content or "Ich habe im Moment keine Antwort."
    return message.strip()


async def ask_openai(
    prompt: str,
    *,
    conversation_id: int | str | None = None,
    user_label: str | None = None,
) -> str:
    key = _conversation_key(conversation_id)
    messages = _build_messages(key, prompt, user_label)
    loop = asyncio.get_running_loop()
    answer = await loop.run_in_executor(None, partial(_sync_completion, messages))
    if key is not None:
        stored_user_text = prompt if user_label is None else f"{user_label}: {prompt}"
        _store_turn(key, stored_user_text, answer)
    return answer

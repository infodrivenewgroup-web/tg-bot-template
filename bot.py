"""Шаблон Telegram-бота (aiogram 3).

Переменные окружения:
  BOT_TOKEN       — токен от @BotFather (обязательно)
  SYSTEM_PROMPT   — характер бота; если задан и есть ключ ИИ, бот отвечает с помощью ИИ
  ALLOWED_CHAT_IDS — (необязательно) список chat ID через запятую, кому бот отвечает
  GEMINI_API_KEY / OPENROUTER_API_KEY / OLLAMA_URL — ИИ: Gemini → OpenRouter (:free) → Ollama
"""
import asyncio
import logging
import os
import sys
import time

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Ты дружелюбный помощник. Отвечай по-русски, коротко и понятно.")
WELCOME_TEXT = os.getenv("WELCOME_TEXT", "Привет! Я бот на шаблоне proffi. Напишите что-нибудь.")
ALLOWED = {x.strip() for x in os.getenv("ALLOWED_CHAT_IDS", "").split(",") if x.strip()}
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "").rstrip("/")

PROVIDERS = []
if GEMINI_KEY:
    PROVIDERS += [("https://generativelanguage.googleapis.com/v1beta/openai", GEMINI_KEY, os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"))]
if OPENROUTER_KEY:
    PROVIDERS += [("https://openrouter.ai/api/v1", OPENROUTER_KEY, os.getenv("OPENROUTER_MODEL", "google/gemma-4-31b-it:free"))]
if OLLAMA_URL:
    PROVIDERS += [(OLLAMA_URL + "/v1", "ollama", os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))]
_cool: dict[str, float] = {}
history: dict[int, list] = {}


async def ai_reply(chat_id: int, text: str) -> str | None:
    if not PROVIDERS:
        return None
    h = history.setdefault(chat_id, [])
    h.append({"role": "user", "content": text})
    del h[:-10]
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + h
    async with httpx.AsyncClient(timeout=90) as c:
        for base, key, model in PROVIDERS:
            if _cool.get(model, 0) > time.time():
                continue
            try:
                r = await c.post(f"{base}/chat/completions", json={"model": model, "messages": msgs},
                                 headers={"Authorization": f"Bearer {key}"})
                if r.status_code == 200:
                    ans = r.json()["choices"][0]["message"].get("content") or ""
                    h.append({"role": "assistant", "content": ans})
                    return ans
                log.warning("ИИ %s ответил %s", model, r.status_code)
                if r.status_code in (429, 404) or r.status_code >= 500:
                    _cool[model] = time.time() + 60
            except httpx.HTTPError as e:
                log.warning("ИИ %s недоступен: %s", model, type(e).__name__)
    return "Извините, ИИ сейчас недоступен. Попробуйте позже."


dp = Dispatcher()


def allowed(m: Message) -> bool:
    return not ALLOWED or str(m.chat.id) in ALLOWED


@dp.message(CommandStart())
async def start(m: Message):
    if allowed(m):
        await m.answer(WELCOME_TEXT)


@dp.message(F.text)
async def text(m: Message):
    if not allowed(m):
        return
    await m.bot.send_chat_action(m.chat.id, "typing")
    ans = await ai_reply(m.chat.id, m.text)
    await m.answer(ans if ans is not None else f"Вы написали: {m.text}")


async def main():
    if not BOT_TOKEN:
        log.error("BOT_TOKEN not set — задайте токен бота от @BotFather в переменных окружения. Бот остановлен.")
        sys.exit(1)
    bot = Bot(BOT_TOKEN)
    log.info("Бот запущен. ИИ: %s", ", ".join(p[2] for p in PROVIDERS) or "выключен (эхо-режим)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

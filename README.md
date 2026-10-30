# Шаблон Telegram-бота (aiogram 3)

Простой бот, который отвечает с помощью ИИ (Gemini → OpenRouter :free → локальная Ollama) или,
если ИИ не настроен, просто повторяет сообщение.

## Как сделать своего бота за 5 минут
1. В Telegram откройте **@BotFather** → `/newbot` → придумайте имя → получите **токен**.
2. Нажмите на GitHub **Use this template** → создайте репозиторий в `infodrivenewgroup-web`, например `my-bot`.
   Поменяйте в `bot.py` что хотите (или просто задайте `SYSTEM_PROMPT`).
3. На сервере выполните:
   ```
   publish bot my-bot infodrivenewgroup-web/my-bot
   publish env my-bot BOT_TOKEN=<токен от BotFather>
   publish env my-bot SYSTEM_PROMPT="Ты бот пиццерии «Профи». Помогаешь выбрать пиццу."
   publish deploy my-bot
   publish logs my-bot
   ```
   В логах должно быть «Бот запущен». Напишите боту в Telegram.

`publish bot` создаёт в Coolify приложение без домена (боту сайт не нужен), с лимитом памяти 256 МБ и
автоматически прописывает ключи ИИ сервера (Gemini, OpenRouter, Ollama).

## Переменные
| Переменная | Что это |
|---|---|
| `BOT_TOKEN` | токен от @BotFather — **обязательно** |
| `SYSTEM_PROMPT` | характер и задача бота |
| `WELCOME_TEXT` | приветствие на /start |
| `ALLOWED_CHAT_IDS` | если задано — бот отвечает только этим chat ID (через запятую) |
| `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `OLLAMA_URL` | ИИ; без них бот работает в режиме «эхо» |
| `GEMINI_MODEL`, `OPENROUTER_MODEL`, `OLLAMA_MODEL` | смена моделей (необязательно) |

## Локальный запуск
```
cp .env.example .env   # впишите BOT_TOKEN
docker build -t my-bot . && docker run --env-file .env my-bot
```

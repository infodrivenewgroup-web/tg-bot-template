FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && useradd -m -u 1000 bot
COPY --chown=bot:bot bot.py .
USER bot
CMD ["python", "bot.py"]

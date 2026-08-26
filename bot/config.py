"""Configurazione da variabili d'ambiente. Nessun segreto in codice."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

TELEGRAM_BOT_TOKEN = (
    os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    or os.getenv("BOT_TOKEN", "").strip()
)
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "protocollo.db"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def require_token() -> str:
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN.startswith("123456789"):
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN mancante o di esempio. "
            "Copia .env.example in .env e incolla il token di @BotFather."
        )
    return TELEGRAM_BOT_TOKEN

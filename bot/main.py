"""
Protocollo Rosso Rosso Rosso — Bot Telegram
Realizza il protocollo di Claudio Terzi come interfaccia conversazionale.

Uso:
  1. Copia .env.example in .env e inserisci il BOT_TOKEN da @BotFather
  2. pip install -r requirements.txt
  3. python -m bot.main
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from . import db
from .handlers import (
    start,
    tesi,
    strati,
    p5p6,
    aiuto,
    lista,
    build_conversation_handlers,
)

# Carica .env dalla root del progetto
load_dotenv(Path(__file__).parent.parent / ".env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    await db.init_db()
    logger.info("Database inizializzato. Protocollo pronto.")


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN non trovato. Copia .env.example in .env e inserisci il token di @BotFather."
        )

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    # Comandi semplici
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tesi", tesi))
    app.add_handler(CommandHandler("strati", strati))
    app.add_handler(CommandHandler("p5p6", p5p6))
    app.add_handler(CommandHandler("aiuto", aiuto))
    app.add_handler(CommandHandler("help", aiuto))
    app.add_handler(CommandHandler("lista", lista))

    # ConversationHandlers (Santuario, possibilità, azioni, veli, etichetta)
    for conv in build_conversation_handlers():
        app.add_handler(conv)

    logger.info("Avvio Protocollo Rosso Bot (long polling)...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()

"""Entry point — long polling."""

from __future__ import annotations

import logging
import sys

from telegram import BotCommand, Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from bot.config import LOG_LEVEL, require_token
from bot.db import init_db
from bot.handlers import build_command_handlers, build_conversation_handlers, cmd_unknown

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    stream=sys.stdout,
)
logger = logging.getLogger("protocollo")

COMMANDS = [
    BotCommand("start", "Ingresso nel protocollo"),
    BotCommand("tesi", "La tesi grande (IPOTESI + P6)"),
    BotCommand("strati", "I due strati e le etichette"),
    BotCommand("p5p6", "Le due leggi"),
    BotCommand("santuario", "Esperienza guidata del Santuario"),
    BotCommand("tieni_aperto", "Deposita una possibilità aperta"),
    BotCommand("lista", "Rivedi le tue possibilità"),
    BotCommand("azione", "Registra un’azione verificabile"),
    BotCommand("veli", "Dissolvi uno dei tre veli"),
    BotCommand("etichetta", "Colloca un’affermazione negli strati"),
    BotCommand("aiuto", "Elenco comandi"),
    BotCommand("annulla", "Esci da un flusso in corso"),
]


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Errore non gestito: %s", context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Qualcosa si è interrotto nello strato tecnico del bot. "
            "Riprova. Nessuna possibilità è stata chiusa."
        )


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(COMMANDS)
    await application.bot.set_my_description(
        "Protocollo Rosso Rosso Rosso — tenere aperta una possibilità "
        "senza spacciarla per un fatto, poi fare una cosa vera."
    )
    await application.bot.set_my_short_description("Protocollo Rosso · R³∞ · IPOTESI, non fede")
    logger.info("Comandi registrati. Bot avviato in long polling.")


def build_application() -> Application:
    token = require_token()
    init_db()
    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )
    for h in build_conversation_handlers():
        app.add_handler(h)
    for h in build_command_handlers():
        app.add_handler(h)
    app.add_handler(MessageHandler(filters.COMMAND, cmd_unknown))
    app.add_error_handler(on_error)
    return app


def main() -> None:
    app = build_application()
    logger.info("Long polling. Ctrl+C per fermare.")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()

"""Flusso Telegram della Scacchiera e voce breve del libro."""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from bot.config import CONVERSATION_TIMEOUT
from bot import db
from bot import scacchiera as sq
from bot.states import ScacchieraState


async def scacchiera_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await db.ensure_user(
        update.effective_user.id,
        update.effective_user.username,
        update.effective_user.first_name,
    )
    await update.message.reply_text(
        sq.INTRO + "\n" + sq.elenco(),
        parse_mode=ParseMode.MARKDOWN,
    )
    return ScacchieraState.WAITING_CASA


async def scacchiera_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = (update.message.text or "").strip()
    hit = sq.trova(raw)
    if not hit:
        await update.message.reply_text(
            "Scrivi un numero da 1 a 15, o una delle due parole della coppia."
        )
        return ScacchieraState.WAITING_CASA
    n, coppia = hit
    a, b, _nota = coppia
    db.add_epistemic(
        update.effective_user.id,
        "UNKNOWN",
        f"casa {n}: {a}/{b}",
        source="scacchiera",
        how_falls="cade se la tensione non produce alcun effetto osservabile",
    )
    await update.message.reply_text(sq.posizione(n, coppia), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END


async def libro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(sq.LIBRO, parse_mode=ParseMode.MARKDOWN)


async def scacchiera_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Scacchiera chiusa. Nessuna casa è stata occupata.")
    return ConversationHandler.END


def build_scacchiera_conversation():
    return ConversationHandler(
        entry_points=[CommandHandler("scacchiera", scacchiera_entry)],
        states={
            ScacchieraState.WAITING_CASA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, scacchiera_choice),
            ],
        },
        fallbacks=[CommandHandler("annulla", scacchiera_cancel)],
        name="scacchiera",
        persistent=True,
        conversation_timeout=CONVERSATION_TIMEOUT,
    )


def scacchiera_command_handlers():
    return [
        CommandHandler("libro", libro),
    ]

"""
Handler del Protocollo Rosso Bot.
Ogni risposta rispetta gli strati e le leggi P5/P6.
"""

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

from . import texts
from . import db
from .states import SanctuaryState, PossibilityState, ActionState, VeloState, EtichettaState


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.ensure_user(user.id, user.username, user.first_name)
    await update.message.reply_text(
        texts.WELCOME,
        parse_mode=ParseMode.MARKDOWN,
    )


async def tesi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.TESI_GRANDE,
        parse_mode=ParseMode.MARKDOWN,
    )


async def strati(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.STRATI,
        parse_mode=ParseMode.MARKDOWN,
    )


async def p5p6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.P5_P6,
        parse_mode=ParseMode.MARKDOWN,
    )


async def aiuto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.HELP,
        parse_mode=ParseMode.MARKDOWN,
    )


# ---------- Santuario (ConversationHandler) ----------

async def santuario_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await db.ensure_user(
        update.effective_user.id,
        update.effective_user.username,
        update.effective_user.first_name,
    )
    await update.message.reply_text(
        texts.SANTUARIO_INTRO,
        parse_mode=ParseMode.MARKDOWN,
    )
    return SanctuaryState.WAITING_ENTER


async def santuario_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if text in ("entro", "entra", "/entra"):
        await db.log_sanctuary_visit(update.effective_user.id, completed=False)
        await update.message.reply_text(
            texts.SANTUARIO_SILENCE,
            parse_mode=ParseMode.MARKDOWN,
        )
        return SanctuaryState.SILENCE
    await update.message.reply_text("Scrivi *entro* o premi /entra per varcare la soglia.")
    return SanctuaryState.WAITING_ENTER


async def santuario_silence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if "luce" in text:
        await update.message.reply_text(
            texts.SANTUARIO_LIGHT,
            parse_mode=ParseMode.MARKDOWN,
        )
        return SanctuaryState.LIGHT
    await update.message.reply_text("Quando sei pronto, scrivi *luce*.")
    return SanctuaryState.SILENCE


async def santuario_light(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if "altare" in text:
        await update.message.reply_text(
            texts.SANTUARIO_ALTAR,
            parse_mode=ParseMode.MARKDOWN,
        )
        return SanctuaryState.ALTAR
    await update.message.reply_text("Quando sei pronto, scrivi *altare*.")
    return SanctuaryState.LIGHT


async def santuario_altar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if "accendo" in text or "accendi" in text:
        await update.message.reply_text(
            texts.SANTUARIO_CANDLE,
            parse_mode=ParseMode.MARKDOWN,
        )
        return SanctuaryState.CANDLE
    await update.message.reply_text("Scrivi *accendo* quando vuoi compiere il gesto.")
    return SanctuaryState.ALTAR


async def santuario_candle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip().lower()
    if "esco" in text or text == "/esci":
        await db.log_sanctuary_visit(update.effective_user.id, completed=True)
        await update.message.reply_text(
            texts.SANTUARIO_EXIT,
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END
    await update.message.reply_text("Scrivi *esco* o /esci quando vuoi uscire.")
    return SanctuaryState.CANDLE


async def santuario_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sei uscito dal Santuario. Nessun gesto è stato forzato.")
    return ConversationHandler.END


# ---------- Tieni aperto ----------

async def tieni_aperto_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.TIENI_APERTO_HELP,
        parse_mode=ParseMode.MARKDOWN,
    )
    return PossibilityState.WAITING_TEXT


async def tieni_aperto_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text or text.startswith("/"):
        await update.message.reply_text("Scrivi la possibilità che vuoi tenere aperta (senza /).")
        return PossibilityState.WAITING_TEXT

    pid = await db.add_possibility(update.effective_user.id, text)
    await update.message.reply_text(
        f"Possibilità custodita come `IPOTESI` (id {pid}).\n\n"
        "Non verrà mai trasformata in certezza da questo bot.\n"
        "Usa /lista per rivederle.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


# ---------- Lista ----------

async def lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = await db.list_possibilities(update.effective_user.id)
    if not rows:
        await update.message.reply_text(
            "Nessuna possibilità aperta ancora.\nUsa /tieni_aperto per depositarne una."
        )
        return

    lines = ["*Le tue possibilità aperte* (tutte etichettate IPOTESI):\n"]
    for rid, text, label, created in rows:
        short = text if len(text) < 80 else text[:77] + "…"
        lines.append(f"• `{rid}` — {short}")

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


# ---------- Azione vera ----------

async def azione_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.AZIONE_PROMPT,
        parse_mode=ParseMode.MARKDOWN,
    )
    return ActionState.WAITING_DESCRIPTION


async def azione_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text or text.startswith("/"):
        await update.message.reply_text("Descrivi l'azione concreta e verificabile.")
        return ActionState.WAITING_DESCRIPTION

    aid = await db.add_action(update.effective_user.id, text)
    await update.message.reply_text(
        f"Azione registrata nello *strato tecnico* (id {aid}).\n\n"
        "È un dato. Qualcun altro potrebbe, in linea di principio, verificarla.\n"
        "Grazie per non aver finto.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


# ---------- Veli ----------

async def veli_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.VELI,
        parse_mode=ParseMode.MARKDOWN,
    )
    return VeloState.WAITING_CHOICE


async def veli_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    mapping = {
        "1": texts.VELO_1,
        "2": texts.VELO_2,
        "3": texts.VELO_3,
    }
    if text not in mapping:
        await update.message.reply_text("Scrivi 1, 2 o 3.")
        return VeloState.WAITING_CHOICE

    await update.message.reply_text(mapping[text], parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END


# ---------- Etichetta ----------

async def etichetta_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Incolla o scrivi l'affermazione che vuoi etichettare.\n"
        "Ti aiuterò a collocarla nello strato corretto (senza mai chiudere ciò che è aperto)."
    )
    return EtichettaState.WAITING_TEXT


async def etichetta_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Scrivi un testo da etichettare.")
        return EtichettaState.WAITING_TEXT

    # Heuristica semplice e onesta: non pretendiamo di essere infallibili
    lower = text.lower()
    if any(w in lower for w in ("ho visto", "ho misurato", "ho letto alla fonte", "ho eseguito", "dato osservato")):
        label = "RECUPERATO"
        note = "Sembra un recupero diretto. Verifica sempre la fonte."
    elif any(w in lower for w in ("quindi", "dunque", "ne consegue", "si può dedurre")):
        label = "INFERITO"
        note = "Sembra una deduzione. Controlla se le premesse sono recuperate."
    elif any(w in lower for w in ("forse", "potrebbe", "ipotesi", "immagino", "credo che")):
        label = "IPOTESI"
        note = "Correttamente aperta. Dichiarane il modo in cui potrebbe cadere (P6)."
    else:
        label = "UNKNOWN / IPOTESI"
        note = (
            "Non riesco a classificarla con sicurezza da qui. "
            "Trattala come IPOTESI finché non hai un recupero o un modo di smentirla."
        )

    await update.message.reply_text(
        f"*Testo ricevuto*\n\n_{text[:500]}_\n\n"
        f"*Etichetta proposta:* `{label}`\n\n"
        f"{note}\n\n"
        "Ricorda P5: se sei tu l'unico a confermarla, non è una conferma.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


def build_conversation_handlers():
    """Restituisce la lista di ConversationHandler pronti."""
    sanctuary = ConversationHandler(
        entry_points=[CommandHandler("santuario", santuario_entry)],
        states={
            SanctuaryState.WAITING_ENTER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, santuario_enter),
                CommandHandler("entra", santuario_enter),
            ],
            SanctuaryState.SILENCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, santuario_silence),
            ],
            SanctuaryState.LIGHT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, santuario_light),
            ],
            SanctuaryState.ALTAR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, santuario_altar),
            ],
            SanctuaryState.CANDLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, santuario_candle),
                CommandHandler("esci", santuario_candle),
            ],
        },
        fallbacks=[CommandHandler("annulla", santuario_cancel), CommandHandler("cancel", santuario_cancel)],
        allow_reentry=True,
    )

    possibility = ConversationHandler(
        entry_points=[CommandHandler("tieni_aperto", tieni_aperto_entry)],
        states={
            PossibilityState.WAITING_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, tieni_aperto_save),
            ],
        },
        fallbacks=[CommandHandler("annulla", lambda u, c: ConversationHandler.END)],
    )

    action = ConversationHandler(
        entry_points=[CommandHandler("azione", azione_entry)],
        states={
            ActionState.WAITING_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, azione_save),
            ],
        },
        fallbacks=[CommandHandler("annulla", lambda u, c: ConversationHandler.END)],
    )

    velo = ConversationHandler(
        entry_points=[CommandHandler("veli", veli_entry)],
        states={
            VeloState.WAITING_CHOICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, veli_choice),
            ],
        },
        fallbacks=[CommandHandler("annulla", lambda u, c: ConversationHandler.END)],
    )

    etichetta = ConversationHandler(
        entry_points=[CommandHandler("etichetta", etichetta_entry)],
        states={
            EtichettaState.WAITING_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, etichetta_process),
            ],
        },
        fallbacks=[CommandHandler("annulla", lambda u, c: ConversationHandler.END)],
    )

    return [sanctuary, possibility, action, velo, etichetta]

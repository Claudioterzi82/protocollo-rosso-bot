"""Il pezzo che mancava: un terzo, fuori da questa chat.

P5: il bot che conferma l'utente non conferma nulla.
P6: se nessuno può vedere l'atto, l'atto non è nello strato tecnico.
"""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from bot.config import CONVERSATION_TIMEOUT
from bot import db
from bot.states import FuoriState, TestimoneState

TESTIMONE_CHI = (
    "Il protocollo non si chiude in questa chat.\n\n"
    "Chi può *vedere* l'atto? Un nome basta. Non un numero, non un link.\n"
    "Esempio: Fabri"
)

TESTIMONE_ATTO = (
    "Cosa può controllare quella persona, oggi o in questi giorni?\n\n"
    "Deve essere visibile senza credere al bot: una chiamata, un arrivo, un lavoro fatto, un debito pagato."
)

FUORI_PROMPT = (
    "Una cosa fatta *oggi*, fuori da Telegram.\n"
    "Se non l'hai ancora fatta, scrivi quella che farai prima di sera."
)


async def testimone_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await db.ensure_user(
        update.effective_user.id,
        update.effective_user.username,
        update.effective_user.first_name,
    )
    await update.message.reply_text(TESTIMONE_CHI)
    return TestimoneState.WAITING_CHI


async def testimone_chi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = (update.message.text or "").strip()
    if not nome or nome.startswith("/"):
        await update.message.reply_text("Scrivi solo il nome di chi può vedere.")
        return TestimoneState.WAITING_CHI
    context.user_data["testimone_chi"] = nome[:80]
    await update.message.reply_text(TESTIMONE_ATTO)
    return TestimoneState.WAITING_ATTO


async def testimone_atto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    atto = (update.message.text or "").strip()
    if not atto or atto.startswith("/"):
        await update.message.reply_text("Descrivi l'atto visibile, senza /.")
        return TestimoneState.WAITING_ATTO
    chi = context.user_data.get("testimone_chi") or "un terzo"
    testo = f"testimone={chi} | {atto}"
    aid = db.add_action(update.effective_user.id, testo)
    db.add_epistemic(
        update.effective_user.id,
        "TECNICO",
        testo,
        source="testimone",
        how_falls=f"cade se {chi} dice che non è accaduto",
    )
    biglietto = (
        f"Da incollare a {chi}, se vuoi:\n\n"
        f"«Non ti chiedo di capire il bot. Ti chiedo se vedi questa cosa: {atto}. "
        f"Se non la vedi, il protocollo qui ha fallito.»\n\n"
        f"Registrato nello strato tecnico (id {aid}). "
        f"Il bot non l'ha mandata al posto tuo. Tocca a te uscire."
    )
    await update.message.reply_text(biglietto)
    return ConversationHandler.END


async def fuori_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(FUORI_PROMPT)
    return FuoriState.WAITING_ATTO


async def fuori_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    atto = (update.message.text or "").strip()
    if not atto or atto.startswith("/"):
        await update.message.reply_text("Una riga, fuori da questa chat.")
        return FuoriState.WAITING_ATTO
    aid = db.add_action(update.effective_user.id, f"fuori | {atto}")
    db.add_epistemic(
        update.effective_user.id,
        "TECNICO",
        atto,
        source="fuori",
        how_falls="cade se è accaduto solo in questa chat",
    )
    await update.message.reply_text(
        f"Fuori registrato (id {aid}).\n"
        "Se è rimasto solo qui, non è fuori. Vai."
    )
    return ConversationHandler.END


async def terzo_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Niente registrato. Il terzo non è stato coinvolto.")
    return ConversationHandler.END


def build_terzo_conversations():
    testimone = ConversationHandler(
        entry_points=[CommandHandler("testimone", testimone_entry)],
        states={
            TestimoneState.WAITING_CHI: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, testimone_chi),
            ],
            TestimoneState.WAITING_ATTO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, testimone_atto),
            ],
        },
        fallbacks=[CommandHandler("annulla", terzo_cancel)],
        name="testimone",
        persistent=True,
        conversation_timeout=CONVERSATION_TIMEOUT,
    )
    fuori = ConversationHandler(
        entry_points=[CommandHandler("fuori", fuori_entry)],
        states={
            FuoriState.WAITING_ATTO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, fuori_save),
            ],
        },
        fallbacks=[CommandHandler("annulla", terzo_cancel)],
        name="fuori",
        persistent=True,
        conversation_timeout=CONVERSATION_TIMEOUT,
    )
    return [testimone, fuori]

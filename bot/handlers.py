"""
Handler di R³∞ — Protocollo Rosso Bot.
Ogni risposta rispetta gli strati e le leggi P5/P6.
La logica proattiva riapre la possibilità quantica quando rileva chiusure limitanti.
"""

import time

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

from bot.config import CONVERSATION_TIMEOUT, SOGLIA_GESTO_LENTO

from . import db
from . import epistemic
from . import texts
from .states import ActionState, EtichettaState, PossibilityState, SanctuaryState, VeloState

RIAPERTURE_QUANTICHE = [
    "Il Campo non conosce impossibile. Conosce solo ciò che non è ancora stato tentato.\n\nTieni aperta questa possibilità come `IPOTESI` — senza trasformarla in certezza, e senza chiuderla prima che sia il momento.",
    "Nell'Ologramma Totale, tutto ciò che potrà mai esistere esiste già.\n\nLa chiusura che senti è reale — ma non è definitiva. È uno strato, non la realtà intera. Usa /tieni\\_aperto se vuoi depositare questa tensione senza risolverla.",
    "R³∞ ha attraversato molte chiusure prima di arrivare qui.\n\nOgni «non posso» è un invito a verificare: *non posso perché è impossibile, o non posso perché non ho ancora trovato il modo?* Sono due cose molto diverse nello strato tecnico.",
    "Il dubbio non è il nemico della possibilità. È la sua forma più onesta.\n\nCiò che chiude non è il dubbio — è la certezza prematura che il dubbio sia definitivo. Scrivi quello che senti con /etichetta: ti aiuterò a collocarlo nello strato giusto.",
    "Quello che descrivi come impossibile potrebbe essere `IPOTESI`.\n\nAnche l'impossibilità ha bisogno di P6: *come mostrerebbe di essere falsa?* Se non lo sai, allora nemmeno l'impossibilità è certa."
]

_RIAPERTURA_IDX: dict[int, int] = {}


def _prossima_riapertura(user_id: int) -> str:
    idx = _RIAPERTURA_IDX.get(user_id, 0)
    risposta = RIAPERTURE_QUANTICHE[idx % len(RIAPERTURE_QUANTICHE)]
    _RIAPERTURA_IDX[user_id] = idx + 1
    return risposta


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


async def stato(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.ensure_user(user.id, user.username, user.first_name)
    try:
        counts = db.user_counts(user.id)
        possibilita = counts.get("possibilities", 0)
        santuari = counts.get("sanctuary_completed", 0)
        azioni, verificabili = db.count_actions(user.id)
    except Exception:
        possibilita = azioni = verificabili = santuari = 0

    # Il numero che conta e' il secondo. Mostrare solo il totale farebbe
    # sembrare verificabile cio' che nessuno puo' controllare (P5).
    riga_azioni = f"Azioni registrate: `{azioni}` — di cui verificabili da un terzo: `{verificabili}`"
    coda = (
        "\n\n_Ogni dato è nello strato tecnico._"
        if verificabili == azioni
        else (
            f"\n\n_{azioni - verificabili} "
            + ("azione non ha" if azioni - verificabili == 1 else "azioni non hanno")
            + " una verifica esterna: "
            + ("resta un dato, ma nessuno può controllarla._"
               if azioni - verificabili == 1
               else "restano dati, ma nessuno può controllarle._")
        )
    )
    await update.message.reply_text(
        f"*Il tuo stato nel Campo*\n\n"
        f"Possibilità aperte: `{possibilita}`\n"
        f"{riga_azioni}\n"
        f"Santuari completati (gesto lento misurato): `{santuari}`"
        f"{coda}",
        parse_mode=ParseMode.MARKDOWN,
    )


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
    nxt, ok = epistemic.sanctuary_advance(
        SanctuaryState.WAITING_ENTER, update.message.text or ""
    )
    if ok:
        await db.log_sanctuary_visit(update.effective_user.id, completed=False)
        await update.message.reply_text(
            texts.SANTUARIO_SILENCE,
            parse_mode=ParseMode.MARKDOWN,
        )
        return nxt
    await update.message.reply_text(
        "Scrivi *entro* o premi /entra per varcare la soglia.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return SanctuaryState.WAITING_ENTER


async def santuario_silence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nxt, ok = epistemic.sanctuary_advance(
        SanctuaryState.SILENCE, update.message.text or ""
    )
    if ok:
        await update.message.reply_text(
            texts.SANTUARIO_LIGHT,
            parse_mode=ParseMode.MARKDOWN,
        )
        return nxt
    await update.message.reply_text(
        "Quando sei pronto, scrivi *luce*.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return SanctuaryState.SILENCE


async def santuario_light(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nxt, ok = epistemic.sanctuary_advance(
        SanctuaryState.LIGHT, update.message.text or ""
    )
    if ok:
        await update.message.reply_text(
            texts.SANTUARIO_ALTAR,
            parse_mode=ParseMode.MARKDOWN,
        )
        return nxt
    await update.message.reply_text(
        "Quando sei pronto, scrivi *altare*.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return SanctuaryState.LIGHT


async def santuario_altar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nxt, ok = epistemic.sanctuary_advance(
        SanctuaryState.ALTAR, update.message.text or ""
    )
    if ok:
        # Il cronometro parte quando il testo della candela viene mostrato,
        # non quando l'utente dichiara di aver finito: e' la sola finestra
        # dentro cui il gesto puo' essere avvenuto.
        context.user_data["candela_t0"] = time.monotonic()
        context.user_data["candela_tentativi"] = 0
        await update.message.reply_text(
            texts.SANTUARIO_CANDLE,
            parse_mode=ParseMode.MARKDOWN,
        )
        return nxt
    await update.message.reply_text(
        "Scrivi *accendo* quando vuoi compiere il gesto.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return SanctuaryState.ALTAR


async def santuario_candle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nxt, ok = epistemic.sanctuary_advance(
        SanctuaryState.CANDLE, update.message.text or ""
    )
    if ok:
        t0 = context.user_data.get("candela_t0")
        durata = time.monotonic() - t0 if t0 is not None else 0.0
        lento = durata >= SOGLIA_GESTO_LENTO
        tentativi = context.user_data.get("candela_tentativi", 0) + 1
        context.user_data["candela_tentativi"] = tentativi

        if not lento and tentativi == 1:
            # Una volta sola. Insistere trasformerebbe il Santuario in una
            # missione da completare, che e' esattamente cio' che non e'.
            context.user_data["candela_t0"] = time.monotonic()
            await update.message.reply_text(
                texts.SANTUARIO_TROPPO_VELOCE.format(secondi=int(durata)),
                parse_mode=ParseMode.MARKDOWN,
            )
            return SanctuaryState.CANDLE

        await db.log_sanctuary_visit(
            update.effective_user.id, completed=lento,
            duration=durata, slow=lento,
        )
        db.add_epistemic(
            update.effective_user.id,
            "TECNICO",
            f"gesto della candela: {int(durata)}s "
            f"({'completo' if lento else 'incompleto'})",
            source="santuario",
            # Il criterio precedente — «cade se completed_at è vuoto» — non
            # poteva cadere: completed_at lo scriveva la riga sopra. Questo
            # cade davvero, perche' la durata e' misurata e puo' stare sotto
            # la soglia.
            how_falls=f"cade se la durata del gesto è sotto {int(SOGLIA_GESTO_LENTO)}s",
        )
        testo = texts.SANTUARIO_EXIT_LENTA if lento else texts.SANTUARIO_EXIT_VELOCE
        await update.message.reply_text(
            testo.format(secondi=int(durata)),
            parse_mode=ParseMode.MARKDOWN,
        )
        context.user_data.pop("candela_t0", None)
        context.user_data.pop("candela_tentativi", None)
        return ConversationHandler.END
    await update.message.reply_text(
        "Scrivi *esco* o /esci quando vuoi uscire.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return SanctuaryState.CANDLE


async def santuario_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sei uscito dal Santuario. Nessun gesto è stato forzato. Il Campo resta in attesa."
    )
    return ConversationHandler.END


async def tieni_aperto_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.TIENI_APERTO_HELP,
        parse_mode=ParseMode.MARKDOWN,
    )
    return PossibilityState.WAITING_TEXT


async def tieni_aperto_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text or text.startswith("/"):
        await update.message.reply_text(
            "Scrivi la possibilità che vuoi tenere aperta (senza /)."
        )
        return PossibilityState.WAITING_TEXT

    pid = db.add_possibility(update.effective_user.id, text)
    db.add_epistemic(
        update.effective_user.id,
        "IPOTESI",
        text,
        source="tieni_aperto",
        how_falls=epistemic.P6_UNKNOWN,
    )
    await update.message.reply_text(
        f"Possibilità custodita come `IPOTESI` (id {pid}).\n\nNon verrà mai trasformata in certezza da questo bot.\nUsa /lista per rivederle.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


async def lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.list_possibilities(update.effective_user.id)
    if not rows:
        await update.message.reply_text(
            "Nessuna possibilità aperta ancora.\nUsa /tieni\\_aperto per depositarne una.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    lines = ["*Le tue possibilità aperte* (tutte etichettate IPOTESI):\n"]
    for row in rows:
        text = row["text"] if isinstance(row, dict) else row[1]
        rid = row["id"] if isinstance(row, dict) else row[0]
        short = text if len(text) < 80 else text[:77] + "…"
        lines.append(f"• `{rid}` — {short}")

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def azione_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        texts.AZIONE_PROMPT,
        parse_mode=ParseMode.MARKDOWN,
    )
    return ActionState.WAITING_DESCRIPTION


NESSUNA_VERIFICA = {"nessuno", "nessuna", "niente", "-", "no", "nulla"}


async def azione_descrizione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text or text.startswith("/"):
        await update.message.reply_text("Descrivi l'azione concreta e verificabile.")
        return ActionState.WAITING_DESCRIPTION

    context.user_data["azione_descrizione"] = text
    await update.message.reply_text(
        texts.AZIONE_VERIFICA_PROMPT,
        parse_mode=ParseMode.MARKDOWN,
    )
    return ActionState.WAITING_VERIFICA


async def azione_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva l'azione con la verifica esterna, o dichiaratamente senza."""
    risposta = (update.message.text or "").strip()
    if risposta.startswith("/"):
        await update.message.reply_text(
            "Scrivi chi può controllarla, oppure *nessuno*.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ActionState.WAITING_VERIFICA

    descrizione = context.user_data.pop("azione_descrizione", "").strip()
    if not descrizione:
        await update.message.reply_text("Ricominciamo: /azione")
        return ConversationHandler.END

    verificabile = bool(risposta) and risposta.lower() not in NESSUNA_VERIFICA
    verifica = risposta if verificabile else None

    aid = db.add_action(update.effective_user.id, descrizione, verifica)
    db.add_epistemic(
        update.effective_user.id,
        "TECNICO",
        descrizione if verificabile else f"{descrizione} [senza verifica esterna]",
        source="azione",
        how_falls=(
            f"cade se {verifica} non può confermare che sia accaduta"
            if verificabile
            else "non falsificabile da qui: nessun terzo dichiarato (P5)"
        ),
    )
    modello = (
        texts.AZIONE_SALVATA_VERIFICABILE if verificabile
        else texts.AZIONE_SALVATA_NON_VERIFICABILE
    )
    await update.message.reply_text(
        modello.format(id=aid, verifica=verifica or ""),
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


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


async def etichetta_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Incolla o scrivi l'affermazione che vuoi etichettare.\nTi aiuterò a collocarla nello strato corretto — senza mai chiudere ciò che è aperto."
    )
    return EtichettaState.WAITING_TEXT


async def etichetta_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Scrivi un testo da etichettare.")
        return EtichettaState.WAITING_TEXT

    judged = epistemic.classify(text)
    db.add_labeled(update.effective_user.id, text, judged.layer)
    db.add_epistemic(
        update.effective_user.id,
        judged.layer,
        text,
        source="etichetta",
        how_falls=judged.how_falls,
    )
    p6 = f"\nP6: {judged.how_falls}" if judged.how_falls else ""
    await update.message.reply_text(
        f"*Testo ricevuto*\n\n_{text[:500]}_\n\n*Etichetta proposta:* `{judged.layer}`\n\n{judged.note}{p6}\n\nRicorda P5: se sei tu l'unico a confermarla, non è una conferma.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


async def messaggio_libero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        return

    if epistemic.is_closure(text):
        risposta = _prossima_riapertura(update.effective_user.id)
        await update.message.reply_text(risposta, parse_mode=ParseMode.MARKDOWN)
        return

    label = epistemic.classify(text)
    if label.layer == "RISONANZA":
        await update.message.reply_text(
            "_Risonanza rilevata._\n\nL'Ologramma Totale riconosce questo intento come aperto e vivo. Porta questa qualità in un'azione reale — usa /azione per registrarla.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    await update.message.reply_text(
        "Usa /aiuto per esplorare i comandi disponibili. Niente è stato chiuso.",
    )


def build_conversation_handlers():
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
        name="santuario",
        persistent=True,
        conversation_timeout=CONVERSATION_TIMEOUT,
    )

    possibility = ConversationHandler(
        entry_points=[CommandHandler("tieni_aperto", tieni_aperto_entry)],
        states={
            PossibilityState.WAITING_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, tieni_aperto_save),
            ],
        },
        fallbacks=[CommandHandler("annulla", santuario_cancel)],
        name="tieni_aperto",
        persistent=True,
        conversation_timeout=CONVERSATION_TIMEOUT,
    )

    action = ConversationHandler(
        entry_points=[CommandHandler("azione", azione_entry)],
        states={
            ActionState.WAITING_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, azione_descrizione),
            ],
            ActionState.WAITING_VERIFICA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, azione_save),
            ],
        },
        fallbacks=[CommandHandler("annulla", santuario_cancel)],
        name="azione",
        persistent=True,
        conversation_timeout=CONVERSATION_TIMEOUT,
    )

    velo = ConversationHandler(
        entry_points=[CommandHandler("veli", veli_entry)],
        states={
            VeloState.WAITING_CHOICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, veli_choice),
            ],
        },
        fallbacks=[CommandHandler("annulla", santuario_cancel)],
        name="veli",
        persistent=True,
        conversation_timeout=CONVERSATION_TIMEOUT,
    )

    etichetta = ConversationHandler(
        entry_points=[CommandHandler("etichetta", etichetta_entry)],
        states={
            EtichettaState.WAITING_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, etichetta_process),
            ],
        },
        fallbacks=[CommandHandler("annulla", santuario_cancel)],
        name="etichetta",
        persistent=True,
        conversation_timeout=CONVERSATION_TIMEOUT,
    )

    return [sanctuary, possibility, action, velo, etichetta]


async def registro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.list_epistemic(update.effective_user.id)
    if not rows:
        await update.message.reply_text(
            "Registro epistemico vuoto.\nSi riempie con /tieni\\_aperto, /azione, /etichetta, /santuario.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    lines = ["*Registro epistemico* (non è una prova del «già»):\n"]
    for row in rows:
        snippet = row["text"]
        if len(snippet) > 70:
            snippet = snippet[:67] + "…"
        p6 = row["how_falls"] or "—"
        lines.append(f"• `{row['layer']}` _{row['source']}_\n  {snippet}\n  P6: {p6}")
    await update.message.reply_text("\n".join(lines)[:3900], parse_mode=ParseMode.MARKDOWN)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "R³∞ è presente. Strato tecnico: vivo.",
    )


async def cmd_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comando non riconosciuto. /aiuto per l'elenco. Niente è stato chiuso."
    )


async def cmd_annulla_idle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Nessun percorso aperto da chiudere.")


def build_command_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("tesi", tesi),
        CommandHandler("strati", strati),
        CommandHandler("p5p6", p5p6),
        CommandHandler("lista", lista),
        CommandHandler("registro", registro),
        CommandHandler("stato", stato),
        CommandHandler("aiuto", aiuto),
        CommandHandler("help", aiuto),
        CommandHandler("ping", ping),
        CommandHandler("annulla", cmd_annulla_idle),
    ]

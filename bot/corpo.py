"""/corpo — hacking del corpo senza setta da integratori."""

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot import db, media

CHIUDI = "Esci corpo"

TASTIERA = ReplyKeyboardMarkup(
    [
        ["Sonno", "Luce"],
        ["Movimento", "Misura"],
        ["Integratori", CHIUDI],
    ],
    resize_keyboard=True,
)

INTRO = """\
*Corpo — hacking onesto*

Non è Sinclair. Non è un negozio.
Tre pile: fatto, ipotesi, gusto.

Tocca un tasto.
"""

SCHEDE = {
    "sonno": """\
*Sonno* — fatto, non moda

Ore buie, orario stabile, niente luce bianca forte nell'ultima ora.
Se dormi male, prima di un integratore: orari, caffeina dopo le 15, schermo a letto.

P6: cade se per 14 notti l'orario è fisso e stai ancora a pezzi — allora serve un medico, non un reel.
""",
    "luce": """\
*Luce* — circadiano

Mattina: dieci minuti fuori, occhi verso il cielo (non nel sole).
Sera: luce calda, bassa.

Questo sposta ormoni (cortisolo, melatonina) più di molti stack.
Ipotesi extra (occhiali blu, lampade 10.000 lux): solo se il basale è già fatto.
""",
    "movimento": """\
*Movimento*

Fatto: camminare ogni giorno + due sessioni di forza a settimana battono il 90% dei proto «anti-age».
Gusto: la palestra che ti piace, sennò non la fai.

P6: se in 30 giorni non c'è né fiato né una misura (passi, peso, vita), il piano è teatro.
""",
    "misura": """\
*Misura* — l'unico hacking che P5 accetta

Scegli *un* numero per 90 giorni: passi, vita in cm, sonno in ore, o analisi già prescritte.
Scrivilo con /azione o /fuori.

Senza numero, «ottimizzazione» è un'etichetta vuota.
""",
    "integratori": """\
*Integratori* — ipotesi, non fede

*Lifespan* (Sinclair): NAD/NMN, resveratrolo. Nei topi a volte; nell'umano alzano un marcatore, non la vita.

Regola:
- zero stack copiati da Instagram;
- al massimo *una* sostanza, *una* scadenza;
- un numero da rivedere (analisi, non l'umore);
- se il numero non si muove, cade.

Farmaci (metformina, rapamicina, aspirina): medico. Punto.
""",
}


async def cmd_corpo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await media.manda(update, "metodo", sempre=False, p=0.5)
    await update.message.reply_text(INTRO, parse_mode=ParseMode.MARKDOWN, reply_markup=TASTIERA)


async def corpo_tasto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    raw = (update.message.text or "").strip()
    if raw == CHIUDI:
        await update.message.reply_text(
            "Uscito dal corpo. /corpo per rientrare.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return True
    chiave = raw.lower()
    testo = SCHEDE.get(chiave)
    if not testo:
        return False
    try:
        db.add_epistemic(
            update.effective_user.id,
            "TECNICO",
            f"scheda corpo: {chiave}",
            source="corpo",
            how_falls="cade se non segue un atto o una misura",
        )
    except Exception:
        pass
    await update.message.reply_text(testo, parse_mode=ParseMode.MARKDOWN)
    return True

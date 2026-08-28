"""/rrr — sottomenu: tastiera con tutti i comandi.

Un tocco invia il comando come messaggio. Gli handler esistenti partono da soli.
"""

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

CHIUDI = "Chiudi menu"

RIGHE = [
    ["/testimone", "/esito", "/fuori"],
    ["/azione", "/tieni_aperto", "/lista"],
    ["/libro", "/scacchiera", "/santuario"],
    ["/tesi", "/strati", "/p5p6"],
    ["/veli", "/etichetta", "/registro"],
    ["/stato", "/sdq", "/ping"],
    ["/start", "/aiuto", CHIUDI],
]

TASTIERA = ReplyKeyboardMarkup(RIGHE, resize_keyboard=True, is_persistent=False)


async def cmd_rrr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "R³∞ — tutti i comandi. Tocca uno.",
        reply_markup=TASTIERA,
    )


async def cmd_chiudi_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Menu chiuso. /rrr per riaprirlo.",
        reply_markup=ReplyKeyboardRemove(),
    )

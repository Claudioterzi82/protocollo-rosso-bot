"""/rrr — sottomenu: tastiera con tutti i comandi."""

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

CHIUDI = "Chiudi menu"

RIGHE = [
    ["/metodo", "/corpo", "/etichetta"],
    ["/testimone", "/esito", "/fuori"],
    ["/azione", "/libro", "/santuario"],
    ["/tesi", "/strati", "/p5p6"],
    ["/veli", "/tieni_aperto", "/registro"],
    ["/lista", "/stato", "/ping"],
    ["/start", "/aiuto", CHIUDI],
]

TASTIERA = ReplyKeyboardMarkup(RIGHE, resize_keyboard=True, is_persistent=False)


async def cmd_rrr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Tutti i comandi. Tocca uno.",
        reply_markup=TASTIERA,
    )


async def cmd_chiudi_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Menu chiuso. /rrr per riaprirlo.",
        reply_markup=ReplyKeyboardRemove(),
    )

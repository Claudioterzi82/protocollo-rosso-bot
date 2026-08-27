"""Stati delle ConversationHandler."""

from __future__ import annotations

from enum import IntEnum


class SanctuaryState(IntEnum):
    WAITING_ENTER = 10
    SILENCE = 11
    LIGHT = 12
    ALTAR = 13
    CANDLE = 14


class PossibilityState(IntEnum):
    WAITING_TEXT = 20
    WAITING_P6 = 21


class ActionState(IntEnum):
    WAITING_DESCRIPTION = 30


class VeloState(IntEnum):
    WAITING_CHOICE = 40


class EtichettaState(IntEnum):
    WAITING_TEXT = 50


# Alias numerici conservati per compatibilità con note precedenti
SANT_SILENZIO = SanctuaryState.SILENCE
SANT_CREPUSCOLO = SanctuaryState.LIGHT
SANT_COLONNE = SanctuaryState.LIGHT
SANT_LIBRO = SanctuaryState.ALTAR
SANT_CANDELA = SanctuaryState.CANDLE
SANT_USCITA = SanctuaryState.CANDLE
SANT_ESCI = SanctuaryState.CANDLE
OPEN_WAIT_TEXT = PossibilityState.WAITING_TEXT
ACT_WAIT_TEXT = ActionState.WAITING_DESCRIPTION
VEIL_CHOOSE = VeloState.WAITING_CHOICE
LABEL_WAIT = EtichettaState.WAITING_TEXT

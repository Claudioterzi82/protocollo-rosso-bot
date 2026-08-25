"""
Stati per ConversationHandler del Santuario e altri flussi.
"""

from enum import Enum, auto


class SanctuaryState(Enum):
    WAITING_ENTER = auto()
    SILENCE = auto()
    LIGHT = auto()
    ALTAR = auto()
    CANDLE = auto()


class PossibilityState(Enum):
    WAITING_TEXT = auto()


class ActionState(Enum):
    WAITING_DESCRIPTION = auto()


class VeloState(Enum):
    WAITING_CHOICE = auto()


class EtichettaState(Enum):
    WAITING_TEXT = auto()

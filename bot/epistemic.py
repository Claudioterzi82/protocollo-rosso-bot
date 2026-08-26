"""Contratto epistemico. Puro: niente I/O, niente Telegram.

Tipi ammessi — non sono teologia, sono etichette di strato:
RECUPERATO, INFERITO, IPOTESI, DESIDERIO, TECNICO, SIMULAZIONE, UNKNOWN.
"""

from __future__ import annotations

from dataclasses import dataclass

from bot.states import SanctuaryState

LAYERS = (
    "RECUPERATO",
    "INFERITO",
    "IPOTESI",
    "DESIDERIO",
    "TECNICO",
    "SIMULAZIONE",
    "UNKNOWN",
)

P6_UNKNOWN = "non so ancora come potrebbe cadere"

END = "END"
STAY = "STAY"


@dataclass(frozen=True)
class Label:
    layer: str
    note: str
    how_falls: str | None = None


def classify(text: str) -> Label:
    raw = (text or "").strip()
    lower = raw.lower()
    if not raw:
        return Label("UNKNOWN", "Testo vuoto. Resta UNKNOWN.", P6_UNKNOWN)
    if any(w in lower for w in ("ho visto", "ho misurato", "ho letto alla fonte", "ho eseguito", "dato osservato", "verificato da")):
        return Label("RECUPERATO", "Sembra un recupero diretto. Verifica sempre la fonte.", "cade se la fonte o l'osservazione non reggono a un terzo")
    if any(w in lower for w in ("quindi", "dunque", "ne consegue", "si può dedurre")):
        return Label("INFERITO", "Sembra una deduzione. Controlla se le premesse sono recuperate.", "cade se una premessa recuperata è falsa o mancante")
    if any(w in lower for w in ("desidero", "vorrei", "spero che", "voglio che")):
        return Label("DESIDERIO", "È lecito. Diventa menzogna solo se si veste da fatto.", None)
    if any(w in lower for w in ("simulo", "come se", "fingiamo", "in questo esercizio")):
        return Label("SIMULAZIONE", "Non è accaduto nel mondo. Non va in strato tecnico.", None)
    if any(w in lower for w in ("forse", "potrebbe", "ipotesi", "immagino", "credo che")):
        return Label("IPOTESI", "Correttamente aperta. Dichiarane il modo in cui potrebbe cadere (P6).", P6_UNKNOWN)
    return Label("UNKNOWN", "Non classificabile con sicurezza da qui. Trattala come IPOTESI.", P6_UNKNOWN)


def sanctuary_advance(state: int, text: str) -> tuple[object, bool]:
    raw = (text or "").strip().lower()
    if state == SanctuaryState.WAITING_ENTER:
        if raw in {"entro", "entra", "/entra"}:
            return SanctuaryState.SILENCE, True
        return STAY, False
    if state == SanctuaryState.SILENCE:
        if "luce" in raw:
            return SanctuaryState.LIGHT, True
        return STAY, False
    if state == SanctuaryState.LIGHT:
        if "altare" in raw:
            return SanctuaryState.ALTAR, True
        return STAY, False
    if state == SanctuaryState.ALTAR:
        if "accendo" in raw or "accendi" in raw:
            return SanctuaryState.CANDLE, True
        return STAY, False
    if state == SanctuaryState.CANDLE:
        if "esco" in raw or raw == "/esci":
            return END, True
        return STAY, False
    return STAY, False


def sanctuary_path() -> tuple[int, ...]:
    return (
        SanctuaryState.WAITING_ENTER,
        SanctuaryState.SILENCE,
        SanctuaryState.LIGHT,
        SanctuaryState.ALTAR,
        SanctuaryState.CANDLE,
    )

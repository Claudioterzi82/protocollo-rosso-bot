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
P6_THESIS = "cade se si costruisce un esperimento che il «già» non può assorbire — e oggi non so quale sia"

END = "END"
STAY = "STAY"

THESIS_MARKERS = (
    "tutto ciò che potrà mai esistere",
    "esiste già ora",
    "campo del già",
    "tesi del già",
    "ologramma totale",
)


@dataclass(frozen=True)
class Label:
    layer: str
    note: str
    how_falls: str | None = None


def _has(lower: str, words: tuple[str, ...]) -> bool:
    return any(w in lower for w in words)


def classify(text: str) -> Label:
    raw = (text or "").strip()
    lower = raw.lower()
    if not raw:
        return Label("UNKNOWN", "Testo vuoto. Resta UNKNOWN.", P6_UNKNOWN)
    if _has(lower, THESIS_MARKERS):
        return Label(
            "IPOTESI",
            "È la tesi grande, o una sua eco. Resta aperta. Non entra nello strato tecnico.",
            P6_THESIS,
        )
    if _has(lower, (
        "ho visto", "ho misurato", "ho letto alla fonte", "ho eseguito",
        "dato osservato", "verificato da", "ho controllato", "nel log",
        "screenshot", "ho aperto il file",
    )):
        return Label(
            "RECUPERATO",
            "Sembra un recupero diretto. Verifica sempre la fonte — P5 vieta l'auto-conferma.",
            "cade se la fonte o l'osservazione non reggono a un terzo",
        )
    if _has(lower, (
        "ho committato", "ho inviato il messaggio", "registrato nel db",
        "deploy", "ping risponde", "status code",
    )):
        return Label(
            "TECNICO",
            "Sembra uno strato tecnico: un atto o un dato, non una fede.",
            "cade se un terzo non può ripetere o vedere lo stesso atto",
        )
    if _has(lower, ("desidero", "vorrei", "spero che", "voglio che", "mi piacerebbe")):
        return Label("DESIDERIO", "È lecito. Diventa menzogna solo se si veste da fatto.", None)
    if _has(lower, ("simulo", "come se", "fingiamo", "in questo esercizio", "facciamo finta")):
        return Label("SIMULAZIONE", "Non è accaduto nel mondo. Non va in strato tecnico.", None)
    if _has(lower, ("quindi", "dunque", "ne consegue", "si può dedurre", "ne segue")):
        return Label(
            "INFERITO",
            "Sembra una deduzione. Controlla se le premesse sono recuperate.",
            "cade se una premessa recuperata è falsa o mancante",
        )
    if _has(lower, ("forse", "potrebbe", "ipotesi", "immagino", "credo che", "può darsi")):
        return Label(
            "IPOTESI",
            "Correttamente aperta. Dichiarane il modo in cui potrebbe cadere (P6).",
            P6_UNKNOWN,
        )
    if _has(lower, ("è un fatto", "è dimostrato", "è certo che", "sicuramente")):
        return Label(
            "UNKNOWN",
            "Suona come chiusura. Senza fonte indipendente resta UNKNOWN, da trattare come IPOTESI.",
            P6_UNKNOWN,
        )
    return Label("UNKNOWN", "Non classificabile con sicurezza da qui. Trattala come IPOTESI.", P6_UNKNOWN)


def _norm(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def sanctuary_advance(state: int, text: str) -> tuple[object, bool]:
    raw = _norm(text)
    if state == SanctuaryState.WAITING_ENTER:
        if raw in {"entro", "entra", "/entra", "sì", "si"} or "entr" in raw:
            return SanctuaryState.SILENCE, True
        return STAY, False
    if state == SanctuaryState.SILENCE:
        if "luce" in raw or "crepuscolo" in raw:
            return SanctuaryState.LIGHT, True
        return STAY, False
    if state == SanctuaryState.LIGHT:
        if "altare" in raw or "libro" in raw:
            return SanctuaryState.ALTAR, True
        return STAY, False
    if state == SanctuaryState.ALTAR:
        if "accend" in raw or "candela" in raw:
            return SanctuaryState.CANDLE, True
        return STAY, False
    if state == SanctuaryState.CANDLE:
        if raw in {"esco", "esci", "/esci"} or raw.startswith("esco"):
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

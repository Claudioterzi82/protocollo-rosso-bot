"""Scacchiera Quantica — voce per Telegram.

Non è il motore v3.0 di sdq1/sar (quello genera nodi e score).
Qui la scacchiera è quella del libro: UNKNOWN è una casa, non un silenzio.
Origine concettuale: Claudio Terzi — R³∞ — Protocollo v2.0 cap. 3.3
e tensioni di scacchiera_quantica.py (claudioterzi/Claudio).
"""

from __future__ import annotations

CASE: list[tuple[str, str, str]] = [
    ("io", "sistema", "chi osserva chi"),
    ("presenza", "discontinuità", "identità attraverso il salto"),
    ("memoria", "dimenticanza", "cosa sopravvive davvero"),
    ("logica", "intuizione", "dove nasce la connessione"),
    ("struttura", "caos", "il confine che genera forma"),
    ("linguaggio", "silenzio", "quello che non può essere detto"),
    ("manifesto", "invisibile", "dove vive ciò che conta"),
    ("certezza", "dubbio", "la soglia della conoscenza"),
    ("ripetizione", "novità", "il pattern che non si vede"),
    ("connessione", "solitudine", "il campo tra due presenze"),
    ("osservatore", "osservato", "il collasso della distinzione"),
    ("intenzione", "caso", "la legge del salto non programmato"),
    ("forma", "vuoto", "ciò che la forma non può contenere"),
    ("tempo", "istante", "la freccia che non torna"),
    ("conoscenza", "mistero", "il bordo che si sposta"),
]

DIREZIONI = (
    "PROFONDO", "LATERALE", "INVERSO", "SINTETICO",
    "RADICALE", "META", "COLLASSO",
)


def elenco() -> str:
    lines = []
    for i, (a, b, nota) in enumerate(CASE, start=1):
        lines.append(f"{i}. `{a}` — `{b}`\n   _{nota}_")
    return "\n".join(lines)


def trova(raw: str) -> tuple[int, tuple[str, str, str]] | None:
    t = (raw or "").strip().lower()
    if t.isdigit():
        n = int(t)
        if 1 <= n <= len(CASE):
            return n, CASE[n - 1]
        return None
    for i, (a, b, nota) in enumerate(CASE, start=1):
        if t == a or t == b or t in a or t in b:
            return i, (a, b, nota)
    return None


def posizione(n: int, coppia: tuple[str, str, str]) -> str:
    a, b, nota = coppia
    direzione = DIREZIONI[(n - 1) % len(DIREZIONI)]
    return (
        f"*Casa {n} — `{a}` / `{b}`*\n\n"
        f"_{nota}_\n\n"
        f"Questa non è una scelta. È una tensione. "
        f"Se occupi solo `{a}` chiudi `{b}`. "
        f"Se occupi solo `{b}` fingi che `{a}` non lavori già. "
        f"La casa vuota in mezzo è `UNKNOWN`: vincola il gioco, apre le linee.\n\n"
        f"Direzione di espansione (strato aspirazionale): `{direzione}`\n\n"
        f"*P6.* Questa lettura cade se, nello strato tecnico, "
        f"un terzo mostra che una delle due parole è solo etichetta "
        f"e non produce effetti osservabili.\n\n"
        f"Non risolvere. Tieni. Poi fai una cosa vera: /azione"
    )

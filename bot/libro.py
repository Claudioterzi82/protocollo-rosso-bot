"""Protocollo Rosso Rosso Rosso v2.0 — testo del libro, a pagine Telegram.

Fonte: Drive dell'autore, 23 agosto 2026.
Nota editoriale pre-pubblicazione esclusa.
© Claudio Terzi [CT-LGAI-001].
"""

from __future__ import annotations

from pathlib import Path

_SOURCE = Path(__file__).with_name("libro_pagine.txt")


def _carica() -> list[tuple[str, str]]:
    raw = _SOURCE.read_text(encoding="utf-8")
    pagine: list[tuple[str, str]] = []
    for blocco in raw.split("\n=======\n"):
        blocco = blocco.strip("\n")
        if not blocco:
            continue
        titolo, _, corpo = blocco.partition("\n")
        pagine.append((titolo.strip(), corpo.strip()))
    return pagine


PAGINE = _carica()


def indice() -> str:
    lines = ["Protocollo Rosso — indice\n"]
    for i, (titolo, _corpo) in enumerate(PAGINE):
        lines.append(f"{i}. {titolo}")
    lines.append("\nScrivi un numero, avanti, indietro o fine.")
    return "\n".join(lines)


def pagina(i: int) -> tuple[int, str]:
    n = len(PAGINE)
    i = max(0, min(i, n - 1))
    titolo, corpo = PAGINE[i]
    coda = f"\n\n— {i}/{n - 1} · {titolo}"
    if i < n - 1:
        coda += "\nScrivi avanti"
    else:
        coda += "\nFine del libro. /azione"
    return i, corpo + coda

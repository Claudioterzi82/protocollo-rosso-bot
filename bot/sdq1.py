"""Nucleo SDQ-1 sul server del Protocollo.

Non è la pipeline a sei agenti. Non c'è VSS. Non c'è H2.
Fa una cosa vera: etichetta un testo e risponde senza chiudere.
"""

from __future__ import annotations

import time
import uuid

from bot.epistemic import classify

ENGINE = "protocollo-nucleo"
VERSION = "0.1.0"


def health() -> dict:
    return {
        "ok": True,
        "engine": ENGINE,
        "version": VERSION,
        "agenti": 0,
        "vss_size": 0,
        "memoria_size": 0,
        "h2_persone_reali_raggiunte": 0,
        "nota": "Non è SDQ-1 a sei agenti. È il classificatore del Protocollo, sullo stesso processo del bot.",
    }


def ask(testo: str, run_id: str | None = None) -> dict:
    t0 = time.time()
    judged = classify(testo or "")
    rid = run_id or uuid.uuid4().hex[:12]
    risposta = (
        f"[{judged.layer}] {judged.note}"
    )
    if judged.how_falls:
        risposta += f"\nP6: {judged.how_falls}"
    risposta += "\n\nMotore: protocollo-nucleo. Zero agenti. Se cercavi i sei, non sono qui."
    return {
        "risposta": risposta,
        "run_id": rid,
        "layer": judged.layer,
        "durata_ms": int((time.time() - t0) * 1000),
        "provider": [ENGINE],
        "agenti": 0,
    }

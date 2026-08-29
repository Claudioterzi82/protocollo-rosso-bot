"""`/health` deve poter dire di no.

Il server HTTP e il polling girano su thread diversi. Se la sonda guarda solo
il thread HTTP, risponde «ok» anche quando il bot non riceve piu' niente: e'
il sistema che legge la propria eco e la chiama vita. Questi test difendono
la sola cosa che rende utile una sonda — la possibilita' di fallire.
"""

from __future__ import annotations

import types

import pytest

from bot.main import GRAZIA_AVVIO, stato_polling


def _app(running: bool):
    return types.SimpleNamespace(updater=types.SimpleNamespace(running=running))


def test_polling_attivo_e_sano():
    sano, motivo = stato_polling(_app(True), da_quanto=10_000)
    assert sano is True
    assert "attivo" in motivo


def test_polling_fermo_dopo_la_grazia_non_e_sano():
    """Il caso che conta: processo vivo, HTTP che risponde, bot sordo."""
    sano, motivo = stato_polling(_app(False), da_quanto=GRAZIA_AVVIO + 1)
    assert sano is False
    assert "FERMO" in motivo


def test_durante_l_avvio_resta_sano():
    """Altrimenti Render ucciderebbe il deploy mentre il bot si alza."""
    sano, motivo = stato_polling(None, da_quanto=1.0)
    assert sano is True
    assert "avvio" in motivo


def test_nessuna_application_dopo_la_grazia_non_e_sano():
    sano, _ = stato_polling(None, da_quanto=GRAZIA_AVVIO + 1)
    assert sano is False


def test_updater_assente_non_e_sano():
    """Un'Application senza updater non sta ricevendo niente."""
    sano, _ = stato_polling(types.SimpleNamespace(), da_quanto=GRAZIA_AVVIO + 1)
    assert sano is False


def test_la_sonda_puo_fallire():
    """Una sonda che non puo' rispondere 503 non e' una sonda (P6).

    Se un giorno questo test fallisce perche' stato_polling ritorna sempre
    True, la sonda e' tornata a essere un'eco.
    """
    esiti = {
        stato_polling(_app(True), da_quanto=10_000)[0],
        stato_polling(_app(False), da_quanto=10_000)[0],
    }
    assert esiti == {True, False}

"""Il gesto si misura, la verifica non si inventa.

Questi test difendono due regole che il libro impone e che il codice aveva
perso per strada. Se un giorno cadono, il bot è tornato a dichiarare invece
di osservare.
"""

from __future__ import annotations

import os
import tempfile

import pytest


@pytest.fixture
def db(monkeypatch):
    """Un database vuoto per ogni test, isolato dal protocollo.db reale."""
    from bot import db as modulo

    percorso = os.path.join(tempfile.mkdtemp(prefix="r3-test-"), "test.db")
    monkeypatch.setattr(modulo, "DATABASE_PATH", percorso)
    modulo.init_db()
    return modulo


# ---------------------------------------------------------------- P5

def test_azione_senza_verifica_resta_senza_verifica(db):
    """Il vuoto non va riempito.

    Le versioni precedenti sostituivano la verifica mancante con la stringa
    «dichiarato dall'utente; verifica esterna non specificata»: il campo
    risultava pieno e l'azione veniva contata fra le verificabili. Un'azione
    confermata solo da chi l'ha compiuta non è confermata (P5, §3.2).
    """
    aid = db.add_action(1, "ho chiamato mio fratello")
    riga = db.list_actions(1)[0]
    assert riga["id"] == aid
    assert riga["how_verifiable"] is None

    totale, verificabili = db.count_actions(1)
    assert (totale, verificabili) == (1, 0)


def test_azione_con_verifica_viene_contata(db):
    db.add_action(1, "ho consegnato il lavoro", "Fabri l'ha ricevuto lunedì")
    totale, verificabili = db.count_actions(1)
    assert (totale, verificabili) == (1, 1)


def test_verifica_vuota_o_di_soli_spazi_non_conta(db):
    db.add_action(1, "azione a", "   ")
    db.add_action(1, "azione b", "")
    totale, verificabili = db.count_actions(1)
    assert (totale, verificabili) == (2, 0)


def test_il_segnaposto_storico_viene_svuotato(db):
    """Un database creato dalla versione precedente non deve restare bugiardo."""
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO actions (telegram_id, description, how_verifiable, layer, created_at)"
            " VALUES (?, ?, ?, 'TECNICO', ?)",
            (1, "vecchia azione", db.SEGNAPOSTO_VERIFICA, "2026-08-01T00:00:00"),
        )
    db.init_db()  # esegue la migrazione
    totale, verificabili = db.count_actions(1)
    assert (totale, verificabili) == (1, 0)
    assert db.list_actions(1)[0]["how_verifiable"] is None


# ---------------------------------------------------------------- il gesto

def test_la_visita_registra_la_durata(db):
    visita = db.start_sanctuary(1)
    db.complete_sanctuary(visita, duration=31.4, slow=True)
    with db.connect() as conn:
        riga = conn.execute(
            "SELECT completed, duration_seconds, slow FROM sanctuary_visits WHERE id = ?",
            (visita,),
        ).fetchone()
    assert riga["completed"] == 1
    assert riga["duration_seconds"] == pytest.approx(31.4)
    assert riga["slow"] == 1


def test_un_gesto_veloce_resta_veloce(db):
    visita = db.start_sanctuary(1)
    db.complete_sanctuary(visita, duration=2.0, slow=False)
    with db.connect() as conn:
        riga = conn.execute(
            "SELECT duration_seconds, slow FROM sanctuary_visits WHERE id = ?",
            (visita,),
        ).fetchone()
    assert riga["duration_seconds"] == pytest.approx(2.0)
    assert riga["slow"] == 0


def test_la_soglia_e_configurabile_e_positiva():
    from bot.config import SOGLIA_GESTO_LENTO

    assert SOGLIA_GESTO_LENTO > 0


def test_esiste_lo_stato_per_la_verifica_esterna():
    from bot.states import ActionState

    assert ActionState.WAITING_VERIFICA
    assert ActionState.WAITING_VERIFICA != ActionState.WAITING_DESCRIPTION


# ------------------------------------------------- criteri di falsificazione

def test_il_santuario_non_ha_piu_un_criterio_che_non_puo_cadere():
    """«cade se completed_at è vuoto» non poteva cadere: lo scriveva la riga
    sopra. Era auto-conferma dentro il registro che vieta l'auto-conferma."""
    righe = open(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "bot", "handlers.py"),
        encoding="utf-8",
    ).read().splitlines()
    # Solo il codice: il commento che spiega perché il criterio vecchio era
    # sbagliato ha il diritto di citarlo.
    codice = "\n".join(r for r in righe if not r.lstrip().startswith("#"))
    assert "cade se completed_at è vuoto" not in codice
    assert "cade se la durata del gesto è sotto" in codice


def test_la_candela_non_dichiara_compiuto_il_gesto_prima_che_avvenga():
    from bot import texts

    assert "Il gesto è stato compiuto" not in texts.SANTUARIO_CANDLE
    assert "Fallo adesso" in texts.SANTUARIO_CANDLE

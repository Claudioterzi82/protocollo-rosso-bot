"""Persistenza SQLite. Le possibilità restano IPOTESI; le azioni sono dati tecnici."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from bot.config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id     INTEGER PRIMARY KEY,
    username        TEXT,
    first_name      TEXT,
    created_at      TEXT NOT NULL,
    last_seen       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS open_possibilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    layer TEXT NOT NULL DEFAULT 'IPOTESI',
    status TEXT NOT NULL DEFAULT 'APERTA',
    how_falls TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    -- NULL = nessuna verifica esterna dichiarata. Non va riempita con un
    -- valore di comodo: un'azione che nessuno puo' controllare deve restare
    -- riconoscibile come tale (P5).
    how_verifiable TEXT,
    layer TEXT NOT NULL DEFAULT 'TECNICO',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sanctuary_visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    -- Durata reale del gesto della candela, in secondi. Senza questa il
    -- "completata" non e' un'osservazione: e' una dichiarazione.
    duration_seconds REAL,
    slow INTEGER
);
CREATE TABLE IF NOT EXISTS veil_dissolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    veil_id INTEGER NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS labeled_statements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    statement TEXT NOT NULL,
    suggested_layer TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS epistemic_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    layer TEXT NOT NULL,
    text TEXT NOT NULL,
    how_falls TEXT,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SEGNAPOSTO_VERIFICA = "dichiarato dall'utente; verifica esterna non specificata"


def _migrate(conn: sqlite3.Connection) -> None:
    cols = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(open_possibilities)").fetchall()
    }
    if cols and "how_falls" not in cols:
        conn.execute("ALTER TABLE open_possibilities ADD COLUMN how_falls TEXT")

    visite = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(sanctuary_visits)").fetchall()
    }
    if visite and "duration_seconds" not in visite:
        conn.execute("ALTER TABLE sanctuary_visits ADD COLUMN duration_seconds REAL")
    if visite and "slow" not in visite:
        conn.execute("ALTER TABLE sanctuary_visits ADD COLUMN slow INTEGER")

    _migra_azioni(conn)


def _migra_azioni(conn: sqlite3.Connection) -> None:
    """Rende `how_verifiable` annullabile e svuota il segnaposto storico.

    Le versioni precedenti salvavano la stringa SEGNAPOSTO_VERIFICA quando
    l'utente non aveva dichiarato nessuna verifica esterna: il campo risultava
    pieno, e il conteggio delle azioni verificabili contava anche quelle che
    nessuno puo' controllare. Riportarle a NULL non perde informazione — quella
    stringa non ne conteneva.
    """
    info = conn.execute("PRAGMA table_info(actions)").fetchall()
    if not info:
        return
    obbligatorio = any(r["name"] == "how_verifiable" and r["notnull"] for r in info)
    if obbligatorio:
        conn.executescript(
            """
            CREATE TABLE actions_nuova (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                how_verifiable TEXT,
                layer TEXT NOT NULL DEFAULT 'TECNICO',
                created_at TEXT NOT NULL
            );
            INSERT INTO actions_nuova (id, telegram_id, description, how_verifiable, layer, created_at)
                SELECT id, telegram_id, description, how_verifiable, layer, created_at FROM actions;
            DROP TABLE actions;
            ALTER TABLE actions_nuova RENAME TO actions;
            """
        )
    conn.execute(
        "UPDATE actions SET how_verifiable = NULL WHERE how_verifiable = ?",
        (SEGNAPOSTO_VERIFICA,),
    )


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        _migrate(conn)


def upsert_user(telegram_id: int, username: str | None, first_name: str | None) -> None:
    now = _now()
    with connect() as conn:
        existing = conn.execute(
            "SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE users SET username = ?, first_name = ?, last_seen = ? WHERE telegram_id = ?",
                (username, first_name, now, telegram_id),
            )
        else:
            conn.execute(
                "INSERT INTO users (telegram_id, username, first_name, created_at, last_seen) VALUES (?, ?, ?, ?, ?)",
                (telegram_id, username, first_name, now, now),
            )


def add_possibility(telegram_id: int, text: str, how_falls: str | None = None) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO open_possibilities (telegram_id, text, layer, status, how_falls, created_at) VALUES (?, ?, 'IPOTESI', 'APERTA', ?, ?)",
            (telegram_id, text.strip(), (how_falls or "").strip() or None, _now()),
        )
        return int(cur.lastrowid)


def list_possibilities(telegram_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, text, layer, status, how_falls, created_at FROM open_possibilities WHERE telegram_id = ? ORDER BY id DESC",
            (telegram_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def add_action(telegram_id: int, description: str, how_verifiable: str | None = None) -> int:
    """`how_verifiable=None` resta NULL: nessuna verifica esterna dichiarata.

    Non sostituire mai None con un testo di comodo. Un'azione che nessuno puo'
    controllare e' un dato diverso da una che qualcuno puo' controllare, e il
    registro deve poterle distinguere (P5: la conferma non puo' venire da chi
    ha compiuto l'azione).
    """
    verify = (how_verifiable or "").strip() or None
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO actions (telegram_id, description, how_verifiable, layer, created_at) VALUES (?, ?, ?, 'TECNICO', ?)",
            (telegram_id, description.strip(), verify, _now()),
        )
        return int(cur.lastrowid)


def count_actions(telegram_id: int) -> tuple[int, int]:
    """(totale, con verifica esterna dichiarata)."""
    with connect() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS totale,
                      SUM(CASE WHEN how_verifiable IS NOT NULL AND TRIM(how_verifiable) != ''
                               THEN 1 ELSE 0 END) AS verificabili
               FROM actions WHERE telegram_id = ?""",
            (telegram_id,),
        ).fetchone()
    return int(row["totale"] or 0), int(row["verificabili"] or 0)


def list_actions(telegram_id: int, limit: int = 20) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, description, how_verifiable, layer, created_at FROM actions WHERE telegram_id = ? ORDER BY id DESC LIMIT ?",
            (telegram_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def start_sanctuary(telegram_id: int) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO sanctuary_visits (telegram_id, completed, started_at) VALUES (?, 0, ?)",
            (telegram_id, _now()),
        )
        return int(cur.lastrowid)


def complete_sanctuary(visit_id: int, duration: float | None = None,
                       slow: bool | None = None) -> None:
    with connect() as conn:
        conn.execute(
            """UPDATE sanctuary_visits
                  SET completed = 1, completed_at = ?, duration_seconds = ?, slow = ?
                WHERE id = ?""",
            (_now(), duration, None if slow is None else int(slow), visit_id),
        )


def add_veil(telegram_id: int, veil_id: int, note: str | None) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO veil_dissolutions (telegram_id, veil_id, note, created_at) VALUES (?, ?, ?, ?)",
            (telegram_id, veil_id, (note or "").strip() or None, _now()),
        )
        return int(cur.lastrowid)


def add_labeled(telegram_id: int, statement: str, suggested_layer: str) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO labeled_statements (telegram_id, statement, suggested_layer, created_at) VALUES (?, ?, ?, ?)",
            (telegram_id, statement.strip(), suggested_layer, _now()),
        )
        return int(cur.lastrowid)


def add_epistemic(telegram_id: int, layer: str, text: str, source: str, how_falls: str | None = None) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO epistemic_records (telegram_id, layer, text, how_falls, source, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (telegram_id, layer, text.strip(), (how_falls or "").strip() or None, source, _now()),
        )
        return int(cur.lastrowid)


def list_epistemic(telegram_id: int, limit: int = 20) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, layer, text, how_falls, source, created_at FROM epistemic_records WHERE telegram_id = ? ORDER BY id DESC LIMIT ?",
            (telegram_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def set_possibility_how_falls(telegram_id: int, possibility_id: int, how_falls: str) -> bool:
    note = how_falls.strip()
    if not note:
        return False
    with connect() as conn:
        cur = conn.execute(
            "UPDATE open_possibilities SET how_falls = ? WHERE id = ? AND telegram_id = ?",
            (note, possibility_id, telegram_id),
        )
        if not cur.rowcount:
            return False
        conn.execute(
            """
            UPDATE epistemic_records
            SET how_falls = ?
            WHERE id = (
                SELECT id FROM epistemic_records
                WHERE telegram_id = ? AND source = 'tieni_aperto'
                ORDER BY id DESC LIMIT 1
            )
            """,
            (note, telegram_id),
        )
        return True


def user_counts(telegram_id: int) -> dict[str, int]:
    with connect() as conn:
        poss = conn.execute(
            "SELECT COUNT(*) AS n FROM open_possibilities WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()["n"]
        acts = conn.execute(
            "SELECT COUNT(*) AS n FROM actions WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()["n"]
        visits = conn.execute(
            "SELECT COUNT(*) AS n FROM sanctuary_visits WHERE telegram_id = ? AND completed = 1",
            (telegram_id,),
        ).fetchone()["n"]
        recs = conn.execute(
            "SELECT COUNT(*) AS n FROM epistemic_records WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()["n"]
    return {
        "possibilities": int(poss),
        "actions": int(acts),
        "sanctuary_completed": int(visits),
        "epistemic": int(recs),
    }


async def ensure_user(telegram_id: int, username: str | None, first_name: str | None) -> None:
    upsert_user(telegram_id, username, first_name)


async def log_sanctuary_visit(telegram_id: int, completed: bool = False,
                              duration: float | None = None,
                              slow: bool | None = None) -> int:
    if completed:
        with connect() as conn:
            row = conn.execute(
                "SELECT id FROM sanctuary_visits WHERE telegram_id = ? AND completed = 0 ORDER BY id DESC LIMIT 1",
                (telegram_id,),
            ).fetchone()
            if row:
                complete_sanctuary(int(row["id"]), duration, slow)
                return int(row["id"])
        visit_id = start_sanctuary(telegram_id)
        complete_sanctuary(visit_id, duration, slow)
        return visit_id
    return start_sanctuary(telegram_id)

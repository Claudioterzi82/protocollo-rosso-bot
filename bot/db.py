"""
Persistenza semplice con aiosqlite.
Tutto ciò che viene salvato è etichettato o è un'azione verificabile.
"""

import aiosqlite
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent.parent / "protocollo.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS open_possibilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT NOT NULL,
                label TEXT DEFAULT 'IPOTESI',
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                description TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sanctuary_visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                completed INTEGER DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.commit()


async def ensure_user(user_id: int, username: str | None, first_name: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (user_id, username, first_name, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, username, first_name, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()


async def add_possibility(user_id: int, text: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO open_possibilities (user_id, text, label, created_at)
            VALUES (?, ?, 'IPOTESI', ?)
            """,
            (user_id, text.strip(), datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def list_possibilities(user_id: int) -> list[tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, text, label, created_at
            FROM open_possibilities
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (user_id,),
        )
        return await cursor.fetchall()


async def add_action(user_id: int, description: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO actions (user_id, description, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, description.strip(), datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()
        return cursor.lastrowid


async def log_sanctuary_visit(user_id: int, completed: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO sanctuary_visits (user_id, completed, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, 1 if completed else 0, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()

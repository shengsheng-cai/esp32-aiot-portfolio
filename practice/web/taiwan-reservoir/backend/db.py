import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "reservoir.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservoir_snapshots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                scraped_at  TEXT NOT NULL,
                name        TEXT NOT NULL,
                percent     REAL,
                volume      TEXT,
                status      TEXT,
                update_time TEXT
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_scraped_at ON reservoir_snapshots(scraped_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_name ON reservoir_snapshots(name)"
        )


def insert_snapshots(records: list[dict], scraped_at: datetime):
    ts = scraped_at.isoformat()
    with get_conn() as conn:
        conn.executemany(
            """
            INSERT INTO reservoir_snapshots (scraped_at, name, percent, volume, status, update_time)
            VALUES (:scraped_at, :name, :percent, :volume, :status, :update_time)
            """,
            [{**r, "scraped_at": ts} for r in records],
        )


def get_latest() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM reservoir_snapshots
            WHERE scraped_at = (SELECT scraped_at FROM reservoir_snapshots ORDER BY id DESC LIMIT 1)
            ORDER BY percent DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def get_history(name: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT scraped_at, percent, status FROM reservoir_snapshots WHERE name = ? ORDER BY scraped_at",
            (name,),
        ).fetchall()
        return [dict(r) for r in rows]

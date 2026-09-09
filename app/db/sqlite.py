import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/leads.db"))


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


_db_initialized = False


def init_db() -> None:
    global _db_initialized
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                website TEXT DEFAULT '',
                email TEXT DEFAULT '',
                lat REAL,
                lon REAL,
                query TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_leads_name ON leads(name)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_leads_query ON leads(query)"
        )

        # Automatic non-destructive migration for existing databases
        existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(leads)").fetchall()}
        if "lat" not in existing_cols:
            conn.execute("ALTER TABLE leads ADD COLUMN lat REAL")
        if "lon" not in existing_cols:
            conn.execute("ALTER TABLE leads ADD COLUMN lon REAL")

    _db_initialized = True


def insert_lead(
    *,
    uuid: str,
    name: str,
    address: str = "",
    phone: str = "",
    website: str = "",
    email: str = "",
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    query: str = "",
    created_at: Optional[str] = None,
) -> Dict[str, Any]:
    global _db_initialized
    if not _db_initialized:
        init_db()

    ts = created_at or datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO leads (uuid, name, address, phone, website, email, lat, lon, query, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (uuid, name.strip(), address, phone, website, email, lat, lon, query, ts),
        )
    return {
        "uuid": uuid,
        "name": name.strip(),
        "address": address,
        "phone": phone,
        "website": website,
        "email": email,
        "lat": lat,
        "lon": lon,
        "query": query,
        "created_at": ts,
    }


def get_all_leads() -> List[Dict[str, Any]]:
    global _db_initialized
    if not _db_initialized:
        init_db()

    with _connect() as conn:
        rows = conn.execute(
            "SELECT uuid, name, address, phone, website, email, lat, lon, query, created_at "
            "FROM leads ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def count_leads() -> int:
    global _db_initialized
    if not _db_initialized:
        init_db()

    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()
    return int(row["c"]) if row else 0

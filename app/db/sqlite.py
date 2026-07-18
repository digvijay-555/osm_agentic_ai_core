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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
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


def insert_lead(
    *,
    uuid: str,
    name: str,
    address: str = "",
    phone: str = "",
    website: str = "",
    email: str = "",
    query: str = "",
    created_at: Optional[str] = None,
) -> Dict[str, Any]:
    init_db()
    ts = created_at or datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO leads (uuid, name, address, phone, website, email, query, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (uuid, name.strip(), address, phone, website, email, query, ts),
        )
    return {
        "uuid": uuid,
        "name": name.strip(),
        "address": address,
        "phone": phone,
        "website": website,
        "email": email,
        "query": query,
        "created_at": ts,
    }


def get_all_leads() -> List[Dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT uuid, name, address, phone, website, email, query, created_at "
            "FROM leads ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def count_leads() -> int:
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()
    return int(row["c"]) if row else 0

"""
Simple persistent store for prediction/logistics results.
Stores records by UUID in a SQLite database so clients can retrieve results
without re-running predictions. This replaces the previous in-memory store
with a lightweight file-backed persistence suitable for local development.

Notes:
- TTL is enforced on retrieval; expired rows are removed when fetched.
- For production, consider Redis or a more robust DB with TTL support.
"""

from typing import Optional, Dict, Any
from uuid import uuid4
import time
import json
import sqlite3
import os
from threading import Lock

from app.config import settings

# Default TTL (seconds) for stored predictions - 24 hours
DEFAULT_TTL = 24 * 60 * 60

# DB file path from settings
_DB_PATH = settings.prediction_db_path

# Ensure data directory exists
db_dir = os.path.dirname(_DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

# Threading lock for sqlite connection safety
_LOCK = Lock()


def _get_conn():
    # Use a short-lived connection per operation to keep things simple and
    # avoid cross-thread connection sharing issues.
    return sqlite3.connect(_DB_PATH, timeout=5)


def _init_db() -> None:
    with _LOCK:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    job_id TEXT PRIMARY KEY,
                    created_at REAL NOT NULL,
                    ttl INTEGER,
                    payload_json TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


_init_db()


def save_result(payload: Dict[str, Any], ttl: int = DEFAULT_TTL) -> str:
    """Save a payload (arbitrary JSON-serializable dict) and return a job id.

    Args:
        payload: Arbitrary JSON-serializable dict to store
        ttl: Time-to-live in seconds

    Returns:
        job_id (str)
    """
    job_id = str(uuid4())
    created_at = time.time()
    payload_json = json.dumps(payload, default=str)

    with _LOCK:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO predictions (job_id, created_at, ttl, payload_json) VALUES (?, ?, ?, ?)",
                (job_id, created_at, ttl, payload_json),
            )
            conn.commit()
        finally:
            conn.close()

    return job_id


def get_result(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a stored payload by job id.

    Returns None if not found or expired.
    """
    with _LOCK:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT created_at, ttl, payload_json FROM predictions WHERE job_id = ?", (job_id,))
            row = cur.fetchone()
            if not row:
                return None

            created_at, ttl, payload_json = row

            # Check TTL
            if ttl is not None and (time.time() - created_at) > ttl:
                # expired - delete and return None
                try:
                    cur.execute("DELETE FROM predictions WHERE job_id = ?", (job_id,))
                    conn.commit()
                except Exception:
                    pass
                return None

            try:
                payload = json.loads(payload_json)
            except Exception:
                # If deserialization fails, return raw string wrapped
                payload = {"raw": payload_json}

            return payload
        finally:
            conn.close()


def clear_store() -> None:
    """Clear persisted predictions. Useful for tests."""
    with _LOCK:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM predictions")
            conn.commit()
        finally:
            conn.close()

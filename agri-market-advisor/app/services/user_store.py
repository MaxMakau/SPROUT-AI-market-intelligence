"""
Simple user store using SQLite for scaffold signup/signin.

This is intentionally lightweight for the scaffold: passwords are
hashed with a per-user salt using SHA-256. For production use a
stronger KDF (bcrypt, argon2) and proper security practices.
"""
from typing import Optional, Dict, Any
from uuid import uuid4
import sqlite3
import os
import time
import hashlib
import binascii
from threading import Lock

from app.config import settings


_DB_PATH = settings.user_db_path

# Ensure data directory exists
db_dir = os.path.dirname(_DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

_LOCK = Lock()


def _get_conn():
    return sqlite3.connect(_DB_PATH, timeout=5)


def _init_db() -> None:
    with _LOCK:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    county TEXT,
                    subcounty TEXT,
                    produce TEXT,
                    quantity REAL,
                    password_salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at REAL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()


_init_db()


def _hash_password(password: str, salt: Optional[bytes] = None) -> (str, str):
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return binascii.hexlify(salt).decode('ascii'), binascii.hexlify(dk).decode('ascii')


def create_user(name: str, phone: str, county: str, subcounty: Optional[str], produce: str, quantity: float, password: str) -> str:
    user_id = str(uuid4())
    created_at = time.time()
    salt, password_hash = _hash_password(password)

    with _LOCK:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (id, name, phone, county, subcounty, produce, quantity, password_salt, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, name, phone, county, subcounty, produce, quantity, salt, password_hash, created_at),
            )
            conn.commit()
        finally:
            conn.close()

    return user_id


def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    with _LOCK:
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, phone, county, subcounty, produce, quantity, password_salt, password_hash, created_at FROM users WHERE phone = ?", (phone,))
            row = cur.fetchone()
            if not row:
                return None
            keys = ["id", "name", "phone", "county", "subcounty", "produce", "quantity", "password_salt", "password_hash", "created_at"]
            return dict(zip(keys, row))
        finally:
            conn.close()


def verify_password(phone: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user_by_phone(phone)
    if not user:
        return None
    salt_hex = user.get('password_salt')
    stored_hash = user.get('password_hash')
    try:
        salt = binascii.unhexlify(salt_hex)
    except Exception:
        return None
    _, computed_hash = _hash_password(password, salt=salt)
    if computed_hash == stored_hash:
        # remove sensitive fields before returning
        user_safe = user.copy()
        user_safe.pop('password_salt', None)
        user_safe.pop('password_hash', None)
        return user_safe
    return None

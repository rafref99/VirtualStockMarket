from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from config import APP_SETTINGS_FILE, DATA_DIR, MARKET_FILE, STARTING_CURRENCY, USERS_FILE
from market import generate_market

def ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not USERS_FILE.exists():
        save_json(USERS_FILE, {"users": {}})
    if not MARKET_FILE.exists():
        save_json(MARKET_FILE, {"last_tick": time.time(), "assets": generate_market()})
    if not APP_SETTINGS_FILE.exists():
        save_json(APP_SETTINGS_FILE, {"remembered_username": ""})


def load_json(path: Path, fallback: dict) -> dict:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120_000)
    return salt, digest.hex()


def create_user_record(username: str, password: str) -> dict:
    salt, digest = hash_password(password)
    return {
        "password_salt": salt,
        "password_hash": digest,
        "cash": STARTING_CURRENCY,
        "portfolio": {},
        "transactions": [],
        "settings": {"language": "English", "dark_mode": False},
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def verify_password(password: str, record: dict) -> bool:
    salt = record.get("password_salt", "")
    expected = record.get("password_hash", "")
    if not salt or not expected:
        return False
    _, actual = hash_password(password, salt)
    return hmac.compare_digest(actual, expected)


@dataclass
class Session:
    username: str
    users_data: dict
    market_data: dict

    @property
    def user(self) -> dict:
        return self.users_data["users"][self.username]

    def save(self) -> None:
        save_json(USERS_FILE, self.users_data)
        save_json(MARKET_FILE, self.market_data)

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from config import APP_SETTINGS_FILE, DATA_DIR, MARKET_FILE, STARTING_CURRENCY, USERS_FILE
from market import generate_market, normalize_asset_prices, seed_news


def normalize_user_record(record: dict) -> dict:
    record.setdefault("cash", STARTING_CURRENCY)
    record.setdefault("portfolio", {})
    record.setdefault("transactions", [])
    record.setdefault("orders", [])
    record.setdefault("loans", [])
    record.setdefault("credit_score", 650)
    record.setdefault("margin_debt", 0.0)
    record.setdefault("short_positions", {})
    record.setdefault("insurance_policies", [])
    record.setdefault("liquidations", [])
    record.setdefault("achievements", {})
    record.setdefault("read_news", [])
    record.setdefault("news_read_count", 0)
    record.setdefault("net_worth_history", [])
    record.setdefault("created_at", time.strftime("%Y-%m-%d %H:%M:%S"))
    record.setdefault("last_closed_at", "")
    record.setdefault("last_closed_at_ts", 0.0)
    record.setdefault("last_login_at", "")
    record.setdefault("last_login_at_ts", 0.0)
    record.setdefault("last_offline_summary", {})
    settings = record.setdefault("settings", {})
    settings.setdefault("language", "English")
    settings.setdefault("dark_mode", False)
    settings.setdefault("sound_effects_enabled", True)
    settings.setdefault("tutorial_seen", False)
    settings.setdefault("trading_mode", "sandbox")
    settings.setdefault("live_interval_seconds", 3.0)
    return record


def normalize_users_data(data: dict) -> dict:
    users = data.setdefault("users", {})
    if not isinstance(users, dict):
        data["users"] = {}
        return data
    for record in users.values():
        if isinstance(record, dict):
            normalize_user_record(record)
    return data


def normalize_market_data(data: dict) -> dict:
    if not isinstance(data.get("assets"), list) or not data["assets"]:
        data["assets"] = generate_market()
    data.setdefault("last_tick", time.time())
    settings = data.setdefault("settings", {})
    settings.setdefault("volatility_multiplier", 1.0)
    settings.setdefault("event_frequency", 1.0)
    data.setdefault("news_feed", [])
    normalize_asset_prices(data)
    seed_news(data)
    return data


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
    return normalize_user_record({
        "password_salt": salt,
        "password_hash": digest,
        "cash": STARTING_CURRENCY,
        "portfolio": {},
        "transactions": [],
        "orders": [],
        "loans": [],
        "credit_score": 650,
        "margin_debt": 0.0,
        "short_positions": {},
        "insurance_policies": [],
        "liquidations": [],
        "achievements": {},
        "read_news": [],
        "news_read_count": 0,
        "net_worth_history": [],
        "settings": {
            "language": "English",
            "dark_mode": False,
            "sound_effects_enabled": True,
            "trading_mode": "sandbox",
            "live_interval_seconds": 3.0,
        },
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "last_closed_at": "",
        "last_closed_at_ts": 0.0,
        "last_login_at": "",
        "last_login_at_ts": 0.0,
        "last_offline_summary": {},
    })


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

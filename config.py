from __future__ import annotations

from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"
MARKET_FILE = DATA_DIR / "market.json"
APP_SETTINGS_FILE = DATA_DIR / "app_settings.json"
STARTING_CURRENCY = 100.0
CHART_RANGES = {
    "Hours": 20,
    "Days": 80,
    "Week": 180,
    "Years": 500,
    "Max": None,
}


def money(value: float) -> str:
    return f"{value:,.2f} FC"

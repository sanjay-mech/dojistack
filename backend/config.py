"""Configuration loaded from .env for DojiStack backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

LIVE_MODE: bool = os.getenv("LIVE_MODE", "false").strip().lower() in ("1", "true", "yes")
ANGEL_API_KEY: str = os.getenv("ANGEL_API_KEY", "").strip()
ANGEL_CLIENT_ID: str = (
    os.getenv("ANGEL_CLIENT_ID", "") or os.getenv("ANGEL_CLIENT_CODE", "")
).strip()
ANGEL_PIN: str = (
    os.getenv("ANGEL_PIN", "") or os.getenv("ANGEL_PASSWORD", "")
).strip()
ANGEL_TOTP_SECRET: str = os.getenv("ANGEL_TOTP_SECRET", "").strip()

DB_PATH: Path = Path(
    os.getenv("DOJISTACK_DB_PATH", str(Path(__file__).resolve().parent / "dojistack.db"))
)

MIN_DAILY_VOLUME: int = int(os.getenv("MIN_DAILY_VOLUME", "0") or 0)
MIN_PRICE: float = float(os.getenv("MIN_PRICE", "0") or 0)
SCAN_MAX_SYMBOLS: int = int(os.getenv("SCAN_MAX_SYMBOLS", "0") or 0)


def angel_credentials_ready() -> bool:
    return bool(ANGEL_API_KEY and ANGEL_CLIENT_ID and ANGEL_PIN and ANGEL_TOTP_SECRET)

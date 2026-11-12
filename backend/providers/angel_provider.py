"""Angel One SmartAPI live-mode provider (TOTP auth, ScripMaster, rate-limited candles)."""

import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import pyotp
import requests
from SmartApi import SmartConnect

from backend.config import (
    ANGEL_API_KEY,
    ANGEL_CLIENT_ID,
    ANGEL_PIN,
    ANGEL_TOTP_SECRET,
    LIVE_MODE,
    angel_credentials_ready,
)
from backend.doji import is_market_open, resample_15m_to_75m, resample_daily_to_weekly

IST = ZoneInfo("Asia/Kolkata")
SCRIP_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
SCRIP_CACHE_PATH = Path(__file__).resolve().parent.parent / "scrip_master_cache.json"


class RateLimiter:
    """Thread-safe ~3 requests/sec rate limiter."""

    def __init__(self, min_interval: float = 0.36) -> None:
        self._min_interval = min_interval
        self._lock = threading.Lock()
        self._last = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last = time.monotonic()


class AngelClient:
    def __init__(self) -> None:
        self._smart: Optional[SmartConnect] = None
        self._session_ts: float = 0.0
        self._limiter = RateLimiter(0.36)
        self._scrip_index: Optional[Dict[str, Any]] = None

    def is_active(self) -> bool:
        return LIVE_MODE and angel_credentials_ready() and is_market_open()

    def ensure_session(self) -> Optional[SmartConnect]:
        if not angel_credentials_ready():
            return None
        # Refresh session every 6 hours
        if self._smart is not None and (time.time() - self._session_ts) < 21600:
            return self._smart

        smart = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        data = smart.generateSession(ANGEL_CLIENT_ID, ANGEL_PIN, totp)
        if not data or not data.get("status"):
            return None
        self._smart = smart
        self._session_ts = time.time()
        return self._smart

    def _load_scrip_master(self) -> Dict[str, Any]:
        if self._scrip_index is not None:
            return self._scrip_index

        raw_list: List[Dict[str, Any]] = []
        if SCRIP_CACHE_PATH.exists() and (time.time() - SCRIP_CACHE_PATH.stat().st_mtime) < 43200:
            try:
                raw_list = json.loads(SCRIP_CACHE_PATH.read_text(encoding="utf-8"))
            except Exception:
                raw_list = []

        if not raw_list:
            resp = requests.get(SCRIP_MASTER_URL, timeout=25)
            resp.raise_for_status()
            raw_list = resp.json()
            SCRIP_CACHE_PATH.write_text(json.dumps(raw_list), encoding="utf-8")

        equities: Dict[str, Dict[str, str]] = {}
        options: Dict[tuple, Dict[str, str]] = {}
        for item in raw_list:
            exch = item.get("exch_seg")
            if exch == "NSE" and str(item.get("symbol", "")).endswith("-EQ"):
                sym = item["symbol"][:-3]
                equities[sym] = {
                    "token": str(item["token"]),
                    "tradingsymbol": item["symbol"],
                }
            elif exch == "NFO" and item.get("instrumenttype") == "OPTSTK":
                name = str(item.get("name", "")).strip()
                exp_raw = str(item.get("expiry", "")).strip()
                tsym = str(item.get("symbol", ""))
                opt_type = "CE" if tsym.endswith("CE") else ("PE" if tsym.endswith("PE") else "")
                if not opt_type:
                    continue
                try:
                    # Angel expiry format is like 26NOV2026
                    exp_dt = datetime.strptime(exp_raw, "%d%b%Y").date().isoformat()
                    # Angel strike is multiplied by 100
                    strike = round(float(item.get("strike", 0)) / 100.0, 2)
                except Exception:
                    continue
                options[(name, exp_dt, strike, opt_type)] = {
                    "token": str(item["token"]),
                    "tradingsymbol": tsym,
                }

        self._scrip_index = {"equities": equities, "options": options}
        return self._scrip_index

    def get_equity_token(self, symbol: str) -> Optional[Dict[str, str]]:
        idx = self._load_scrip_master()
        return idx["equities"].get(symbol)

    def get_option_token(
        self, symbol: str, expiry: str, strike: float, opt_type: str
    ) -> Optional[Dict[str, str]]:
        idx = self._load_scrip_master()
        return idx["options"].get((symbol, expiry, round(strike, 2), opt_type.upper()))

    def get_candles(
        self,
        exchange: str,
        token: str,
        tf: str,
    ) -> List[Dict[str, Any]]:
        smart = self.ensure_session()
        if smart is None:
            return []

        now = datetime.now(IST)
        if tf == "75m":
            interval = "FIFTEEN_MINUTE"
            from_dt = now - timedelta(days=45)
        else:
            interval = "ONE_DAY"
            from_dt = now - timedelta(days=200)

        params = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_dt.strftime("%Y-%m-%d 09:15"),
            "todate": now.strftime("%Y-%m-%d %H:%M"),
        }

        for attempt in range(3):
            self._limiter.wait()
            try:
                resp = smart.getCandleData(params)
                if resp and resp.get("status") and resp.get("data"):
                    candles = [
                        {
                            "time": row[0][:16].replace("T", " ") if tf == "75m" else row[0][:10],
                            "open": float(row[1]),
                            "high": float(row[2]),
                            "low": float(row[3]),
                            "close": float(row[4]),
                            "volume": float(row[5]),
                        }
                        for row in resp["data"]
                    ]
                    if tf == "75m":
                        return resample_15m_to_75m(candles)
                    if tf == "1W":
                        return resample_daily_to_weekly(candles)
                    return candles
            except Exception:
                time.sleep(0.7 * (attempt + 1))
        return []


angel_client = AngelClient()

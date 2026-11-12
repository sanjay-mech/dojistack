"""NSE F&O UDiFF Bhavcopy downloader and ATM CE/PE option OHLC builder."""

import io
import time
import zipfile
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from backend.database import load_option_history, save_bhavcopy_rows, set_meta
from backend.doji import resample_daily_to_weekly
from backend.universe import BY_SYMBOL

IST = ZoneInfo("Asia/Kolkata")

NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


def _create_nse_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(NSE_HEADERS)
    try:
        session.get("https://www.nseindia.com", timeout=8)
    except Exception:
        pass
    return session


def download_udiff_bhavcopy(
    trade_date: date,
    session: Optional[requests.Session] = None,
    retries: int = 2,
) -> int:
    """
    Download and ingest NSE F&O UDiFF Bhavcopy for a given date.
    Returns number of option rows saved, or 0 if unavailable/holiday.
    """
    if trade_date.weekday() >= 5:
        return 0

    sess = session or _create_nse_session()
    ymd = trade_date.strftime("%Y%m%d")
    url = f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"

    resp_bytes: Optional[bytes] = None
    for attempt in range(retries + 1):
        try:
            r = sess.get(url, timeout=15)
            if r.status_code == 200 and r.content[:2] == b"PK":
                resp_bytes = r.content
                break
            if r.status_code == 404:
                return 0
        except Exception:
            pass
        if attempt < retries:
            time.sleep(0.8 * (attempt + 1))

    if not resp_bytes:
        return 0

    try:
        with zipfile.ZipFile(io.BytesIO(resp_bytes)) as zf:
            csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not csv_names:
                return 0
            with zf.open(csv_names[0]) as f:
                df = pd.read_csv(f, low_memory=False)
    except Exception:
        return 0

    # Filter to stock options (OPTSTK) in our F&O universe
    if "FinInstrmTp" in df.columns:
        df = df[df["FinInstrmTp"].isin(["STO", "OPTSTK"])]
    elif "INSTRUMENT" in df.columns:
        df = df[df["INSTRUMENT"] == "OPTSTK"]

    if df.empty or "TckrSymb" not in df.columns:
        return 0

    universe_syms = set(BY_SYMBOL.keys())
    df = df[df["TckrSymb"].isin(universe_syms)]
    if df.empty:
        return 0

    rows: List[Dict[str, Any]] = []
    td_str = trade_date.isoformat()
    for _, r in df.iterrows():
        opt_tp = str(r.get("OptnTp", "")).strip().upper()
        if opt_tp not in ("CE", "PE"):
            continue
        try:
            exp_raw = str(r.get("XpryDt", "")).strip()[:10]
            strike = float(r.get("StrkPric", 0))
            o = float(r.get("OpnPric", 0) or 0)
            h = float(r.get("HghPric", 0) or 0)
            l = float(r.get("LwPric", 0) or 0)
            c = float(r.get("ClsPric", 0) or 0)
            vol = float(r.get("TtlTradgVol", 0) or 0)
            oi = float(r.get("OpnIntrst", 0) or 0)
            if c <= 0 and h <= 0:
                continue
            rows.append(
                {
                    "trade_date": str(r.get("TradDt", td_str))[:10],
                    "symbol": str(r["TckrSymb"]).strip(),
                    "expiry": exp_raw,
                    "strike": strike,
                    "opt_type": opt_tp,
                    "open": o if o > 0 else c,
                    "high": h if h > 0 else c,
                    "low": l if l > 0 else c,
                    "close": c,
                    "volume": vol,
                    "oi": oi,
                }
            )
        except (ValueError, TypeError):
            continue

    saved = save_bhavcopy_rows(rows)
    if saved > 0:
        set_meta("bhavcopy_last_date", td_str)
    return saved


def ingest_recent_bhavcopies(days_back: int = 15) -> int:
    """Attempt to download recent trading days' Bhavcopies into SQLite."""
    sess = _create_nse_session()
    today = datetime.now(IST).date()
    total = 0
    for d in range(days_back):
        dt = today - timedelta(days=d)
        if dt.weekday() >= 5:
            continue
        total += download_udiff_bhavcopy(dt, session=sess, retries=1)
    return total


def get_bhavcopy_option_candles(
    symbol: str,
    expiry: str,
    strike: float,
    opt_type: str,
    tf: str = "1D",
) -> List[Dict[str, Any]]:
    """Load option candles from SQLite bhavcopy store for 1D or 1W."""
    daily = load_option_history(symbol=symbol, expiry=expiry, strike=strike, opt_type=opt_type)
    if not daily:
        return []
    if tf == "1W":
        return resample_daily_to_weekly(daily)
    return daily

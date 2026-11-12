"""Core DojiStack screener orchestration, SQLite caching, and confluence calculation."""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from backend.config import SCAN_MAX_SYMBOLS
from backend.database import load_candles, save_candles, set_meta
from backend.doji import detect_doji_streak, is_market_open
from backend.providers.angel_provider import angel_client
from backend.providers.bhavcopy_provider import get_bhavcopy_option_candles
from backend.providers.yahoo_provider import fetch_yahoo_spot_batch
from backend.universe import (
    BY_SYMBOL,
    FNO_UNIVERSE,
    FnoStock,
    get_nearest_monthly_expiry,
    nearest_atm_strike,
)

IST = ZoneInfo("Asia/Kolkata")
CACHE_TTL_SEC = 300  # 5 minutes


def _active_universe() -> List[FnoStock]:
    if SCAN_MAX_SYMBOLS > 0:
        return FNO_UNIVERSE[:SCAN_MAX_SYMBOLS]
    return FNO_UNIVERSE


def refresh_timeframe_cache(tf: str = "1D", force: bool = False) -> str:
    """
    Ensure spot (and available option) candles for `tf` are cached in SQLite.
    Returns data source label ("Angel One · Live" or "Yahoo + Bhavcopy").
    """
    stocks = _active_universe()
    expiry = get_nearest_monthly_expiry()

    # Check if cache is already fresh
    if not force and stocks:
        sample = load_candles(stocks[0].symbol, "stock", tf, max_age_sec=CACHE_TTL_SEC)
        if sample is not None:
            return "Angel One · Live" if angel_client.is_active() else "Yahoo + Bhavcopy"

    use_angel = angel_client.is_active()
    source_label = "Angel One · Live" if use_angel else "Yahoo + Bhavcopy"

    spot_map: Dict[str, List[Dict[str, Any]]] = {}
    if use_angel:
        for s in stocks:
            eq = angel_client.get_equity_token(s.symbol)
            if eq:
                candles = angel_client.get_candles("NSE", eq["token"], tf)
                if candles:
                    spot_map[s.symbol] = candles
        if not spot_map:
            use_angel = False
            source_label = "Yahoo + Bhavcopy"

    if not spot_map:
        spot_map = fetch_yahoo_spot_batch(stocks, tf=tf)

    for s in stocks:
        candles = spot_map.get(s.symbol, [])
        if not candles:
            continue
        ltp = float(candles[-1]["close"])
        strike = nearest_atm_strike(ltp, s.strike_step)
        save_candles(s.symbol, "stock", tf, candles, strike=strike, expiry=expiry)

        # Fetch/load ATM CE & PE candles
        for opt_type in ("CE", "PE"):
            kind = opt_type.lower()
            opt_candles: List[Dict[str, Any]] = []
            if use_angel:
                opt_meta = angel_client.get_option_token(s.symbol, expiry, strike, opt_type)
                if opt_meta:
                    opt_candles = angel_client.get_candles("NFO", opt_meta["token"], tf)
            if not opt_candles and tf in ("1D", "1W"):
                opt_candles = get_bhavcopy_option_candles(
                    symbol=s.symbol,
                    expiry=expiry,
                    strike=strike,
                    opt_type=opt_type,
                    tf=tf,
                )
            if opt_candles:
                save_candles(s.symbol, kind, tf, opt_candles, strike=strike, expiry=expiry)

    now_iso = datetime.now(IST).strftime("%d %b %Y · %H:%M IST")
    set_meta("last_updated", now_iso)
    set_meta("data_source", source_label)
    set_meta("nearest_expiry", expiry)
    return source_label


def run_screen(
    tf: str = "1D",
    src: str = "stock",
    min_doji: int = 2,
    body_pct: float = 10.0,
    sector: str = "all",
    q: str = "",
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """Run the DojiStack screen and return rows, summary counts, and metadata."""
    tf_norm = tf if tf in ("75m", "1D", "1W") else "1D"
    src_norm = src.lower() if src.lower() in ("stock", "ce", "pe") else "stock"

    source_label = refresh_timeframe_cache(tf=tf_norm, force=force_refresh)
    stocks = _active_universe()
    expiry = get_nearest_monthly_expiry()

    sector_norm = (sector or "all").strip().lower()
    tokens = [t.strip().upper() for t in (q or "").split(",") if t.strip()]

    double_count = 0
    triple_count = 0
    four_plus_count = 0
    rows: List[Dict[str, Any]] = []
    latest_bar_time = ""

    for s in stocks:
        if sector_norm != "all" and s.sector_slug != sector_norm and s.sector.lower() != sector_norm:
            continue
        if tokens and not any(tok in s.symbol or tok in s.name.upper() for tok in tokens):
            continue

        stk_entry = load_candles(s.symbol, "stock", tf_norm)
        if not stk_entry or not stk_entry["candles"]:
            continue

        stk_res = detect_doji_streak(stk_entry["candles"], body_pct=body_pct, tf=tf_norm)
        strike = stk_entry["strike"] or nearest_atm_strike(stk_res["last_close"], s.strike_step)

        ce_entry = load_candles(s.symbol, "ce", tf_norm)
        pe_entry = load_candles(s.symbol, "pe", tf_norm)

        ce_res = (
            detect_doji_streak(ce_entry["candles"], body_pct=body_pct, tf=tf_norm)
            if ce_entry and ce_entry["candles"]
            else None
        )
        pe_res = (
            detect_doji_streak(pe_entry["candles"], body_pct=body_pct, tf=tf_norm)
            if pe_entry and pe_entry["candles"]
            else None
        )

        active_res = (
            ce_res if src_norm == "ce" else (pe_res if src_norm == "pe" else stk_res)
        )
        if active_res is None:
            continue

        if stk_res["last_time"] > latest_bar_time:
            latest_bar_time = stk_res["last_time"]

        streak = active_res["streak"]
        if streak == 2:
            double_count += 1
        elif streak == 3:
            triple_count += 1
        elif streak >= 4:
            four_plus_count += 1

        if streak < min_doji:
            continue

        rows.append(
            {
                "symbol": s.symbol,
                "name": s.name,
                "sector": s.sector,
                "sector_slug": s.sector_slug,
                "ltp": stk_res["last_close"],
                "change_pct": stk_res["change_pct"],
                "streak": streak,
                "coil_range_pct": active_res["coil_range_pct"],
                "break_above": active_res["break_above"],
                "break_below": active_res["break_below"],
                "atm_strike": strike,
                "ce_ltp": ce_res["last_close"] if ce_res else None,
                "pe_ltp": pe_res["last_close"] if pe_res else None,
                "stk_streak": stk_res["streak"],
                "ce_streak": ce_res["streak"] if ce_res else 0,
                "pe_streak": pe_res["streak"] if pe_res else 0,
                "last_bar": active_res["last_time"],
            }
        )

    # Default sort: more dojis first, then smaller coil range
    rows.sort(key=lambda r: (-r["streak"], r["coil_range_pct"], r["symbol"]))

    return {
        "rows": rows,
        "summary": {
            "double": double_count,
            "triple": triple_count,
            "four_plus": four_plus_count,
            "matching": len(rows),
        },
        "expiry": expiry,
        "universe_size": len(stocks),
        "tf": tf_norm,
        "src": src_norm,
        "source": source_label,
        "is_live": is_market_open(),
        "last_updated": datetime.now(IST).strftime("%d %b %Y · %H:%M IST"),
        "latest_bar": latest_bar_time,
    }


def get_stock_detail(
    symbol: str,
    tf: str = "1D",
    body_pct: float = 10.0,
) -> Optional[Dict[str, Any]]:
    """Return spot, ATM CE, and ATM PE candle arrays + doji indices + break levels."""
    sym = symbol.strip().upper()
    stock = BY_SYMBOL.get(sym)
    if not stock:
        return None

    tf_norm = tf if tf in ("75m", "1D", "1W") else "1D"
    stk_entry = load_candles(sym, "stock", tf_norm)
    if not stk_entry:
        refresh_timeframe_cache(tf=tf_norm, force=False)
        stk_entry = load_candles(sym, "stock", tf_norm)
    if not stk_entry:
        return None

    stk_res = detect_doji_streak(stk_entry["candles"], body_pct=body_pct, tf=tf_norm)
    strike = stk_entry["strike"] or nearest_atm_strike(stk_res["last_close"], stock.strike_step)
    expiry = stk_entry["expiry"] or get_nearest_monthly_expiry()

    ce_entry = load_candles(sym, "ce", tf_norm)
    pe_entry = load_candles(sym, "pe", tf_norm)

    ce_res = (
        detect_doji_streak(ce_entry["candles"], body_pct=body_pct, tf=tf_norm)
        if ce_entry and ce_entry["candles"]
        else None
    )
    pe_res = (
        detect_doji_streak(pe_entry["candles"], body_pct=body_pct, tf=tf_norm)
        if pe_entry and pe_entry["candles"]
        else None
    )

    def _fmt_panel(res: Optional[Dict[str, Any]], label: str) -> Dict[str, Any]:
        if not res:
            return {
                "label": label,
                "candles": [],
                "doji_indices": [],
                "streak": 0,
                "break_above": None,
                "break_below": None,
                "coil_range_pct": 0.0,
            }
        return {
            "label": label,
            "candles": res["candles"][-80:],
            "doji_indices": [
                i - max(0, len(res["candles"]) - 80)
                for i in res["doji_indices"]
                if i >= max(0, len(res["candles"]) - 80)
            ],
            "streak": res["streak"],
            "break_above": res["break_above"],
            "break_below": res["break_below"],
            "coil_range_pct": res["coil_range_pct"],
        }

    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "sector": stock.sector,
        "tf": tf_norm,
        "strike": strike,
        "expiry": expiry,
        "spot": _fmt_panel(stk_res, f"{stock.symbol} Spot"),
        "ce": _fmt_panel(ce_res, f"{stock.symbol} {int(strike)} CE"),
        "pe": _fmt_panel(pe_res, f"{stock.symbol} {int(strike)} PE"),
    }

"""Doji detection, 75m/1W resampling, coil range, and market-hours completed-bar logic."""

from datetime import datetime, time as dtime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import pandas as pd

IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = dtime(9, 15)
MARKET_CLOSE = dtime(15, 30)


def is_market_open(now: Optional[datetime] = None) -> bool:
    """Return True if NSE is currently in regular trading hours (09:15-15:30 IST, Mon-Fri)."""
    dt = now or datetime.now(IST)
    if dt.weekday() >= 5:
        return False
    t = dt.time()
    return MARKET_OPEN <= t < MARKET_CLOSE


def is_doji_candle(
    open_p: float,
    high_p: float,
    low_p: float,
    close_p: float,
    body_pct: float = 10.0,
) -> bool:
    """Exact Doji rule: abs(close - open) <= (bodyPct/100) * (high - low) and high > low."""
    if high_p <= low_p:
        return False
    return abs(close_p - open_p) <= (body_pct / 100.0) * (high_p - low_p)


def resample_15m_to_75m(candles_15m: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build 75-minute candles from 15-minute bars by grouping 5 bars per session
    starting at 09:15 IST: 09:15, 10:30, 11:45, 13:00, 14:15.
    """
    if not candles_15m:
        return []

    slots = [
        (dtime(9, 15), dtime(10, 30), "09:15"),
        (dtime(10, 30), dtime(11, 45), "10:30"),
        (dtime(11, 45), dtime(13, 0), "11:45"),
        (dtime(13, 0), dtime(14, 15), "13:00"),
        (dtime(14, 15), dtime(15, 35), "14:15"),
    ]

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for c in candles_15m:
        ts_str = str(c["time"])
        try:
            dt = datetime.fromisoformat(ts_str)
        except ValueError:
            continue
        t = dt.time()
        day_str = dt.date().isoformat()
        bucket_label = None
        for start_t, end_t, label in slots:
            if start_t <= t < end_t:
                bucket_label = f"{day_str} {label}"
                break
        if bucket_label is None:
            continue
        grouped.setdefault(bucket_label, []).append(c)

    out: List[Dict[str, Any]] = []
    for key in sorted(grouped.keys()):
        bars = grouped[key]
        out.append(
            {
                "time": key,
                "open": float(bars[0]["open"]),
                "high": max(float(b["high"]) for b in bars),
                "low": min(float(b["low"]) for b in bars),
                "close": float(bars[-1]["close"]),
                "volume": sum(float(b.get("volume", 0) or 0) for b in bars),
            }
        )
    return out


def resample_daily_to_weekly(candles_1d: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build Monday-Friday weekly candles from daily OHLCV data."""
    if not candles_1d:
        return []

    df = pd.DataFrame(candles_1d)
    df["dt"] = pd.to_datetime(df["time"])
    df = df.sort_values("dt").set_index("dt")

    agg = (
        df.resample("W-FRI")
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        .dropna(subset=["open", "high", "low", "close"])
    )

    out: List[Dict[str, Any]] = []
    for idx, row in agg.iterrows():
        out.append(
            {
                "time": idx.strftime("%Y-%m-%d"),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"] or 0),
            }
        )
    return out


def drop_in_progress_bar(
    candles: List[Dict[str, Any]],
    tf: str,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Ignore the in-progress bar during market hours; keep all bars when market is closed.
    """
    if not candles or len(candles) < 2:
        return candles

    dt_now = now or datetime.now(IST)
    if not is_market_open(dt_now):
        return candles

    last_time = str(candles[-1]["time"])
    today_str = dt_now.date().isoformat()
    if tf == "1D" and last_time.startswith(today_str):
        return candles[:-1]
    if tf == "75m" and last_time.startswith(today_str):
        # Check if the 75m slot is still active
        try:
            bar_dt = datetime.fromisoformat(last_time).replace(tzinfo=IST)
            if (dt_now - bar_dt).total_seconds() < 75 * 60:
                return candles[:-1]
        except ValueError:
            pass
    if tf == "1W":
        # Current week bar is in progress during market hours
        try:
            bar_date = datetime.fromisoformat(last_time[:10]).date()
            if bar_date >= dt_now.date():
                return candles[:-1]
        except ValueError:
            pass
    return candles


def detect_doji_streak(
    candles: List[Dict[str, Any]],
    body_pct: float = 10.0,
    tf: str = "1D",
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Evaluate consecutive Doji streak ending at the most recent completed bar.
    Returns:
      streak, doji_indices, break_above, break_below, coil_range_pct,
      last_close, prev_close, change_pct, last_time, candles
    """
    completed = drop_in_progress_bar(candles, tf=tf, now=now)
    if not completed:
        return {
            "streak": 0,
            "doji_indices": [],
            "break_above": 0.0,
            "break_below": 0.0,
            "coil_range_pct": 0.0,
            "last_close": 0.0,
            "prev_close": 0.0,
            "change_pct": 0.0,
            "last_time": "",
            "candles": [],
        }

    flags = [
        is_doji_candle(c["open"], c["high"], c["low"], c["close"], body_pct=body_pct)
        for c in completed
    ]

    streak = 0
    for f in reversed(flags):
        if f:
            streak += 1
        else:
            break

    n = len(completed)
    doji_indices = list(range(n - streak, n)) if streak > 0 else []

    last_bar = completed[-1]
    prev_bar = completed[-2] if n >= 2 else last_bar
    last_close = float(last_bar["close"])
    prev_close = float(prev_bar["close"])
    change_pct = ((last_close - prev_close) / prev_close * 100.0) if prev_close else 0.0

    if streak > 0:
        cluster = completed[-streak:]
        break_above = max(float(b["high"]) for b in cluster)
        break_below = min(float(b["low"]) for b in cluster)
        coil_range_pct = (
            ((break_above - break_below) / last_close) * 100.0 if last_close > 0 else 0.0
        )
    else:
        break_above = float(last_bar["high"])
        break_below = float(last_bar["low"])
        coil_range_pct = 0.0

    return {
        "streak": streak,
        "doji_indices": doji_indices,
        "break_above": round(break_above, 2),
        "break_below": round(break_below, 2),
        "coil_range_pct": round(coil_range_pct, 2),
        "last_close": round(last_close, 2),
        "prev_close": round(prev_close, 2),
        "change_pct": round(change_pct, 2),
        "last_time": str(last_bar["time"]),
        "candles": completed,
    }

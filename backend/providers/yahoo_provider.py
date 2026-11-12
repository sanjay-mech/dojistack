"""Yahoo Finance spot OHLC provider (1D, 1W from 1D, and 75m from 15m)."""

from typing import Any, Dict, List

import pandas as pd
import yfinance as yf

from backend.doji import resample_15m_to_75m, resample_daily_to_weekly
from backend.universe import FNO_UNIVERSE, FnoStock


def _df_to_candles(df: pd.DataFrame, intraday: bool) -> List[Dict[str, Any]]:
    if df is None or df.empty:
        return []
    df = df.dropna(subset=["Open", "High", "Low", "Close"]).copy()
    if df.empty:
        return []

    out: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        ts = pd.Timestamp(idx)
        if intraday:
            if ts.tzinfo is not None:
                ts = ts.tz_convert("Asia/Kolkata")
            time_str = ts.strftime("%Y-%m-%d %H:%M")
        else:
            time_str = ts.strftime("%Y-%m-%d")

        vol = row.get("Volume", 0)
        out.append(
            {
                "time": time_str,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": 0.0 if pd.isna(vol) else float(vol),
            }
        )
    return out


def fetch_yahoo_spot_batch(
    stocks: List[FnoStock] | None = None,
    tf: str = "1D",
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Batch-download spot OHLCV from Yahoo Finance for all stocks.
    - tf == '1D': 6mo daily
    - tf == '1W': 1y daily resampled to Mon-Fri weekly
    - tf == '75m': 60d 15m resampled to 75m (09:15..14:15)
    """
    items = stocks or FNO_UNIVERSE
    if not items:
        return {}

    tickers = [s.yf_symbol for s in items]
    if tf == "75m":
        period, interval, intraday = "60d", "15m", True
    elif tf == "1W":
        period, interval, intraday = "1y", "1d", False
    else:
        period, interval, intraday = "6mo", "1d", False

    result: Dict[str, List[Dict[str, Any]]] = {}
    chunk_size = 55
    for start in range(0, len(items), chunk_size):
        chunk_items = items[start : start + chunk_size]
        chunk_tickers = [s.yf_symbol for s in chunk_items]
        raw = yf.download(
            tickers=chunk_tickers,
            period=period,
            interval=interval,
            group_by="ticker",
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if raw is None or raw.empty:
            continue

        if len(chunk_tickers) == 1:
            s = chunk_items[0]
            sub = (
                raw[s.yf_symbol]
                if isinstance(raw.columns, pd.MultiIndex)
                and s.yf_symbol in raw.columns.get_level_values(0)
                else raw
            )
            candles = _df_to_candles(sub, intraday=intraday)
            if tf == "75m":
                candles = resample_15m_to_75m(candles)
            elif tf == "1W":
                candles = resample_daily_to_weekly(candles)
            if candles:
                result[s.symbol] = candles
            continue

        top_cols = set(raw.columns.get_level_values(0))
        for s in chunk_items:
            if s.yf_symbol not in top_cols:
                continue
            candles = _df_to_candles(raw[s.yf_symbol], intraday=intraday)
            if tf == "75m":
                candles = resample_15m_to_75m(candles)
            elif tf == "1W":
                candles = resample_daily_to_weekly(candles)
            if candles:
                result[s.symbol] = candles
    return result

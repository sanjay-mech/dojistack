"""SQLite persistence and caching for DojiStack."""

import json
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

from backend.config import DB_PATH


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS ohlcv_cache (
                symbol TEXT NOT NULL,
                kind TEXT NOT NULL,
                tf TEXT NOT NULL,
                strike REAL DEFAULT 0,
                expiry TEXT DEFAULT '',
                updated_at REAL NOT NULL,
                candles_json TEXT NOT NULL,
                PRIMARY KEY (symbol, kind, tf)
            );

            CREATE TABLE IF NOT EXISTS bhavcopy_options (
                trade_date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                expiry TEXT NOT NULL,
                strike REAL NOT NULL,
                opt_type TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL DEFAULT 0,
                oi REAL DEFAULT 0,
                PRIMARY KEY (trade_date, symbol, expiry, strike, opt_type)
            );

            CREATE TABLE IF NOT EXISTS meta_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            );
            """
        )


def set_meta(key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO meta_state (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            (key, value, time.time()),
        )


def get_meta(key: str, default: Optional[str] = None) -> Optional[str]:
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM meta_state WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def save_candles(
    symbol: str,
    kind: str,
    tf: str,
    candles: List[Dict[str, Any]],
    strike: float = 0.0,
    expiry: str = "",
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO ohlcv_cache (symbol, kind, tf, strike, expiry, updated_at, candles_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, kind, tf) DO UPDATE SET
                strike=excluded.strike,
                expiry=excluded.expiry,
                updated_at=excluded.updated_at,
                candles_json=excluded.candles_json
            """,
            (symbol, kind, tf, strike, expiry, time.time(), json.dumps(candles)),
        )


def load_candles(
    symbol: str,
    kind: str,
    tf: str,
    max_age_sec: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT strike, expiry, updated_at, candles_json FROM ohlcv_cache WHERE symbol=? AND kind=? AND tf=?",
            (symbol, kind, tf),
        ).fetchone()
        if not row:
            return None
        if max_age_sec is not None and (time.time() - row["updated_at"]) > max_age_sec:
            return None
        return {
            "strike": row["strike"],
            "expiry": row["expiry"],
            "updated_at": row["updated_at"],
            "candles": json.loads(row["candles_json"]),
        }


def save_bhavcopy_rows(rows: List[Dict[str, Any]]) -> int:
    if not rows:
        return 0
    with get_conn() as conn:
        conn.executemany(
            """
            INSERT INTO bhavcopy_options
                (trade_date, symbol, expiry, strike, opt_type, open, high, low, close, volume, oi)
            VALUES (:trade_date, :symbol, :expiry, :strike, :opt_type, :open, :high, :low, :close, :volume, :oi)
            ON CONFLICT(trade_date, symbol, expiry, strike, opt_type) DO UPDATE SET
                open=excluded.open, high=excluded.high, low=excluded.low,
                close=excluded.close, volume=excluded.volume, oi=excluded.oi
            """,
            rows,
        )
    return len(rows)


def load_option_history(
    symbol: str,
    expiry: str,
    strike: float,
    opt_type: str,
) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT trade_date, open, high, low, close, volume, oi
            FROM bhavcopy_options
            WHERE symbol=? AND expiry=? AND ABS(strike - ?) < 0.01 AND opt_type=?
            ORDER BY trade_date ASC
            """,
            (symbol, expiry, strike, opt_type),
        ).fetchall()
        return [
            {
                "time": r["trade_date"],
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r["volume"]),
                "oi": float(r["oi"]),
            }
            for r in rows
        ]

"""Tests for DojiStack backend logic and API endpoints."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from backend.doji import (
    detect_doji_streak,
    is_doji_candle,
    resample_15m_to_75m,
    resample_daily_to_weekly,
)
from backend.main import app
from backend.universe import get_nearest_monthly_expiry, nearest_atm_strike

IST = ZoneInfo("Asia/Kolkata")


def test_doji_rule():
    # abs(100.5 - 100.0) = 0.5 <= 0.10 * (105 - 95) = 1.0 -> True
    assert is_doji_candle(100.0, 105.0, 95.0, 100.5, body_pct=10.0) is True
    # high == low -> False per spec (high > low)
    assert is_doji_candle(100.0, 100.0, 100.0, 100.0, body_pct=10.0) is False
    # Large body -> False
    assert is_doji_candle(100.0, 110.0, 99.0, 109.0, body_pct=10.0) is False


def test_resample_15m_to_75m_five_bars():
    bars_15m = [
        {"time": "2026-11-11 09:15", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 10},
        {"time": "2026-11-11 09:30", "open": 101, "high": 103, "low": 100, "close": 102, "volume": 10},
        {"time": "2026-11-11 10:15", "open": 102, "high": 104, "low": 101, "close": 100.2, "volume": 10},
        {"time": "2026-11-11 10:30", "open": 100.2, "high": 105, "low": 98, "close": 100.5, "volume": 10},
        {"time": "2026-11-11 14:15", "open": 100.5, "high": 101, "low": 99, "close": 100.6, "volume": 10},
    ]
    bars_75m = resample_15m_to_75m(bars_15m)
    assert len(bars_75m) == 3
    assert bars_75m[0]["time"] == "2026-11-11 09:15"
    assert bars_75m[0]["high"] == 104
    assert bars_75m[0]["close"] == 100.2
    assert bars_75m[1]["time"] == "2026-11-11 10:30"
    assert bars_75m[2]["time"] == "2026-11-11 14:15"


def test_resample_daily_to_weekly():
    daily = [
        {"time": "2026-11-02", "open": 100, "high": 105, "low": 98, "close": 102, "volume": 100},
        {"time": "2026-11-06", "open": 102, "high": 108, "low": 101, "close": 106, "volume": 200},
    ]
    weekly = resample_daily_to_weekly(daily)
    assert len(weekly) == 1
    assert weekly[0]["open"] == 100
    assert weekly[0]["high"] == 108
    assert weekly[0]["low"] == 98
    assert weekly[0]["close"] == 106


def test_detect_doji_streak_and_coil_range():
    # Closed market timestamp (16:00 IST) keeps all bars
    closed_dt = datetime(2026, 11, 12, 16, 0, tzinfo=IST)
    candles = [
        {"time": "2026-11-10", "open": 100, "high": 110, "low": 99, "close": 109, "volume": 100},
        {"time": "2026-11-11", "open": 109, "high": 112, "low": 104, "close": 109.2, "volume": 100},
        {"time": "2026-11-12", "open": 109.1, "high": 111, "low": 105, "close": 109.0, "volume": 100},
    ]
    res = detect_doji_streak(candles, body_pct=10.0, tf="1D", now=closed_dt)
    assert res["streak"] == 2
    assert res["break_above"] == 112.0
    assert res["break_below"] == 104.0
    assert res["doji_indices"] == [1, 2]
    assert res["coil_range_pct"] == round(((112.0 - 104.0) / 109.0) * 100.0, 2)


def test_atm_strike_and_expiry_rollover():
    assert nearest_atm_strike(1148.0, 20.0) == 1140.0
    assert nearest_atm_strike(1152.0, 20.0) == 1160.0
    # Nov 2026 last Thursday is Nov 26; on Nov 26 it rolls to Dec 31
    assert get_nearest_monthly_expiry(date(2026, 11, 12)) == "2026-11-26"
    assert get_nearest_monthly_expiry(date(2026, 11, 26)) == "2026-12-31"


def test_api_meta():
    with TestClient(app) as client:
        res = client.get("/api/meta")
        assert res.status_code == 200
        data = res.json()
        assert data["universe_size"] == 218
        assert len(data["sectors"]) > 0

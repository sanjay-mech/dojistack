"""FastAPI backend + APScheduler cron jobs for DojiStack."""

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database import get_meta, init_db
from backend.doji import is_market_open
from backend.providers.angel_provider import angel_client
from backend.providers.bhavcopy_provider import ingest_recent_bhavcopies
from backend.screener import get_stock_detail, refresh_timeframe_cache, run_screen
from backend.universe import FNO_UNIVERSE, SECTORS, get_nearest_monthly_expiry

IST = ZoneInfo("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=IST)


def _cron_daily_bhavcopy() -> None:
    try:
        ingest_recent_bhavcopies(days_back=5)
        refresh_timeframe_cache("1D", force=True)
        refresh_timeframe_cache("1W", force=True)
    except Exception:
        pass


def _cron_intraday_75m() -> None:
    if angel_client.is_active():
        try:
            refresh_timeframe_cache("75m", force=True)
        except Exception:
            pass


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    scheduler.add_job(_cron_daily_bhavcopy, "cron", hour=18, minute=10, id="daily_bhavcopy", replace_existing=True)
    scheduler.add_job(_cron_intraday_75m, "cron", day_of_week="mon-fri", hour="9-15", minute="*/5", id="intraday_75m", replace_existing=True)
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="DojiStack API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/meta")
def api_meta() -> Dict[str, Any]:
    return {
        "sectors": SECTORS,
        "universe_size": len(FNO_UNIVERSE),
        "expiry": get_nearest_monthly_expiry(),
        "data_source": get_meta("data_source") or ("Angel One · Live" if angel_client.is_active() else "Yahoo + Bhavcopy"),
        "last_updated": get_meta("last_updated") or datetime.now(IST).strftime("%d %b %Y · %H:%M IST"),
        "is_live": is_market_open(),
    }


@app.get("/api/screen")
def api_screen(
    tf: str = Query("1D"),
    src: str = Query("stock"),
    min: int = Query(2, ge=1, le=10),
    body: float = Query(10.0, ge=1.0, le=30.0),
    sector: str = Query("all"),
    q: str = Query(""),
    refresh: bool = Query(False),
) -> Dict[str, Any]:
    return run_screen(
        tf=tf,
        src=src,
        min_doji=min,
        body_pct=body,
        sector=sector,
        q=q,
        force_refresh=refresh,
    )


@app.get("/api/stock/{symbol}")
def api_stock_detail(
    symbol: str,
    tf: str = Query("1D"),
    body: float = Query(10.0, ge=1.0, le=30.0),
) -> Dict[str, Any]:
    detail = get_stock_detail(symbol=symbol, tf=tf, body_pct=body)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")
    return detail


@app.post("/api/bhavcopy/ingest")
def api_ingest_bhavcopy(days: int = Query(10, ge=1, le=30)) -> Dict[str, Any]:
    count = ingest_recent_bhavcopies(days_back=days)
    return {"ingested_rows": count}


# Serve built React SPA when frontend/dist exists (single-service Render deployment)
_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _DIST_DIR.exists():
    _ASSETS_DIR = _DIST_DIR / "assets"
    if _ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(_ASSETS_DIR)), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str) -> FileResponse:
        candidate = _DIST_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(_DIST_DIR / "index.html"))

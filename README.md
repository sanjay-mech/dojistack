# DojiStack — Multiple Doji Screener for NSE F&O

A dark-themed, single-page Multiple Doji Screener for **76 NSE F&O stocks** and their **ATM Call (CE) / Put (PE)** option charts across **75-minute**, **Daily**, and **Weekly** timeframes.

## Project Structure

```text
DOUBLE DOJI/
├── .env
├── README.md
├── backend/
│   ├── main.py                  # FastAPI REST API + APScheduler cron jobs
│   ├── config.py                # Env settings (LIVE_MODE, Angel One, SQLite path)
│   ├── database.py              # SQLite cache (ohlcv_cache, bhavcopy_options, meta_state)
│   ├── doji.py                  # Doji detection, 75m/1W resampling, coil range
│   ├── universe.py              # 76 NSE F&O stocks, sectors, strike steps, expiry
│   ├── screener.py              # Spot + ATM CE/PE screening & confluence
│   ├── providers/
│   │   ├── yahoo_provider.py    # Yahoo Finance spot OHLC (15m->75m, 1D, 1W)
│   │   ├── bhavcopy_provider.py # NSE UDiFF F&O Bhavcopy downloader & option OHLC
│   │   └── angel_provider.py    # Angel One SmartAPI live mode (TOTP + rate limiter)
│   ├── requirements.txt
│   └── tests/test_doji_stack.py
└── frontend/
    ├── index.html
    ├── netlify.toml
    ├── public/_redirects        # SPA routing for Netlify
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx              # URL-synced filter state & layout
        ├── api.ts
        ├── types.ts
        └── components/
            ├── Navbar.tsx
            ├── Hero.tsx
            ├── FilterBar.tsx
            ├── SummaryCards.tsx
            ├── ResultsTable.tsx
            ├── StockDrawer.tsx  # 3x TradingView lightweight-charts (Spot, CE, PE)
            └── DojiIcons.tsx
```

## Environment Variables (`.env`)

```env
LIVE_MODE=false
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_ID=your_client_id
ANGEL_PIN=your_pin
ANGEL_TOTP_SECRET=your_totp_base32_secret
```

> `ANGEL_CLIENT_CODE` and `ANGEL_PASSWORD` are also supported as aliases.

## Running Locally

### 1. Backend (FastAPI + SQLite)
```powershell
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend (React + Vite)
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173/?tf=1D&src=stock&min=2&body=10&sector=all&q=`

## Deploying

- **Frontend (Netlify)**: Connect the repo, set base directory to `frontend`, build command `npm run build`, publish directory `dist` (configured in `frontend/netlify.toml` and `frontend/public/_redirects`). Set `VITE_API_BASE=https://your-backend-url` in Netlify environment variables.
- **Backend (Render / Railway / VPS)**: Run `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.

## Disclaimer
For educational use. Not investment advice.

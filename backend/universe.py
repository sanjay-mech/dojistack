"""NSE F&O stock universe, sectors, strike steps, and nearest monthly expiry."""

import calendar
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True)
class FnoStock:
    symbol: str
    yf_symbol: str
    name: str
    sector: str        # Display label e.g. "Banks", "IT"
    sector_slug: str   # URL slug e.g. "banks", "it"
    strike_step: float
    lot_size: int = 1


# 76 liquid NSE F&O stocks with sector and strike step
_FNO_STOCKS: List[Tuple[str, str, str, str, float, int]] = [
    # Banks
    ("HDFCBANK", "HDFC Bank Ltd", "Banks", "banks", 20.0, 550),
    ("ICICIBANK", "ICICI Bank Ltd", "Banks", "banks", 20.0, 700),
    ("SBIN", "State Bank of India", "Banks", "banks", 10.0, 750),
    ("KOTAKBANK", "Kotak Mahindra Bank Ltd", "Banks", "banks", 20.0, 400),
    ("AXISBANK", "Axis Bank Ltd", "Banks", "banks", 20.0, 625),
    ("INDUSINDBK", "IndusInd Bank Ltd", "Banks", "banks", 20.0, 500),
    ("BANKBARODA", "Bank of Baroda", "Banks", "banks", 5.0, 2925),
    ("PNB", "Punjab National Bank", "Banks", "banks", 2.5, 8000),
    ("CANBK", "Canara Bank", "Banks", "banks", 2.5, 6750),
    ("FEDERALBNK", "Federal Bank Ltd", "Banks", "banks", 2.5, 5000),

    # Financials
    ("BAJFINANCE", "Bajaj Finance Ltd", "Financials", "financials", 100.0, 125),
    ("BAJAJFINSV", "Bajaj Finserv Ltd", "Financials", "financials", 20.0, 500),
    ("JIOFIN", "Jio Financial Services", "Financials", "financials", 5.0, 2350),
    ("SHRIRAMFIN", "Shriram Finance Ltd", "Financials", "financials", 50.0, 150),
    ("CHOLAFIN", "Cholamandalam Investment", "Financials", "financials", 20.0, 625),
    ("HDFCLIFE", "HDFC Life Insurance", "Financials", "financials", 10.0, 1100),
    ("SBILIFE", "SBI Life Insurance", "Financials", "financials", 20.0, 375),
    ("PFC", "Power Finance Corp", "Financials", "financials", 10.0, 1300),
    ("RECLTD", "REC Ltd", "Financials", "financials", 10.0, 1000),
    ("MUTHOOTFIN", "Muthoot Finance Ltd", "Financials", "financials", 20.0, 275),

    # IT
    ("TCS", "Tata Consultancy Services", "IT", "it", 50.0, 175),
    ("INFY", "Infosys Ltd", "IT", "it", 20.0, 400),
    ("HCLTECH", "HCL Technologies Ltd", "IT", "it", 20.0, 350),
    ("WIPRO", "Wipro Ltd", "IT", "it", 5.0, 1500),
    ("TECHM", "Tech Mahindra Ltd", "IT", "it", 20.0, 600),
    ("LTIM", "LTIMindtree Ltd", "IT", "it", 100.0, 150),
    ("PERSISTENT", "Persistent Systems Ltd", "IT", "it", 100.0, 100),
    ("COFORGE", "Coforge Ltd", "IT", "it", 100.0, 75),

    # Energy
    ("RELIANCE", "Reliance Industries Ltd", "Energy", "energy", 20.0, 500),
    ("ONGC", "Oil & Natural Gas Corp", "Energy", "energy", 5.0, 1925),
    ("BPCL", "Bharat Petroleum Corp", "Energy", "energy", 5.0, 1800),
    ("IOC", "Indian Oil Corporation", "Energy", "energy", 2.5, 4875),
    ("GAIL", "GAIL (India) Ltd", "Energy", "energy", 5.0, 2575),
    ("NTPC", "NTPC Ltd", "Energy", "energy", 5.0, 1500),
    ("POWERGRID", "Power Grid Corp", "Energy", "energy", 5.0, 1800),
    ("TATAPOWER", "Tata Power Co Ltd", "Energy", "energy", 10.0, 1350),

    # Auto
    ("MARUTI", "Maruti Suzuki India Ltd", "Auto", "auto", 100.0, 50),
    ("M&M", "Mahindra & Mahindra Ltd", "Auto", "auto", 50.0, 175),
    ("TATAMOTORS", "Tata Motors Ltd", "Auto", "auto", 10.0, 550),
    ("BAJAJ-AUTO", "Bajaj Auto Ltd", "Auto", "auto", 100.0, 75),
    ("EICHERMOT", "Eicher Motors Ltd", "Auto", "auto", 50.0, 175),
    ("HEROMOTOCO", "Hero MotoCorp Ltd", "Auto", "auto", 50.0, 150),
    ("TVSMOTOR", "TVS Motor Company Ltd", "Auto", "auto", 50.0, 350),
    ("MOTHERSON", "Samvardhana Motherson", "Auto", "auto", 2.5, 4100),

    # Pharma
    ("SUNPHARMA", "Sun Pharmaceutical Ind", "Pharma", "pharma", 20.0, 350),
    ("CIPLA", "Cipla Ltd", "Pharma", "pharma", 20.0, 325),
    ("DRREDDY", "Dr. Reddy's Labs", "Pharma", "pharma", 20.0, 625),
    ("DIVISLAB", "Divi's Laboratories", "Pharma", "pharma", 100.0, 100),
    ("APOLLOHOSP", "Apollo Hospitals Ent", "Pharma", "pharma", 100.0, 125),
    ("LUPIN", "Lupin Ltd", "Pharma", "pharma", 20.0, 425),
    ("AUROPHARMA", "Aurobindo Pharma Ltd", "Pharma", "pharma", 20.0, 550),

    # FMCG
    ("HINDUNILVR", "Hindustan Unilever Ltd", "FMCG", "fmcg", 20.0, 300),
    ("ITC", "ITC Ltd", "FMCG", "fmcg", 5.0, 1600),
    ("NESTLEIND", "Nestle India Ltd", "FMCG", "fmcg", 20.0, 250),
    ("BRITANNIA", "Britannia Industries", "FMCG", "fmcg", 50.0, 100),
    ("TATACONSUM", "Tata Consumer Products", "FMCG", "fmcg", 20.0, 456),
    ("DABUR", "Dabur India Ltd", "FMCG", "fmcg", 10.0, 1250),
    ("VBL", "Varun Beverages Ltd", "FMCG", "fmcg", 10.0, 875),

    # Metals
    ("TATASTEEL", "Tata Steel Ltd", "Metals", "metals", 2.5, 5500),
    ("JSWSTEEL", "JSW Steel Ltd", "Metals", "metals", 20.0, 675),
    ("HINDALCO", "Hindalco Industries", "Metals", "metals", 10.0, 1400),
    ("COALINDIA", "Coal India Ltd", "Metals", "metals", 10.0, 1050),
    ("VEDL", "Vedanta Ltd", "Metals", "metals", 10.0, 1150),
    ("JINDALSTEL", "Jindal Steel & Power", "Metals", "metals", 20.0, 625),

    # Telecom
    ("BHARTIARTL", "Bharti Airtel Ltd", "Telecom", "telecom", 20.0, 475),
    ("INDUSTOWER", "Indus Towers Ltd", "Telecom", "telecom", 5.0, 1700),

    # Infra
    ("LT", "Larsen & Toubro Ltd", "Infra", "infra", 50.0, 150),
    ("ADANIPORTS", "Adani Ports & SEZ Ltd", "Infra", "infra", 20.0, 400),
    ("ADANIENT", "Adani Enterprises Ltd", "Infra", "infra", 50.0, 300),
    ("HAL", "Hindustan Aeronautics", "Infra", "infra", 100.0, 150),
    ("BEL", "Bharat Electronics Ltd", "Infra", "infra", 5.0, 2850),
    ("DLF", "DLF Ltd", "Infra", "infra", 10.0, 825),

    # Consumer
    ("TITAN", "Titan Company Ltd", "Consumer", "consumer", 50.0, 175),
    ("TRENT", "Trent Ltd", "Consumer", "consumer", 100.0, 100),
    ("ASIANPAINT", "Asian Paints Ltd", "Consumer", "consumer", 50.0, 200),
    ("INDIGO", "InterGlobe Aviation", "Consumer", "consumer", 50.0, 150),
]

FNO_UNIVERSE: List[FnoStock] = [
    FnoStock(
        symbol=sym,
        yf_symbol=f"{sym}.NS",
        name=name,
        sector=sec,
        sector_slug=slug,
        strike_step=step,
        lot_size=lot,
    )
    for sym, name, sec, slug, step, lot in _FNO_STOCKS
]

BY_SYMBOL: Dict[str, FnoStock] = {s.symbol: s for s in FNO_UNIVERSE}

SECTORS: List[Dict[str, str]] = [
    {"slug": slug, "label": label}
    for slug, label in sorted({(s.sector_slug, s.sector) for s in FNO_UNIVERSE}, key=lambda x: x[1])
]


def nearest_atm_strike(spot: float, step: float) -> float:
    """Round spot price to the nearest valid option strike."""
    if step <= 0:
        return round(spot, 2)
    return round(round(spot / step) * step, 2)


def _last_thursday(year: int, month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    d = date(year, month, last_day)
    # Thursday is weekday() == 3
    offset = (d.weekday() - 3) % 7
    return date(year, month, last_day - offset)


def get_nearest_monthly_expiry(ref_date: date | None = None) -> str:
    """
    Return the nearest monthly F&O expiry (YYYY-MM-DD).
    Rolls to next month's expiry on or after expiry day.
    """
    today = ref_date or datetime.now(IST).date()
    exp = _last_thursday(today.year, today.month)
    if today >= exp:
        next_month = today.month + 1
        next_year = today.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        exp = _last_thursday(next_year, next_month)
    return exp.isoformat()

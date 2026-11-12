"""Full NSE F&O stock universe (218+ stocks), sectors, strike steps, and nearest monthly expiry."""

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
    sector: str
    sector_slug: str
    strike_step: float
    lot_size: int = 1


_SECTOR_MAP: Dict[str, Tuple[str, str]] = {
    # Banks
    "AUBANK": ("Banks", "banks"),
    "AXISBANK": ("Banks", "banks"),
    "BANDHANBNK": ("Banks", "banks"),
    "BANKBARODA": ("Banks", "banks"),
    "BANKINDIA": ("Banks", "banks"),
    "CANBK": ("Banks", "banks"),
    "CUB": ("Banks", "banks"),
    "FEDERALBNK": ("Banks", "banks"),
    "HDFCBANK": ("Banks", "banks"),
    "ICICIBANK": ("Banks", "banks"),
    "IDFCFIRSTB": ("Banks", "banks"),
    "INDIANB": ("Banks", "banks"),
    "INDUSINDBK": ("Banks", "banks"),
    "KARURVYSYA": ("Banks", "banks"),
    "KOTAKBANK": ("Banks", "banks"),
    "MAHABANK": ("Banks", "banks"),
    "PNB": ("Banks", "banks"),
    "RBLBANK": ("Banks", "banks"),
    "SBIN": ("Banks", "banks"),
    "UJJIVANSFB": ("Banks", "banks"),
    "UNIONBANK": ("Banks", "banks"),
    "YESBANK": ("Banks", "banks"),

    # Financials
    "360ONE": ("Financials", "financials"),
    "ABCAPITAL": ("Financials", "financials"),
    "ANGELONE": ("Financials", "financials"),
    "BAJAJFINSV": ("Financials", "financials"),
    "BAJFINANCE": ("Financials", "financials"),
    "BSE": ("Financials", "financials"),
    "CAMS": ("Financials", "financials"),
    "CDSL": ("Financials", "financials"),
    "CHOLAFIN": ("Financials", "financials"),
    "HDFCAMC": ("Financials", "financials"),
    "HDFCLIFE": ("Financials", "financials"),
    "ICICIGI": ("Financials", "financials"),
    "ICICILIFE": ("Financials", "financials"),
    "IEX": ("Financials", "financials"),
    "IREDA": ("Financials", "financials"),
    "IRFC": ("Financials", "financials"),
    "JIOFIN": ("Financials", "financials"),
    "KFINTECH": ("Financials", "financials"),
    "LICHSGFIN": ("Financials", "financials"),
    "LICI": ("Financials", "financials"),
    "LTF": ("Financials", "financials"),
    "MANAPPURAM": ("Financials", "financials"),
    "MCX": ("Financials", "financials"),
    "MFSL": ("Financials", "financials"),
    "MOTILALOFS": ("Financials", "financials"),
    "MUTHOOTFIN": ("Financials", "financials"),
    "NAM-INDIA": ("Financials", "financials"),
    "PAYTM": ("Financials", "financials"),
    "PFC": ("Financials", "financials"),
    "PNBHOUSING": ("Financials", "financials"),
    "POLICYBZR": ("Financials", "financials"),
    "RECLTD": ("Financials", "financials"),
    "SBICARD": ("Financials", "financials"),
    "SBILIFE": ("Financials", "financials"),
    "SHRIRAMFIN": ("Financials", "financials"),

    # IT
    "COFORGE": ("IT", "it"),
    "HCLTECH": ("IT", "it"),
    "INFY": ("IT", "it"),
    "KPITTECH": ("IT", "it"),
    "LTM": ("IT", "it"),
    "MPHASIS": ("IT", "it"),
    "NAUKRI": ("IT", "it"),
    "OFSS": ("IT", "it"),
    "PERSISTENT": ("IT", "it"),
    "SAGILITY": ("IT", "it"),
    "TATAELXSI": ("IT", "it"),
    "TCS": ("IT", "it"),
    "TECHM": ("IT", "it"),
    "WIPRO": ("IT", "it"),

    # Energy
    "ADANIENSOL": ("Energy", "energy"),
    "ADANIGREEN": ("Energy", "energy"),
    "ADANIPOWER": ("Energy", "energy"),
    "BPCL": ("Energy", "energy"),
    "GAIL": ("Energy", "energy"),
    "GVT&D": ("Energy", "energy"),
    "HINDPETRO": ("Energy", "energy"),
    "INOXWIND": ("Energy", "energy"),
    "IOC": ("Energy", "energy"),
    "JSWENERGY": ("Energy", "energy"),
    "NHPC": ("Energy", "energy"),
    "NTPC": ("Energy", "energy"),
    "OIL": ("Energy", "energy"),
    "ONGC": ("Energy", "energy"),
    "PETRONET": ("Energy", "energy"),
    "POWERGRID": ("Energy", "energy"),
    "PREMIERENE": ("Energy", "energy"),
    "RELIANCE": ("Energy", "energy"),
    "SUZLON": ("Energy", "energy"),
    "TATAPOWER": ("Energy", "energy"),
    "WAAREEENER": ("Energy", "energy"),

    # Auto
    "ASHOKLEY": ("Auto", "auto"),
    "ATHERENERG": ("Auto", "auto"),
    "BAJAJ-AUTO": ("Auto", "auto"),
    "BHARATFORG": ("Auto", "auto"),
    "BOSCHLTD": ("Auto", "auto"),
    "EICHERMOT": ("Auto", "auto"),
    "FORCEMOT": ("Auto", "auto"),
    "HEROMOTOCO": ("Auto", "auto"),
    "HYUNDAI": ("Auto", "auto"),
    "M&M": ("Auto", "auto"),
    "MARUTI": ("Auto", "auto"),
    "MOTHERSON": ("Auto", "auto"),
    "SONACOMS": ("Auto", "auto"),
    "TIINDIA": ("Auto", "auto"),
    "TMPV": ("Auto", "auto"),
    "TVSMOTOR": ("Auto", "auto"),
    "UNOMINDA": ("Auto", "auto"),

    # Pharma
    "ALKEM": ("Pharma", "pharma"),
    "APOLLOHOSP": ("Pharma", "pharma"),
    "AUROPHARMA": ("Pharma", "pharma"),
    "BIOCON": ("Pharma", "pharma"),
    "CIPLA": ("Pharma", "pharma"),
    "DIVISLAB": ("Pharma", "pharma"),
    "DRREDDY": ("Pharma", "pharma"),
    "FORTIS": ("Pharma", "pharma"),
    "GLENMARK": ("Pharma", "pharma"),
    "LAURUSLABS": ("Pharma", "pharma"),
    "LUPIN": ("Pharma", "pharma"),
    "MANKIND": ("Pharma", "pharma"),
    "MAXHEALTH": ("Pharma", "pharma"),
    "SUNPHARMA": ("Pharma", "pharma"),
    "TORNTPHARM": ("Pharma", "pharma"),
    "ZYDUSLIFE": ("Pharma", "pharma"),

    # FMCG
    "BRITANNIA": ("FMCG", "fmcg"),
    "COLPAL": ("FMCG", "fmcg"),
    "DABUR": ("FMCG", "fmcg"),
    "GODFRYPHLP": ("FMCG", "fmcg"),
    "GODREJCP": ("FMCG", "fmcg"),
    "HINDUNILVR": ("FMCG", "fmcg"),
    "ITC": ("FMCG", "fmcg"),
    "MARICO": ("FMCG", "fmcg"),
    "NESTLEIND": ("FMCG", "fmcg"),
    "PATANJALI": ("FMCG", "fmcg"),
    "RADICO": ("FMCG", "fmcg"),
    "TATACONSUM": ("FMCG", "fmcg"),
    "UNITDSPR": ("FMCG", "fmcg"),
    "VBL": ("FMCG", "fmcg"),

    # Metals
    "APLAPOLLO": ("Metals", "metals"),
    "COALINDIA": ("Metals", "metals"),
    "HINDALCO": ("Metals", "metals"),
    "HINDZINC": ("Metals", "metals"),
    "JINDALSTEL": ("Metals", "metals"),
    "JSWSTEEL": ("Metals", "metals"),
    "NATIONALUM": ("Metals", "metals"),
    "NMDC": ("Metals", "metals"),
    "SAIL": ("Metals", "metals"),
    "TATASTEEL": ("Metals", "metals"),
    "VEDL": ("Metals", "metals"),

    # Telecom
    "BHARTIARTL": ("Telecom", "telecom"),
    "IDEA": ("Telecom", "telecom"),
    "INDUSTOWER": ("Telecom", "telecom"),

    # Infra & Capital Goods
    "ABB": ("Infra", "infra"),
    "ADANIENT": ("Infra", "infra"),
    "ADANIPORTS": ("Infra", "infra"),
    "BDL": ("Infra", "infra"),
    "BEL": ("Infra", "infra"),
    "BHEL": ("Infra", "infra"),
    "CGPOWER": ("Infra", "infra"),
    "COCHINSHIP": ("Infra", "infra"),
    "CONCOR": ("Infra", "infra"),
    "CUMMINSIND": ("Infra", "infra"),
    "DATAPATTNS": ("Infra", "infra"),
    "DELHIVERY": ("Infra", "infra"),
    "DLF": ("Infra", "infra"),
    "ENRIN": ("Infra", "infra"),
    "GMRAIRPORT": ("Infra", "infra"),
    "GODREJPROP": ("Infra", "infra"),
    "HAL": ("Infra", "infra"),
    "INDIGO": ("Infra", "infra"),
    "LODHA": ("Infra", "infra"),
    "LT": ("Infra", "infra"),
    "MAZDOCK": ("Infra", "infra"),
    "NBCC": ("Infra", "infra"),
    "OBEROIRLTY": ("Infra", "infra"),
    "PHOENIXLTD": ("Infra", "infra"),
    "POWERINDIA": ("Infra", "infra"),
    "PRESTIGE": ("Infra", "infra"),
    "RVNL": ("Infra", "infra"),
    "SIEMENS": ("Infra", "infra"),
    "SOLARINDS": ("Infra", "infra"),

    # Consumer
    "AMBER": ("Consumer", "consumer"),
    "ASIANPAINT": ("Consumer", "consumer"),
    "ASTRAL": ("Consumer", "consumer"),
    "BLUESTARCO": ("Consumer", "consumer"),
    "CROMPTON": ("Consumer", "consumer"),
    "DIXON": ("Consumer", "consumer"),
    "DMART": ("Consumer", "consumer"),
    "ETERNAL": ("Consumer", "consumer"),
    "HAVELLS": ("Consumer", "consumer"),
    "INDHOTEL": ("Consumer", "consumer"),
    "JUBLFOOD": ("Consumer", "consumer"),
    "KALYANKJIL": ("Consumer", "consumer"),
    "KAYNES": ("Consumer", "consumer"),
    "KEI": ("Consumer", "consumer"),
    "NYKAA": ("Consumer", "consumer"),
    "PAGEIND": ("Consumer", "consumer"),
    "PGEL": ("Consumer", "consumer"),
    "POLYCAB": ("Consumer", "consumer"),
    "SUPREMEIND": ("Consumer", "consumer"),
    "SWIGGY": ("Consumer", "consumer"),
    "SYRMA": ("Consumer", "consumer"),
    "TITAN": ("Consumer", "consumer"),
    "TRENT": ("Consumer", "consumer"),
    "VMM": ("Consumer", "consumer"),
    "VOLTAS": ("Consumer", "consumer"),

    # Chemicals & Cement
    "AMBUJACEM": ("Chemicals & Cement", "chemicals"),
    "COROMANDEL": ("Chemicals & Cement", "chemicals"),
    "GRASIM": ("Chemicals & Cement", "chemicals"),
    "NAVINFLUOR": ("Chemicals & Cement", "chemicals"),
    "PIDILITIND": ("Chemicals & Cement", "chemicals"),
    "PIIND": ("Chemicals & Cement", "chemicals"),
    "SHREECEM": ("Chemicals & Cement", "chemicals"),
    "SRF": ("Chemicals & Cement", "chemicals"),
    "ULTRACEMCO": ("Chemicals & Cement", "chemicals"),
    "UPL": ("Chemicals & Cement", "chemicals"),
}

# All 218 live NSE F&O OPTSTK underlyings: (symbol, strike_step, lot_size)
_RAW_FNO: List[Tuple[str, float, int]] = [
    ("360ONE", 20.0, 500), ("ABB", 100.0, 125), ("ABCAPITAL", 5.0, 1550),
    ("ADANIENSOL", 20.0, 675), ("ADANIENT", 50.0, 309), ("ADANIGREEN", 20.0, 600),
    ("ADANIPORTS", 20.0, 475), ("ADANIPOWER", 2.5, 3550), ("ALKEM", 50.0, 125),
    ("AMBER", 100.0, 100), ("AMBUJACEM", 5.0, 1200), ("ANANDRATHI", 20.0, 250),
    ("ANGELONE", 5.0, 2500), ("APLAPOLLO", 20.0, 350), ("APOLLOHOSP", 100.0, 125),
    ("ASHOKLEY", 2.5, 5000), ("ASIANPAINT", 20.0, 250), ("ASTRAL", 20.0, 425),
    ("ATHERENERG", 20.0, 375), ("AUBANK", 10.0, 500), ("AUROPHARMA", 20.0, 550),
    ("AXISBANK", 10.0, 625), ("BAJAJ-AUTO", 100.0, 75), ("BAJAJFINSV", 20.0, 300),
    ("BAJFINANCE", 10.0, 750), ("BANDHANBNK", 2.5, 3600), ("BANKBARODA", 2.5, 2925),
    ("BANKINDIA", 2.5, 5200), ("BDL", 20.0, 425), ("BEL", 5.0, 1425),
    ("BHARATFORG", 20.0, 500), ("BHARTIARTL", 20.0, 475), ("BHEL", 10.0, 2625),
    ("BIOCON", 5.0, 2500), ("BLUESTARCO", 20.0, 325), ("BOSCHLTD", 500.0, 25),
    ("BPCL", 5.0, 1975), ("BRITANNIA", 50.0, 125), ("BSE", 50.0, 200),
    ("CAMS", 10.0, 825), ("CANBK", 1.0, 6750), ("CDSL", 20.0, 475),
    ("CGPOWER", 10.0, 850), ("CHOLAFIN", 20.0, 625), ("CIPLA", 10.0, 425),
    ("COALINDIA", 5.0, 1350), ("COCHINSHIP", 20.0, 400), ("COFORGE", 20.0, 475),
    ("COLPAL", 20.0, 275), ("CONCOR", 5.0, 1250), ("COROMANDEL", 20.0, 300),
    ("CROMPTON", 2.5, 2150), ("CUB", 5.0, 2325), ("CUMMINSIND", 50.0, 100),
    ("DABUR", 5.0, 1250), ("DATAPATTNS", 100.0, 125), ("DELHIVERY", 5.0, 2075),
    ("DIVISLAB", 100.0, 100), ("DIXON", 250.0, 50), ("DLF", 10.0, 950),
    ("DMART", 50.0, 150), ("DRREDDY", 10.0, 625), ("EICHERMOT", 100.0, 100),
    ("ENRIN", 50.0, 175), ("ETERNAL", 5.0, 2425), ("FEDERALBNK", 5.0, 2500),
    ("FORCEMOT", 250.0, 25), ("FORTIS", 10.0, 775), ("GAIL", 2.5, 3550),
    ("GLENMARK", 20.0, 375), ("GMRAIRPORT", 1.0, 6975), ("GODFRYPHLP", 20.0, 275),
    ("GODREJCP", 10.0, 500), ("GODREJPROP", 20.0, 325), ("GRASIM", 20.0, 250),
    ("GVT&D", 100.0, 125), ("HAL", 50.0, 150), ("HAVELLS", 10.0, 500),
    ("HCLTECH", 20.0, 400), ("HDFCAMC", 20.0, 300), ("HDFCBANK", 10.0, 650),
    ("HDFCLIFE", 5.0, 1100), ("HEROMOTOCO", 50.0, 150), ("HINDALCO", 10.0, 700),
    ("HINDPETRO", 5.0, 2025), ("HINDUNILVR", 20.0, 300), ("HINDZINC", 10.0, 1225),
    ("HYUNDAI", 20.0, 275), ("ICICIBANK", 10.0, 700), ("ICICIGI", 20.0, 325),
    ("ICICILIFE", 5.0, 925), ("IDEA", 1.0, 71475), ("IDFCFIRSTB", 1.0, 9275),
    ("IEX", 1.0, 4350), ("INDHOTEL", 10.0, 1000), ("INDIANB", 10.0, 1000),
    ("INDIGO", 50.0, 150), ("INDUSINDBK", 10.0, 700), ("INDUSTOWER", 5.0, 1700),
    ("INFY", 20.0, 400), ("INOXWIND", 1.0, 6400), ("IOC", 1.0, 4875),
    ("IREDA", 1.0, 4525), ("IRFC", 1.0, 5425), ("ITC", 2.5, 1725),
    ("JINDALSTEL", 20.0, 625), ("JIOFIN", 2.5, 2350), ("JSWENERGY", 10.0, 1075),
    ("JSWSTEEL", 10.0, 675), ("JUBLFOOD", 10.0, 1250), ("KALYANKJIL", 10.0, 1350),
    ("KARURVYSYA", 5.0, 1550), ("KAYNES", 50.0, 150), ("KEI", 100.0, 175),
    ("KFINTECH", 20.0, 575), ("KOTAKBANK", 5.0, 2000), ("KPITTECH", 10.0, 775),
    ("LAURUSLABS", 20.0, 425), ("LICHSGFIN", 5.0, 1000), ("LICI", 5.0, 1400),
    ("LODHA", 20.0, 625), ("LT", 50.0, 175), ("LTF", 5.0, 2250),
    ("LTM", 100.0, 150), ("LUPIN", 20.0, 425), ("M&M", 50.0, 200),
    ("MAHABANK", 1.0, 6500), ("MANAPPURAM", 5.0, 3000), ("MANKIND", 20.0, 250),
    ("MARICO", 10.0, 1200), ("MARUTI", 100.0, 50), ("MAXHEALTH", 10.0, 525),
    ("MAZDOCK", 20.0, 225), ("MCX", 50.0, 225), ("MFSL", 20.0, 400),
    ("MOTHERSON", 2.5, 6150), ("MOTILALOFS", 20.0, 775), ("MPHASIS", 50.0, 275),
    ("MUTHOOTFIN", 50.0, 275), ("NAM-INDIA", 20.0, 625), ("NATIONALUM", 5.0, 1875),
    ("NAUKRI", 20.0, 550), ("NAVINFLUOR", 100.0, 75), ("NBCC", 1.0, 6500),
    ("NESTLEIND", 20.0, 500), ("NHPC", 1.0, 6950), ("NMDC", 1.0, 6750),
    ("NTPC", 2.5, 1500), ("NYKAA", 5.0, 1575), ("OBEROIRLTY", 20.0, 350),
    ("OFSS", 50.0, 50), ("OIL", 5.0, 1400), ("ONGC", 2.5, 2250),
    ("PAGEIND", 500.0, 20), ("PATANJALI", 5.0, 1075), ("PAYTM", 20.0, 725),
    ("PERSISTENT", 100.0, 125), ("PETRONET", 5.0, 1900), ("PFC", 5.0, 1300),
    ("PGEL", 10.0, 950), ("PHOENIXLTD", 20.0, 350), ("PIDILITIND", 20.0, 500),
    ("PIIND", 20.0, 175), ("PNB", 1.0, 8000), ("PNBHOUSING", 20.0, 650),
    ("POLICYBZR", 20.0, 350), ("POLYCAB", 100.0, 125), ("POWERGRID", 2.5, 1900),
    ("POWERINDIA", 500.0, 25), ("PREMIERENE", 20.0, 650), ("PRESTIGE", 20.0, 450),
    ("RADICO", 50.0, 150), ("RBLBANK", 5.0, 3175), ("RECLTD", 5.0, 1575),
    ("RELIANCE", 10.0, 500), ("RVNL", 2.5, 1925), ("SAGILITY", 1.0, 12000),
    ("SAIL", 2.5, 4700), ("SBICARD", 10.0, 800), ("SBILIFE", 20.0, 375),
    ("SBIN", 10.0, 750), ("SHREECEM", 250.0, 25), ("SHRIRAMFIN", 20.0, 825),
    ("SIEMENS", 50.0, 175), ("SOLARINDS", 250.0, 25), ("SONACOMS", 10.0, 1225),
    ("SRF", 20.0, 200), ("SUNPHARMA", 20.0, 350), ("SUPREMEIND", 50.0, 175),
    ("SUZLON", 1.0, 12700), ("SWIGGY", 5.0, 1825), ("SYRMA", 20.0, 325),
    ("TATACONSUM", 10.0, 550), ("TATAELXSI", 50.0, 125), ("TATAPOWER", 5.0, 1450),
    ("TATASTEEL", 2.5, 2750), ("TCS", 20.0, 225), ("TECHM", 20.0, 600),
    ("TIINDIA", 50.0, 200), ("TITAN", 50.0, 175), ("TMPV", 5.0, 1600),
    ("TORNTPHARM", 50.0, 125), ("TRENT", 50.0, 225), ("TVSMOTOR", 50.0, 175),
    ("UJJIVANSFB", 1.0, 8000), ("ULTRACEMCO", 100.0, 50), ("UNIONBANK", 2.5, 4425),
    ("UNITDSPR", 20.0, 400), ("UNOMINDA", 20.0, 550), ("UPL", 5.0, 1355),
    ("VBL", 5.0, 1275), ("VEDL", 5.0, 1150), ("VMM", 1.0, 4850),
    ("VOLTAS", 20.0, 375), ("WAAREEENER", 20.0, 175), ("WIPRO", 2.5, 3000),
    ("YESBANK", 1.0, 31100), ("ZYDUSLIFE", 10.0, 450),
]

FNO_UNIVERSE: List[FnoStock] = [
    FnoStock(
        symbol=sym,
        yf_symbol=f"{sym}.NS",
        name=sym,
        sector=_SECTOR_MAP.get(sym, ("Other", "other"))[0],
        sector_slug=_SECTOR_MAP.get(sym, ("Other", "other"))[1],
        strike_step=step,
        lot_size=lot,
    )
    for sym, step, lot in _RAW_FNO
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

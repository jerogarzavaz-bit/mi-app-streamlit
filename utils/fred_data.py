import requests
import pandas as pd
import streamlit as st

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

FRED_SERIES = {
    "Fed Funds Rate": "FEDFUNDS",
    "CPI YoY": "CPIAUCSL",
    "Unemployment": "UNRATE",
    "10Y Treasury": "DGS10",
    "2Y Treasury": "DGS2",
    "30Y Mortgage": "MORTGAGE30US",
    "M2 Money Supply": "M2SL",
    "PCE Inflation": "PCEPI",
    "GDP Growth": "A191RL1Q225SBEA",
    "CAPE Ratio": "CAPE",
    "Industrial Production": "INDPRO",
    "Retail Sales": "RSAFS",
}

# Series that represent levels and need YoY % change
_YOY_SERIES = {"CPIAUCSL", "PCEPI"}


@st.cache_data(ttl=3600)
def get_fred_series(series_id: str, api_key: str, limit: int = 60) -> pd.Series | None:
    """Fetches a FRED series. Returns pd.Series with DatetimeIndex, None on error."""
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit + 12 if series_id in _YOY_SERIES else limit,
    }
    try:
        resp = requests.get(FRED_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        observations = resp.json().get("observations", [])
        if not observations:
            return None

        s = pd.Series(
            {obs["date"]: obs["value"] for obs in observations if obs["value"] != "."}
        )
        s.index = pd.to_datetime(s.index)
        s = s.sort_index().astype(float)

        if series_id in _YOY_SERIES:
            s = s.pct_change(12).dropna() * 100
            s = s.tail(limit)

        return s
    except Exception:
        return None


@st.cache_data(ttl=3600)
def get_multiple_series(series_ids: list[str], api_key: str, limit: int = 60) -> dict[str, pd.Series]:
    """Fetches multiple FRED series. Returns dict name→Series."""
    # Build reverse lookup: series_id → name
    id_to_name = {v: k for k, v in FRED_SERIES.items()}
    result = {}
    for sid in series_ids:
        s = get_fred_series(sid, api_key, limit)
        if s is not None:
            name = id_to_name.get(sid, sid)
            result[name] = s
    return result


def get_yield_curve(api_key: str) -> dict:
    """Returns dict of maturity label → latest yield (float)."""
    maturities = {
        "3M": "DGS3MO",
        "6M": "DGS6MO",
        "1Y": "DGS1",
        "2Y": "DGS2",
        "5Y": "DGS5",
        "10Y": "DGS10",
        "30Y": "DGS30",
    }
    result = {}
    for label, sid in maturities.items():
        s = get_fred_series(sid, api_key, limit=5)
        if s is not None and not s.empty:
            result[label] = round(float(s.iloc[-1]), 4)
    return result

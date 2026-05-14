import yfinance as yf
import pandas as pd
import streamlit as st

CHAIN_COLUMNS = ["strike", "lastPrice", "bid", "ask", "volume", "openInterest", "impliedVolatility", "inTheMoney"]


def _filter_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in CHAIN_COLUMNS if c in df.columns]
    result = df[cols].copy()
    if "impliedVolatility" in result.columns:
        result["impliedVolatility"] = (result["impliedVolatility"] * 100).round(2)
    return result


@st.cache_data(ttl=300)
def get_options_chain(ticker: str) -> dict:
    """Returns dict with calls, puts, expiration_dates, info. Empty dict on error."""
    try:
        t = yf.Ticker(ticker)
        expirations = t.options
        if not expirations:
            return {}
        chain = t.option_chain(expirations[0])
        info = t.fast_info
        return {
            "calls": _filter_columns(chain.calls),
            "puts": _filter_columns(chain.puts),
            "expiration_dates": list(expirations),
            "info": info,
        }
    except Exception:
        return {}


@st.cache_data(ttl=300)
def get_options_for_expiry(ticker: str, expiry: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (calls_df, puts_df) for a specific expiry. Empty DFs on error."""
    empty = pd.DataFrame()
    try:
        chain = yf.Ticker(ticker).option_chain(expiry)
        return _filter_columns(chain.calls), _filter_columns(chain.puts)
    except Exception:
        return empty, empty


def get_options_summary(ticker: str) -> dict:
    """Returns ticker, current_price, iv_percentile, total_call_oi, total_put_oi, put_call_ratio, nearest_expiry."""
    try:
        t = yf.Ticker(ticker)
        expirations = t.options
        if not expirations:
            return {}

        nearest_expiry = expirations[0]
        chain = t.option_chain(nearest_expiry)
        calls, puts = chain.calls, chain.puts

        total_call_oi = int(calls["openInterest"].fillna(0).sum())
        total_put_oi = int(puts["openInterest"].fillna(0).sum())
        put_call_ratio = round(total_put_oi / total_call_oi, 4) if total_call_oi > 0 else None

        # Approximate IV percentile from current expiry IVs
        all_ivs = pd.concat([calls["impliedVolatility"], puts["impliedVolatility"]]).dropna()
        iv_percentile = round(float(all_ivs.rank(pct=True).mean()) * 100, 2) if not all_ivs.empty else None

        current_price = t.fast_info.last_price

        return {
            "ticker": ticker.upper(),
            "current_price": current_price,
            "iv_percentile": iv_percentile,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "put_call_ratio": put_call_ratio,
            "nearest_expiry": nearest_expiry,
        }
    except Exception:
        return {}

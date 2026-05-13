import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta


@st.cache_data(ttl=3600)
def get_dividend_data(ticker: str) -> dict:
    """Fetch dividend info for a single ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        divs = t.dividends
        annual = info.get("dividendRate") or 0
        yld = (info.get("dividendYield") or 0) * 100
        ex_date = info.get("exDividendDate")
        if ex_date:
            import datetime
            ex_date = datetime.datetime.fromtimestamp(ex_date).strftime("%Y-%m-%d")
        payout = (info.get("payoutRatio") or 0) * 100
        # 5-year dividend growth rate
        growth = 0.0
        if len(divs) >= 5:
            annual_divs = divs.resample("YE").sum()
            if len(annual_divs) >= 5 and annual_divs.iloc[-5] > 0:
                growth = ((annual_divs.iloc[-1] / annual_divs.iloc[-5]) ** 0.2 - 1) * 100
        return {
            "ticker": ticker, "annual_dividend": round(annual, 4),
            "yield_pct": round(yld, 2), "ex_date": ex_date,
            "payout_ratio": round(payout, 1), "growth_5yr": round(growth, 2),
            "frequency": _infer_frequency(divs),
        }
    except Exception:
        return {"ticker": ticker, "annual_dividend": 0, "yield_pct": 0,
                "ex_date": None, "payout_ratio": 0, "growth_5yr": 0, "frequency": "N/A"}


def _infer_frequency(divs) -> str:
    if divs is None or len(divs) < 2:
        return "N/A"
    try:
        avg_days = (divs.index[-1] - divs.index[0]).days / max(len(divs) - 1, 1)
        if avg_days < 40:
            return "Monthly"
        if avg_days < 100:
            return "Quarterly"
        if avg_days < 200:
            return "Semi-Annual"
        return "Annual"
    except Exception:
        return "N/A"


@st.cache_data(ttl=3600)
def get_portfolio_dividend_calendar(tickers: tuple) -> list:
    """Return upcoming ex-dividend events for the next 12 months."""
    events = []
    cutoff = date.today() + timedelta(days=365)
    for t in tickers:
        d = get_dividend_data(t)
        if d["ex_date"]:
            try:
                ex = date.fromisoformat(d["ex_date"])
                if date.today() <= ex <= cutoff:
                    freq_divisor = {"Quarterly": 4, "Monthly": 12, "Semi-Annual": 2, "Annual": 1}
                    divisor = freq_divisor.get(d["frequency"], 4) or 4
                    events.append({
                        "ticker": t,
                        "ex_date": d["ex_date"],
                        "amount": d["annual_dividend"] / divisor,
                        "frequency": d["frequency"],
                    })
            except Exception:
                pass
    return sorted(events, key=lambda x: x["ex_date"])


def get_portfolio_annual_income(holdings: list) -> dict:
    """Compute projected annual dividend income for a portfolio."""
    total = 0.0
    by_ticker = {}
    monthly = {m: 0.0 for m in range(1, 13)}
    for h in holdings:
        t = h.get("ticker", "")
        qty = h.get("quantity", 0)
        d = get_dividend_data(t)
        annual = d["annual_dividend"] * qty
        total += annual
        by_ticker[t] = round(annual, 2)
        # distribute across months by frequency
        freq_map = {
            "Monthly": list(range(1, 13)),
            "Quarterly": [3, 6, 9, 12],
            "Semi-Annual": [6, 12],
            "Annual": [12],
        }
        months = freq_map.get(d["frequency"], [3, 6, 9, 12])
        per_payment = annual / len(months) if months else 0
        for m in months:
            monthly[m] += per_payment
    return {
        "total_annual": round(total, 2),
        "monthly_breakdown": {m: round(v, 2) for m, v in monthly.items()},
        "by_ticker": by_ticker,
    }

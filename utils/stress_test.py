import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

SCENARIOS = {
    "2008 Financial Crisis":  {"market": -37, "Financials": -55, "Energy": -45, "Technology": -42, "Real Estate": -68},
    "2020 COVID Crash":       {"market": -34, "Consumer Cyclical": -45, "Energy": -55, "Technology": -20, "Healthcare": -10},
    "2022 Rate Hike Cycle":   {"market": -19, "Technology": -33, "Communication": -40, "Utilities": -5, "Energy": 40},
    "Tech Bubble Burst":      {"market": -20, "Technology": -45, "Communication": -38, "Consumer Defensive": 5},
    "Mild Recession":         {"market": -15, "Consumer Cyclical": -22, "Financials": -20, "Consumer Defensive": -5, "Utilities": 0},
    "Inflation Spike":        {"market": -10, "Energy": 30, "Materials": 22, "Technology": -18, "Consumer Defensive": 5},
    "Flash Crash -10%":       {"market": -10},
    "Bull Market Rally +20%": {"market": 20},
}


@st.cache_data(ttl=3600)
def _get_holding_meta(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info or {}
        return {"beta": info.get("beta") or 1.0, "sector": info.get("sector") or "Unknown"}
    except Exception:
        return {"beta": 1.0, "sector": "Unknown"}


def run_stress_test(holdings: list) -> dict:
    results = {}
    total_value = sum(h.get("current_value", 0) for h in holdings) or 1
    for scenario, shocks in SCENARIOS.items():
        market_shock = shocks.get("market", 0) / 100
        holding_details = []
        total_impact = 0.0
        for h in holdings:
            t = h.get("ticker", "")
            val = h.get("current_value", 0)
            meta = _get_holding_meta(t)
            beta = float(meta["beta"])
            sector = meta["sector"]
            # sector-specific shock or beta-scaled market shock
            if sector in shocks:
                shock_pct = shocks[sector] / 100
            else:
                shock_pct = market_shock * min(beta, 3.0)
            impact = val * shock_pct
            total_impact += impact
            holding_details.append({
                "ticker": t,
                "shock_pct": round(shock_pct * 100, 1),
                "impact_usd": round(impact, 2),
                "sector": sector,
                "beta": beta,
            })
        results[scenario] = {
            "portfolio_impact_pct": round(total_impact / total_value * 100, 2),
            "portfolio_impact_usd": round(total_impact, 2),
            "holdings": holding_details,
        }
    return results


def compute_var(holdings: list, confidence: float = 0.95, days: int = 1, period: str = "1y") -> dict:
    tickers = [h["ticker"] for h in holdings]
    values = {h["ticker"]: h.get("current_value", 0) for h in holdings}
    total_val = sum(values.values()) or 1
    try:
        prices = yf.download(tickers, period=period, auto_adjust=True, progress=False)
        if isinstance(prices.columns, pd.MultiIndex):
            closes = prices["Close"]
        else:
            closes = prices
        closes = closes.dropna(how="all")
        rets = closes.pct_change().dropna()
        weights = np.array([values.get(t, 0) / total_val for t in rets.columns])
        port_rets = rets.values @ weights
        scaled = port_rets * np.sqrt(days)
        var_pct = float(np.percentile(scaled, (1 - confidence) * 100))
        cvar_pct = float(scaled[scaled <= var_pct].mean()) if any(scaled <= var_pct) else var_pct
        return {
            "var_usd": round(var_pct * total_val, 2),
            "var_pct": round(var_pct * 100, 2),
            "cvar_usd": round(cvar_pct * total_val, 2),
            "cvar_pct": round(cvar_pct * 100, 2),
            "confidence": confidence,
            "days": days,
            "total_value": total_val,
        }
    except Exception:
        return {
            "var_usd": 0, "var_pct": 0,
            "cvar_usd": 0, "cvar_pct": 0,
            "confidence": confidence, "days": days, "total_value": total_val,
        }

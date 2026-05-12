import numpy as np
import streamlit as st
from utils.data import get_stock_data, compute_rsi, compute_momentum
from utils.config import SCORE_WEIGHTS, TIER1_MIN, TIER2_MIN, CACHE_TTL


def _score_val(info: dict) -> float:
    s = []
    pe = info.get("trailingPE") or 0
    if 0 < pe < 100:  s.append(max(0, min(10, 10 - pe / 5)))
    pb = info.get("priceToBook") or 0
    if 0 < pb < 50:   s.append(max(0, min(10, 10 - pb)))
    peg = info.get("pegRatio") or 0
    if 0 < peg < 10:  s.append(max(0, min(10, 10 - peg * 2)))
    ev = info.get("enterpriseToEbitda") or 0
    if 0 < ev < 100:  s.append(max(0, min(10, 10 - ev / 5)))
    return round(np.mean(s) if s else 5.0, 2)


def _score_growth(info: dict) -> float:
    s = []
    for key in ("revenueGrowth", "earningsGrowth", "earningsQuarterlyGrowth"):
        g = (info.get(key) or 0) * 100
        s.append(min(10, max(0, 5 + g / 10)))
    return round(np.mean(s), 2)


def _score_quality(info: dict) -> float:
    s = []
    roe = (info.get("returnOnEquity") or 0) * 100
    s.append(min(10, max(0, roe / 3)))
    pm = (info.get("profitMargins") or 0) * 100
    s.append(min(10, max(0, pm / 4)))
    cr = info.get("currentRatio") or 0
    if cr > 0: s.append(min(10, max(0, cr * 3)))
    de = info.get("debtToEquity") or 0
    if de >= 0: s.append(max(0, min(10, 10 - de / 20)))
    return round(np.mean(s) if s else 5.0, 2)


def _score_technical(hist, info) -> float:
    if hist is None or len(hist) < 5:
        return 5.0
    close = hist["Close"]
    price = close.iloc[-1]
    rsi   = compute_rsi(close)
    s = []
    if rsi < 30:   s.append(8.0)
    elif rsi < 50: s.append(7.0)
    elif rsi < 60: s.append(6.0)
    elif rsi < 70: s.append(4.0)
    else:          s.append(2.0)
    for window, sc_above, sc_below in [(20, 7, 3), (50, 7, 3), (200, 8, 2)]:
        if len(close) >= window:
            ma = close.rolling(window).mean().iloc[-1]
            s.append(sc_above if price > ma else sc_below)
    return round(np.mean(s), 2)


def _score_momentum(hist) -> float:
    if hist is None or len(hist) < 5:
        return 5.0
    mom = compute_momentum(hist)
    s = [min(10, max(0, 5 + v / 10)) for v in mom.values()]
    return round(np.mean(s), 2)


def _score_sentiment(info: dict) -> float:
    mapping = {"strong_buy": 9.5, "buy": 8.0, "hold": 5.0, "underperform": 3.0, "sell": 1.0}
    base = mapping.get(info.get("recommendationKey", ""), 5.0)
    n    = info.get("numberOfAnalystOpinions") or 0
    conf = min(1.0, n / 20)
    return round(5.0 + (base - 5.0) * conf, 2)


def score_stock(info: dict, hist) -> dict:
    v = _score_val(info)
    g = _score_growth(info)
    q = _score_quality(info)
    t = _score_technical(hist, info)
    m = _score_momentum(hist)
    s = _score_sentiment(info)
    w = SCORE_WEIGHTS
    composite = v*w["valuation"] + g*w["growth"] + q*w["quality"] + t*w["technical"] + m*w["momentum"] + s*w["sentiment"]
    if composite >= TIER1_MIN:
        tier, rec = 1, "BUY"
    elif composite >= TIER2_MIN:
        tier, rec = 2, "HOLD"
    else:
        tier, rec = 3, "AVOID"
    return {
        "composite": round(composite, 2), "tier": tier, "rec": rec,
        "valuation": v, "growth": g, "quality": q,
        "technical": t, "momentum": m, "sentiment": s,
    }


@st.cache_data(ttl=CACHE_TTL)
def run_screen(tickers: tuple, period: str = "1y") -> list:
    results = []
    for ticker in tickers:
        info, hist = get_stock_data(ticker, period)
        if info is None or hist is None or len(hist) == 0:
            continue
        scores = score_stock(info, hist)
        price  = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        prev   = info.get("previousClose", price) or price
        chg    = ((price - prev) / prev * 100) if prev else 0
        rsi    = compute_rsi(hist["Close"])
        mom    = compute_momentum(hist)
        results.append({
            "ticker":      ticker,
            "name":        info.get("shortName", ticker),
            "price":       round(price, 2),
            "change_pct":  round(chg, 2),
            "pe":          round(info.get("trailingPE") or 0, 2),
            "growth":      round((info.get("revenueGrowth") or 0) * 100, 1),
            "margin":      round((info.get("profitMargins") or 0) * 100, 1),
            "rsi":         round(rsi, 1),
            "trend":       "▲" if scores["momentum"] >= 6 else ("▼" if scores["momentum"] <= 4 else "→"),
            "sector":      info.get("sector", "N/A"),
            "mom_1m":      mom.get("1m", 0),
            "target":      info.get("targetMeanPrice", 0) or 0,
            **scores,
        })
    results.sort(key=lambda x: x["composite"], reverse=True)
    return results

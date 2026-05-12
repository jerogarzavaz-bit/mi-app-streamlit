import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from utils.config import CACHE_TTL, PERIOD_DAYS, MARKET_INDICES, SECTOR_ETFS


@st.cache_data(ttl=CACHE_TTL)
def get_stock_data(ticker: str, period: str = PERIOD_DAYS):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period=period)
        return info, hist
    except Exception:
        return None, None


@st.cache_data(ttl=CACHE_TTL)
def get_market_overview():
    result = {}
    for name, symbol in MARKET_INDICES.items():
        try:
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) >= 2:
                price = hist["Close"].iloc[-1]
                prev  = hist["Close"].iloc[-2]
                chg   = price - prev
                pct   = chg / prev * 100
            else:
                price, chg, pct = 0.0, 0.0, 0.0
            result[name] = {"price": price, "change": chg, "change_pct": pct, "symbol": symbol}
        except Exception:
            result[name] = {"price": 0.0, "change": 0.0, "change_pct": 0.0, "symbol": symbol}
    return result


@st.cache_data(ttl=CACHE_TTL)
def get_financial_statements(ticker: str):
    try:
        t = yf.Ticker(ticker)
        return {
            "income":    t.financials,
            "balance":   t.balance_sheet,
            "cashflow":  t.cashflow,
            "income_q":  t.quarterly_financials,
            "balance_q": t.quarterly_balance_sheet,
            "cash_q":    t.quarterly_cashflow,
            "info":      t.info,
        }
    except Exception:
        return None


@st.cache_data(ttl=CACHE_TTL)
def get_sector_performance(period: str = "1mo"):
    results = {}
    for sector, symbol in SECTOR_ETFS.items():
        try:
            hist = yf.Ticker(symbol).history(period=period)
            if len(hist) >= 2:
                ret = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
                results[sector] = round(ret, 2)
            else:
                results[sector] = 0.0
        except Exception:
            results[sector] = 0.0
    return results


@st.cache_data(ttl=CACHE_TTL)
def get_etf_data(tickers: tuple, period: str = "3y"):
    results = {}
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            hist = t.history(period=period)
            results[ticker] = {
                "info":         info,
                "hist":         hist,
                "name":         info.get("longName", ticker),
                "category":     info.get("category", "N/A"),
                "fund_family":  info.get("fundFamily", "N/A"),
                "aum":          info.get("totalAssets", 0),
                "expense_ratio":info.get("annualReportExpenseRatio", 0) or 0,
                "etf_yield":    info.get("yield", 0) or 0,
            }
        except Exception:
            pass
    return results


@st.cache_data(ttl=CACHE_TTL)
def get_earnings_calendar(tickers: tuple):
    results = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            cal = t.calendar
            info = t.info
            if cal is not None and not cal.empty:
                if "Earnings Date" in cal.index:
                    dates = cal.loc["Earnings Date"]
                    date_val = dates.iloc[0] if hasattr(dates, "iloc") else dates
                    results.append({
                        "ticker": ticker,
                        "name": info.get("shortName", ticker),
                        "earnings_date": pd.Timestamp(date_val),
                        "eps_estimate": cal.loc["EPS Estimate"].iloc[0] if "EPS Estimate" in cal.index else None,
                        "revenue_estimate": cal.loc["Revenue Estimate"].iloc[0] if "Revenue Estimate" in cal.index else None,
                    })
        except Exception:
            pass
    return results


def compute_rsi(series: pd.Series, period: int = 14) -> float:
    if len(series) < period + 1:
        return 50.0
    delta = series.diff().dropna()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - 100 / (1 + rs)
    val   = rsi.iloc[-1]
    return float(val) if not np.isnan(val) else 50.0


def compute_momentum(hist: pd.DataFrame) -> dict:
    close = hist["Close"]
    n = len(close)
    def ret(days):
        return (close.iloc[-1] / close.iloc[-days] - 1) * 100 if n > days else 0.0
    return {"1m": round(ret(21), 2), "3m": round(ret(63), 2),
            "6m": round(ret(126), 2), "1y": round(ret(252), 2)}


def compute_metrics(hist: pd.DataFrame, risk_free: float = 0.04) -> dict:
    if hist is None or len(hist) < 2:
        return {}
    rets = hist["Close"].pct_change().dropna()
    ann  = 252
    total_ret  = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
    vol        = rets.std() * np.sqrt(ann) * 100
    mean_ret   = rets.mean() * ann
    sharpe     = (mean_ret - risk_free) / (rets.std() * np.sqrt(ann) + 1e-9)
    neg        = rets[rets < 0]
    sortino    = (mean_ret - risk_free) / (neg.std() * np.sqrt(ann) + 1e-9) if len(neg) > 0 else 0
    roll_max   = hist["Close"].cummax()
    drawdown   = ((hist["Close"] - roll_max) / roll_max).min() * 100
    return {
        "total_ret": round(total_ret, 2),
        "vol": round(vol, 2),
        "sharpe": round(sharpe, 2),
        "sortino": round(sortino, 2),
        "max_dd": round(drawdown, 2),
    }

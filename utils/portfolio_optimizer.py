import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


@st.cache_data(ttl=3600)
def get_returns_data(tickers: tuple, period: str = "2y") -> pd.DataFrame:
    try:
        raw = yf.download(list(tickers), period=period, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            prices = raw["Close"]
        else:
            prices = raw[["Close"]] if "Close" in raw else raw
        prices = prices.dropna(how="all")
        return prices.pct_change().dropna()
    except Exception:
        return pd.DataFrame()


def portfolio_stats(weights: np.ndarray, returns: pd.DataFrame, risk_free: float = 0.045):
    w = np.array(weights)
    ann_ret = (returns.mean() * 252) @ w
    ann_vol = np.sqrt(w @ (returns.cov() * 252) @ w)
    sharpe = (ann_ret - risk_free) / (ann_vol + 1e-9)
    return float(ann_ret), float(ann_vol), float(sharpe)


def optimize_portfolio(tickers: list, period: str = "2y", risk_free: float = 0.045) -> dict:
    returns = get_returns_data(tuple(tickers), period)
    if returns.empty or len(returns.columns) < 2:
        return {}
    # keep only tickers that have data
    tickers = [t for t in tickers if t in returns.columns]
    returns = returns[tickers]
    n = len(tickers)

    # Monte Carlo: 5000 random portfolios
    mc_results = []
    for _ in range(5000):
        w = np.random.dirichlet(np.ones(n))
        r, v, s = portfolio_stats(w, returns, risk_free)
        mc_results.append({"weights": w, "return": r, "volatility": v, "sharpe": s})

    # Try scipy optimization for max Sharpe
    max_sharpe_w = max(mc_results, key=lambda x: x["sharpe"])["weights"]
    min_vol_w = min(mc_results, key=lambda x: x["volatility"])["weights"]
    eq_w = np.ones(n) / n

    try:
        from scipy.optimize import minimize
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
        bounds = [(0.01, 0.60)] * n

        res_sharpe = minimize(
            lambda w: -portfolio_stats(w, returns, risk_free)[2],
            eq_w, method="SLSQP", bounds=bounds, constraints=constraints,
        )
        if res_sharpe.success:
            max_sharpe_w = res_sharpe.x

        res_vol = minimize(
            lambda w: portfolio_stats(w, returns, risk_free)[1],
            eq_w, method="SLSQP", bounds=bounds, constraints=constraints,
        )
        if res_vol.success:
            min_vol_w = res_vol.x
    except ImportError:
        pass

    def fmt(w):
        r, v, s = portfolio_stats(w, returns, risk_free)
        return {
            "weights": {t: round(float(wi) * 100, 1) for t, wi in zip(tickers, w)},
            "return": round(r * 100, 2),
            "volatility": round(v * 100, 2),
            "sharpe": round(s, 3),
        }

    # Efficient frontier points (from MC)
    mc_results.sort(key=lambda x: x["volatility"])
    frontier = [
        {
            "volatility": round(x["volatility"] * 100, 2),
            "return": round(x["return"] * 100, 2),
            "sharpe": round(x["sharpe"], 2),
        }
        for x in mc_results[::50]
    ]

    return {
        "max_sharpe": fmt(max_sharpe_w),
        "min_volatility": fmt(min_vol_w),
        "equal_weight": fmt(eq_w),
        "efficient_frontier": frontier,
        "tickers": tickers,
        "monte_carlo": [
            {
                "v": round(x["volatility"] * 100, 2),
                "r": round(x["return"] * 100, 2),
                "s": round(x["sharpe"], 2),
            }
            for x in mc_results
        ],
    }

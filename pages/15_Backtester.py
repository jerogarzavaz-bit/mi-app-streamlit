import streamlit as st
import pandas as pd
import numpy as np
from utils.data import get_stock_data, compute_rsi
from utils.plots import backtest_chart

st.markdown("""
<div class='page-header'>
  <div class='page-title'>⚡ Strategy Backtester</div>
  <div class='page-subtitle'>Test technical trading strategies against historical price data</div>
</div>""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
ticker   = col1.text_input("Ticker", value="AAPL", placeholder="AAPL, NVDA…")
strategy = col2.selectbox("Strategy", [
    "RSI Mean Reversion",
    "Golden Cross (MA50 > MA200)",
    "Momentum (3-Month)",
    "Breakout (52W High)",
])
period   = col3.select_slider("Backtest Period", ["1Y","2Y","3Y","5Y"], value="3Y")

period_map = {"1Y":"1y","2Y":"2y","3Y":"3y","5Y":"5y"}

with st.expander("⚙️ Strategy Parameters"):
    if strategy == "RSI Mean Reversion":
        rsi_buy  = st.slider("RSI Buy Signal (oversold)", 10, 45, 30)
        rsi_sell = st.slider("RSI Sell Signal (overbought)", 55, 90, 70)
        rsi_period = st.slider("RSI Period", 5, 30, 14)
    elif "Golden Cross" in strategy:
        ma_fast = st.slider("Fast MA", 10, 100, 50)
        ma_slow = st.slider("Slow MA", 50, 300, 200)
    elif "Momentum" in strategy:
        mom_period = st.slider("Momentum Lookback (days)", 20, 120, 63)
    else:
        breakout_lookback = st.slider("Breakout Lookback (days)", 20, 252, 252)

run = st.button("▶ Run Backtest", type="primary", disabled=not ticker)

if not run:
    st.info("Configure a strategy above and click **Run Backtest**.")
    st.stop()

ticker = ticker.strip().upper()
with st.spinner(f"Running {strategy} backtest on {ticker}…"):
    info, hist = get_stock_data(ticker, period_map.get(period, "3y"))

if hist is None or len(hist) < 50:
    st.error("Not enough data for backtesting. Try a longer period or different ticker.")
    st.stop()

prices  = hist["Close"].copy().reset_index(drop=True)
dates   = hist.index
n       = len(prices)
initial = 10_000.0

# ── Strategy Logic ────────────────────────────────────────────────────────────
signals = pd.Series([0] * n)  # 1=buy, -1=sell, 0=hold

if strategy == "RSI Mean Reversion":
    for i in range(rsi_period + 1, n):
        rsi = compute_rsi(prices.iloc[:i+1], rsi_period)
        if rsi < rsi_buy:
            signals.iloc[i] = 1
        elif rsi > rsi_sell:
            signals.iloc[i] = -1

elif "Golden Cross" in strategy:
    for i in range(ma_slow, n):
        fast = prices.iloc[i-ma_fast:i].mean()
        slow = prices.iloc[i-ma_slow:i].mean()
        if fast > slow:
            signals.iloc[i] = 1
        else:
            signals.iloc[i] = -1

elif "Momentum" in strategy:
    for i in range(mom_period, n):
        ret = (prices.iloc[i] / prices.iloc[i - mom_period] - 1) * 100
        signals.iloc[i] = 1 if ret > 5 else (-1 if ret < -5 else 0)

elif "Breakout" in strategy:
    for i in range(breakout_lookback, n):
        high52 = prices.iloc[i-breakout_lookback:i].max()
        if prices.iloc[i] >= high52 * 0.99:
            signals.iloc[i] = 1
        else:
            signals.iloc[i] = 0

# ── Simulate Portfolio ────────────────────────────────────────────────────────
cash    = initial
shares  = 0.0
port    = []
trades  = []
position = False

for i in range(n):
    price = prices.iloc[i]
    if signals.iloc[i] == 1 and not position and cash > price:
        shares   = cash / price
        cash     = 0.0
        position = True
        trades.append({"type":"BUY","date":str(dates[i])[:10],"price":price,"shares":shares})
    elif signals.iloc[i] == -1 and position:
        cash     = shares * price
        shares   = 0.0
        position = False
        trades.append({"type":"SELL","date":str(dates[i])[:10],"price":price,"value":cash})
    port.append(cash + shares * price)

final_val  = port[-1]
total_ret  = (final_val / initial - 1) * 100
bnh_val    = initial * (prices.iloc[-1] / prices.iloc[0])
bnh_ret    = (bnh_val / initial - 1) * 100
port_arr   = np.array(port)
peak       = np.maximum.accumulate(port_arr)
drawdown   = ((port_arr - peak) / peak).min() * 100
daily_rets = np.diff(port_arr) / port_arr[:-1]
sharpe     = (daily_rets.mean() * 252 - 0.04) / (daily_rets.std() * np.sqrt(252) + 1e-9)

# ── Results ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Strategy Return",    f"{total_ret:+.2f}%")
c2.metric("Buy & Hold Return",  f"{bnh_ret:+.2f}%")
c3.metric("Alpha",              f"{total_ret - bnh_ret:+.2f}%")
c4.metric("Max Drawdown",       f"{drawdown:.2f}%")
c5.metric("Sharpe Ratio",       f"{sharpe:.2f}")

# Normalize to $10k
port_norm = [v / initial * 10_000 for v in port]
bnh_norm  = [initial * (p / prices.iloc[0]) / initial * 10_000 for p in prices]
st.plotly_chart(backtest_chart(dates, port_norm, bnh_norm, ticker), use_container_width=True)

# ── Trade Log ─────────────────────────────────────────────────────────────────
if trades:
    st.subheader(f"Trade Log ({len(trades)} trades)")
    st.dataframe(pd.DataFrame(trades), use_container_width=True, hide_index=True)
else:
    st.info("No trades executed. The strategy had no signals in this period.")

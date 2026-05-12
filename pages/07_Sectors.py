import streamlit as st
import pandas as pd
from utils.data import get_market_overview, get_sector_performance, get_stock_data
from utils.plots import sector_bar, multi_line
from utils.config import SECTOR_ETFS, COLOR_SUCCESS, COLOR_DANGER

st.markdown("""
<div class='page-header'>
  <div class='page-title'>🌐 Sectors &amp; Macro</div>
  <div class='page-subtitle'>Macro environment analysis + sector rotation signals</div>
</div>""", unsafe_allow_html=True)

# ── Market Dashboard ──────────────────────────────────────────────────────────
st.subheader("Market Dashboard")
with st.spinner("Loading market data…"):
    mkt = get_market_overview()

cols = st.columns(len(mkt))
for col, (name, d) in zip(cols, mkt.items()):
    pct = d["change_pct"]; arrow = "▲" if pct >= 0 else "▼"
    p = d["price"]
    fmt = f"${p:,.2f}" if name in ("Gold","Oil WTI") else f"{p:.2f}%" if "Yield" in name else f"{p:,.2f}"
    col.metric(name, fmt, f"{arrow} {abs(pct):.2f}%")

with st.expander("View Historical Chart"):
    idx_choice = st.selectbox("Index", list(mkt.keys()))
    symbol = mkt[idx_choice]["symbol"]
    _, hist = get_stock_data(symbol, "2y")
    if hist is not None and len(hist) > 0:
        import plotly.graph_objects as go
        from utils.plots import _DARK
        fig = go.Figure(go.Scatter(x=hist.index, y=hist["Close"], mode="lines",
            line=dict(color="#1f77b4", width=2)))
        fig.update_layout(**_DARK, title=f"{idx_choice} — 2 Year History", height=320)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Market Regime ─────────────────────────────────────────────────────────────
st.subheader("Market Regime Signal")
vix_val = mkt.get("VIX", {}).get("price", 20)
sp_chg  = mkt.get("S&P 500", {}).get("change_pct", 0)
yld_val = mkt.get("10Y Yield", {}).get("price", 4.5)

score = 0
factors = []
if vix_val < 18:  score += 1; factors.append(("VIX",        f"{vix_val:.1f}", "Low — bullish", True))
else:             factors.append(("VIX",        f"{vix_val:.1f}", "Elevated — caution", False))
if yld_val < 4.5: score += 1; factors.append(("10Y Yield",  f"{yld_val:.2f}%","Low — supportive", True))
else:             factors.append(("10Y Yield",  f"{yld_val:.2f}%","High — headwind", False))
if sp_chg > 0:    score += 1; factors.append(("S&P Trend",  f"{sp_chg:+.2f}%","Positive", True))
else:             factors.append(("S&P Trend",  f"{sp_chg:+.2f}%","Negative", False))

regime_color = "#2ca02c" if score >= 4 else "#FFA500" if score >= 2 else "#d62728"
regime_label = "Risk-On / Bullish" if score >= 4 else "Mixed / Cautious" if score >= 2 else "Risk-Off / Defensive"

st.markdown(f"""
<div class='card' style='border-color:{regime_color};'>
  <div style='font-size:1.4rem;font-weight:700;color:{regime_color};'>{regime_label}</div>
  <div style='color:#888;'>Score: {score} / 3 factors bullish</div>
</div>""", unsafe_allow_html=True)

fc = st.columns(len(factors))
for col, (name, val, desc, positive) in zip(fc, factors):
    col.metric(name, val, desc, delta_color="normal" if positive else "inverse")

st.divider()

# ── Sector ETF Performance ────────────────────────────────────────────────────
st.subheader("Sector ETF Performance")
period_map = {"1 Month": "1mo", "3 Months": "3mo", "1 Year": "1y"}
sel_period = st.radio("Heatmap Period", list(period_map.keys()), horizontal=True)

with st.spinner("Loading sector data…"):
    sector_ret = get_sector_performance(period_map[sel_period])

st.plotly_chart(sector_bar(sector_ret), use_container_width=True)

# ── Sector Rotation Chart ─────────────────────────────────────────────────────
st.divider()
st.subheader("Sector Rotation — Cumulative 1Y")

if st.button("Load Rotation Chart"):
    with st.spinner("Loading sector ETFs…"):
        etf_data = {}
        for sector, symbol in list(SECTOR_ETFS.items())[:8]:
            _, hist = get_stock_data(symbol, "1y")
            if hist is not None and len(hist) > 0:
                etf_data[sector] = hist
    if etf_data:
        st.plotly_chart(multi_line(etf_data, "Sector Rotation — Cumulative 1Y", normalize=True),
                        use_container_width=True)
    else:
        st.warning("Could not load sector data.")
else:
    st.info("Click **Load Rotation Chart** to render the 1-year cumulative sector chart.")

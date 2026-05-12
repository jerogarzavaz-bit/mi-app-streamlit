import streamlit as st
import pandas as pd
import numpy as np
from utils.data import get_etf_data, compute_metrics, get_stock_data
from utils.plots import multi_line, correlation_heatmap
from utils.ai import has_key, no_key_banner, chat

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📈 ETF Analysis</div>
  <div class='page-subtitle'>Institutional-grade ETF comparison: performance, risk metrics, correlations, and drawdowns</div>
</div>""", unsafe_allow_html=True)

# ── Configure ─────────────────────────────────────────────────────────────────
with st.expander("⚙️ Configure ETFs", expanded=True):
    raw = st.text_input("ETF Tickers (comma-separated)", value="SPY,QQQ,IWM,EFA,AGG")
    tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
    period  = st.select_slider("History Period", ["1y","2y","3y","5y"], value="3y")
    run_btn = st.button("🔍 Analyze", type="primary")

if not run_btn:
    st.info("Configure ETFs above and click **Analyze**.")
    st.stop()

with st.spinner(f"Loading {len(tickers)} ETFs…"):
    etfs = get_etf_data(tuple(tickers), period)

if not etfs:
    st.error("Could not load ETF data.")
    st.stop()

# ── Profile Cards ─────────────────────────────────────────────────────────────
st.subheader("ETF Profiles")
cols = st.columns(min(5, len(etfs)))
for col, (ticker, d) in zip(cols, etfs.items()):
    info = d["info"]
    aum  = d["aum"] or 0
    er   = d["expense_ratio"]
    col.markdown(f"""
    <div class='card'>
      <div style='font-size:20px;font-weight:700;color:white;'>{ticker}</div>
      <div style='font-size:11px;color:#888;margin-bottom:8px;'>{d['name'][:30]}</div>
      <div style='font-size:12px;color:#ccc;'><b>Category:</b> {d['category']}</div>
      <div style='font-size:12px;color:#ccc;'><b>Family:</b> {d['fund_family']}</div>
      <div style='font-size:12px;color:#ccc;'><b>AUM:</b> ${aum/1e9:.1f}B</div>
      <div style='font-size:12px;color:#ccc;'><b>Expense:</b> {er*100:.2f}%</div>
      <div style='font-size:12px;color:#ccc;'><b>Yield:</b> {d['etf_yield']*100:.2f}%</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Performance Chart ─────────────────────────────────────────────────────────
st.subheader("Performance — Indexed (100 = Start)")
hist_data = {t: d["hist"] for t, d in etfs.items() if len(d["hist"]) > 0}
if hist_data:
    st.plotly_chart(multi_line(hist_data, "ETF Performance Comparison", normalize=True),
                    use_container_width=True)

# ── Risk & Return Metrics ─────────────────────────────────────────────────────
st.divider()
st.subheader("Risk & Return Metrics")

_, spy_hist = get_stock_data("SPY", period)
spy_rets = spy_hist["Close"].pct_change().dropna() if spy_hist is not None else None

rows = []
for ticker, d in etfs.items():
    h = d["hist"]
    if len(h) < 5:
        continue
    m = compute_metrics(h)
    r = h["Close"].pct_change().dropna()

    # Period sub-returns
    def _ret(days):
        return ((h["Close"].iloc[-1] / h["Close"].iloc[-days] - 1) * 100
                if len(h) > days else np.nan)

    beta = np.nan
    if spy_rets is not None and len(r) > 20:
        aligned = pd.concat([r, spy_rets], axis=1).dropna()
        if len(aligned) > 5:
            cov  = aligned.iloc[:,0].cov(aligned.iloc[:,1])
            var  = aligned.iloc[:,1].var()
            beta = round(cov / var, 2) if var else np.nan

    rows.append({
        "ETF":          ticker,
        "1Y Ret %":     round(_ret(252), 2),
        "3Y Ret %":     round(_ret(756), 2),
        "Volatility %": m.get("vol", np.nan),
        "Sharpe":       m.get("sharpe", np.nan),
        "Sortino":      m.get("sortino", np.nan),
        "Max DD %":     m.get("max_dd", np.nan),
        "Beta vs SPY":  beta,
    })

if rows:
    df_risk = pd.DataFrame(rows)
    st.dataframe(df_risk, use_container_width=True, hide_index=True,
        column_config={
            "1Y Ret %":     st.column_config.NumberColumn(format="%.2f%%"),
            "3Y Ret %":     st.column_config.NumberColumn(format="%.2f%%"),
            "Volatility %": st.column_config.NumberColumn(format="%.2f%%"),
            "Max DD %":     st.column_config.NumberColumn(format="%.2f%%"),
        })

# ── Correlation Heatmap ───────────────────────────────────────────────────────
st.divider()
st.subheader("Return Correlation Heatmap")
if len(etfs) >= 2:
    rets_df = pd.DataFrame({t: d["hist"]["Close"].pct_change().dropna()
                             for t, d in etfs.items() if len(d["hist"]) > 5})
    corr = rets_df.corr()
    st.plotly_chart(correlation_heatmap(corr), use_container_width=True)

# ── AI Analysis ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("🤖 AI ETF Analysis")
if not has_key():
    no_key_banner("ETF AI analysis")
else:
    if st.button("Generate AI Comparison", type="primary"):
        summary = "\n".join(f"{r['ETF']}: 1Y={r['1Y Ret %']:.1f}%, Vol={r['Volatility %']:.1f}%, Sharpe={r['Sharpe']:.2f}, MaxDD={r['Max DD %']:.1f}%"
                            for r in rows)
        prompt = f"Compare these ETFs for a diversified portfolio:\n{summary}\n\nProvide: 1) Best risk-adjusted choice 2) Best for aggressive growth 3) Best for conservative allocation 4) Diversification recommendation 5) Hidden risks in any of these ETFs."
        with st.spinner("Analyzing…"):
            resp = chat([{"role": "user", "content": prompt}])
        if resp:
            st.markdown(resp)

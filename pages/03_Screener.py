import streamlit as st
import pandas as pd
from utils.screener import run_screen
from utils.plots import screener_bar, radar_chart
from utils.config import TICKERS_US, TICKERS_MX, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER

st.markdown("""
<div class='page-header'>
  <div class='page-title'>🔍 Stock Screener</div>
  <div class='page-subtitle'>Rank stocks across 6 dimensions: Valuation · Growth · Quality · Technical · Momentum · Sentiment</div>
</div>""", unsafe_allow_html=True)

# ── Market Selection ──────────────────────────────────────────────────────────
market = st.radio("Market", ["United States (NYSE / NASDAQ)", "México (BMV)", "Both Markets"],
                  horizontal=True)

if market == "United States (NYSE / NASDAQ)":
    default_tickers = TICKERS_US
elif market == "México (BMV)":
    default_tickers = TICKERS_MX
else:
    default_tickers = TICKERS_US + TICKERS_MX

# ── Watchlist Config ──────────────────────────────────────────────────────────
with st.expander("⚙️ Configure Watchlist", expanded=True):
    raw = st.text_area("Tickers (comma-separated)",
        value=", ".join(default_tickers), height=80)
    tickers = [t.strip().upper() for t in raw.replace("\n", ",").split(",") if t.strip()]

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Clear"):
            tickers = []
    with col2:
        # Quick screen from saved watchlists
        wls = st.session_state.get("watchlists", {})
        wl_names = list(wls.keys())
        if wl_names:
            sel = st.selectbox("Load saved watchlist:", ["— none —"] + wl_names)
            if sel != "— none —" and st.button("Load"):
                tickers = wls[sel]

    # Save
    wl_name = st.text_input("Name this watchlist…", key="wl_name_input")
    if st.button("💾 Save current tickers") and wl_name:
        wls[wl_name] = tickers
        st.session_state.watchlists = wls
        st.success(f"Watchlist '{wl_name}' saved!")

# ── Pre-Screen Filters ────────────────────────────────────────────────────────
with st.expander("🔧 Pre-Screen Filters"):
    fc1, fc2, fc3 = st.columns(3)
    pe_max    = fc1.number_input("Max P/E",            value=100.0, step=5.0)
    rev_min   = fc2.number_input("Min Revenue Growth %", value=-50.0, step=5.0)
    margin_min= fc3.number_input("Min Profit Margin %",  value=-100.0, step=5.0)

# ── Run ────────────────────────────────────────────────────────────────────────
run = st.button("▶ Run Screen", type="primary", disabled=not tickers)

if run and tickers:
    with st.spinner(f"Screening {len(tickers)} stocks…"):
        period = st.session_state.get("period", "1y")
        results = run_screen(tuple(tickers), period)

    # Apply filters
    results = [r for r in results
               if (r["pe"] == 0 or r["pe"] <= pe_max)
               and r["growth"] >= rev_min
               and r["margin"] >= margin_min]

    if not results:
        st.warning("No stocks passed the filters.")
        st.stop()

    # Save to history
    from datetime import date
    st.session_state.screen_history.append({
        "date": date.today().isoformat(),
        "tickers": tickers,
        "count": len(results),
    })

    df = pd.DataFrame(results)
    t1 = df[df.tier == 1]; t2 = df[df.tier == 2]; t3 = df[df.tier == 3]

    # ── Metric Cards ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stocks Screened", len(results))
    c2.metric("Tier 1 — BUY",  len(t1), delta=None)
    c3.metric("Tier 2 — HOLD", len(t2), delta=None)
    c4.metric("Tier 3 — AVOID",len(t3), delta=None)

    # ── Charts ────────────────────────────────────────────────────────────────
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(screener_bar(df), use_container_width=True)
    with col_r:
        st.plotly_chart(radar_chart(df), use_container_width=True)

    # ── Results Table ─────────────────────────────────────────────────────────
    st.subheader("Detailed Results")

    tab_all, tab1, tab2, tab3 = st.tabs(["All Results", "Tier 1 — BUY", "Tier 2 — HOLD", "Tier 3 — AVOID"])

    def _render_table(frame, tab):
        if frame.empty:
            tab.info("No stocks in this tier.")
            return
        display = frame[["ticker","name","composite","rec","price","change_pct",
                          "pe","growth","margin","rsi","trend","sector"]].copy()
        display.columns = ["Ticker","Name","Score","Rec","Price","Chg%","P/E","Growth%","Margin%","RSI","Trend","Sector"]
        tab.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Price":   st.column_config.NumberColumn(format="$%.2f"),
                "Chg%":    st.column_config.NumberColumn(format="%.2f%%"),
                "Score":   st.column_config.ProgressColumn(min_value=0, max_value=10, format="%.1f"),
            },
        )
        for _, row in frame.iterrows():
            if tab.button(f"📊 Analyze {row['ticker']}", key=f"analyze_{row['ticker']}_{tab}"):
                st.session_state.analyze_ticker = row["ticker"]
                st.switch_page("pages/04_Analysis.py")

    with tab_all: _render_table(df,  tab_all)
    with tab1:    _render_table(t1,  tab1)
    with tab2:    _render_table(t2,  tab2)
    with tab3:    _render_table(t3,  tab3)

    # ── Sector Leaders ────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Sector Leaders")
    sector_best = {}
    for r in results:
        s = r["sector"]
        if s not in sector_best or r["composite"] > sector_best[s]["composite"]:
            sector_best[s] = r

    if sector_best:
        leaders = list(sector_best.values())[:6]
        cols = st.columns(min(3, len(leaders)))
        for i, r in enumerate(leaders):
            with cols[i % 3]:
                tier_color = COLOR_SUCCESS if r["tier"] == 1 else COLOR_WARNING if r["tier"] == 2 else COLOR_DANGER
                st.markdown(f"""
                <div class='card'>
                  <div style='color:#888;font-size:11px;text-transform:uppercase;'>{r['sector']}</div>
                  <div style='font-size:22px;font-weight:700;color:white;margin:4px 0;'>{r['ticker']}</div>
                  <div style='color:#ccc;font-size:13px;margin-bottom:8px;'>{r['name']}</div>
                  <div style='font-size:20px;font-weight:700;color:{tier_color};'>{r['composite']:.1f}/10</div>
                  <div style='color:{tier_color};font-weight:600;font-size:13px;'>{r['rec']}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("Analyze", key=f"leader_{r['ticker']}"):
                    st.session_state.analyze_ticker = r["ticker"]
                    st.switch_page("pages/04_Analysis.py")

else:
    if not run:
        st.info("Configure your watchlist above and click **Run Screen** to start.")

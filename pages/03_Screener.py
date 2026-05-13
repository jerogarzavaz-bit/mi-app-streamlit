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

# ── Market Selection ───────────────────────────────────────────────────────────
market = st.radio("Market", ["United States (NYSE / NASDAQ)", "México (BMV)", "Both Markets"],
                  horizontal=True)

if market == "United States (NYSE / NASDAQ)":
    default_tickers = TICKERS_US
elif market == "México (BMV)":
    default_tickers = TICKERS_MX
else:
    default_tickers = TICKERS_US + TICKERS_MX

# ── Watchlist Config ───────────────────────────────────────────────────────────
with st.expander("⚙️ Configure Watchlist", expanded=True):
    raw = st.text_area("Tickers (comma-separated)",
        value=", ".join(default_tickers), height=80)
    tickers = [t.strip().upper() for t in raw.replace("\n", ",").split(",") if t.strip()]

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Clear"):
            tickers = []
    with col2:
        wls = st.session_state.get("watchlists", {})
        wl_names = list(wls.keys())
        if wl_names:
            sel = st.selectbox("Load saved watchlist:", ["— none —"] + wl_names)
            if sel != "— none —" and st.button("Load"):
                tickers = wls[sel]

    wl_name = st.text_input("Name this watchlist…", key="wl_name_input")
    if st.button("💾 Save current tickers") and wl_name:
        wls[wl_name] = tickers
        st.session_state.watchlists = wls
        st.success(f"Watchlist '{wl_name}' saved!")

# ── Pre-Screen Filters ─────────────────────────────────────────────────────────
with st.expander("🔧 Pre-Screen Filters"):
    fc1, fc2, fc3 = st.columns(3)
    pe_max     = fc1.number_input("Max P/E",              value=100.0, step=5.0)
    rev_min    = fc2.number_input("Min Revenue Growth %", value=-50.0, step=5.0)
    margin_min = fc3.number_input("Min Profit Margin %",  value=-100.0, step=5.0)

# ── Run ────────────────────────────────────────────────────────────────────────
run = st.button("▶ Run Screen", type="primary", disabled=not tickers)

if run and tickers:
    with st.spinner(f"Screening {len(tickers)} stocks…"):
        period  = st.session_state.get("period", "1y")
        results = run_screen(tuple(tickers), period)

    results = [r for r in results
               if (r["pe"] == 0 or r["pe"] <= pe_max)
               and r["growth"] >= rev_min
               and r["margin"] >= margin_min]

    if not results:
        st.warning("No stocks passed the filters.")
        st.stop()

    from datetime import date
    st.session_state.screen_history.append({
        "date":    date.today().isoformat(),
        "tickers": tickers,
        "count":   len(results),
    })

    df = pd.DataFrame(results)
    t1 = df[df.tier == 1]
    t2 = df[df.tier == 2]
    t3 = df[df.tier == 3]

    # ── Summary Metrics ────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stocks Screened", len(results))
    c2.metric("Tier 1 — BUY",   len(t1))
    c3.metric("Tier 2 — HOLD",  len(t2))
    c4.metric("Tier 3 — AVOID", len(t3))

    # ── Charts ─────────────────────────────────────────────────────────────────
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(screener_bar(df), use_container_width=True)
    with col_r:
        st.plotly_chart(radar_chart(df), use_container_width=True)

    st.divider()

    # ── Results — card rows ────────────────────────────────────────────────────
    st.subheader("Detailed Results")

    view = st.radio("View", ["Cards", "Table"], horizontal=True, label_visibility="collapsed")
    filter_tier = st.radio("Filter", ["All", "Tier 1 — BUY", "Tier 2 — HOLD", "Tier 3 — AVOID"],
                            horizontal=True)

    show_df = df
    if filter_tier == "Tier 1 — BUY":   show_df = t1
    elif filter_tier == "Tier 2 — HOLD": show_df = t2
    elif filter_tier == "Tier 3 — AVOID":show_df = t3

    if view == "Cards":
        for _, row in show_df.iterrows():
            tier_color = COLOR_SUCCESS if row["tier"] == 1 else COLOR_WARNING if row["tier"] == 2 else COLOR_DANGER
            tier_label = "BUY" if row["tier"] == 1 else "HOLD" if row["tier"] == 2 else "AVOID"
            tier_bg    = ("rgba(34,197,94,0.07)" if row["tier"] == 1
                          else "rgba(245,158,11,0.07)" if row["tier"] == 2
                          else "rgba(239,68,68,0.07)")
            bar_w = int((row["composite"] or 0) / 10 * 100)
            chg_color = "#22c55e" if (row.get("change_pct") or 0) >= 0 else "#ef4444"
            chg_arrow = "▲" if (row.get("change_pct") or 0) >= 0 else "▼"

            c_main, c_btn = st.columns([10, 1])
            with c_main:
                st.markdown(f"""
                <div class='card' style='padding:14px 20px;margin-bottom:6px;border-left:3px solid {tier_color};background:{tier_bg};'>
                  <div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
                    <div style='min-width:80px;'>
                      <div style='font-size:18px;font-weight:800;color:#c8d8f0;'>{row["ticker"]}</div>
                      <div style='font-size:11px;color:#4a6a8a;white-space:nowrap;overflow:hidden;max-width:140px;text-overflow:ellipsis;'>{row.get("name","")}</div>
                    </div>
                    <div style='min-width:90px;'>
                      <div style='font-size:22px;font-weight:800;color:{tier_color};'>{row["composite"]:.1f}<span style='font-size:12px;color:#4a6a8a;'>/10</span></div>
                      <div style='background:rgba(255,255,255,0.05);border-radius:4px;height:4px;width:80px;margin-top:3px;overflow:hidden;'>
                        <div style='width:{bar_w}%;height:100%;background:{tier_color};border-radius:4px;'></div>
                      </div>
                    </div>
                    <div>
                      <span style='background:rgba(0,0,0,0.3);border:1px solid {tier_color}55;color:{tier_color};font-size:11px;font-weight:700;padding:2px 10px;border-radius:20px;'>{tier_label}</span>
                    </div>
                    <div style='min-width:80px;'>
                      <div style='font-size:14px;font-weight:600;color:#c8d8f0;'>${row.get("price",0):.2f}</div>
                      <div style='font-size:11px;color:{chg_color};'>{chg_arrow} {abs(row.get("change_pct",0)):.2f}%</div>
                    </div>
                    <div style='display:flex;gap:20px;flex-wrap:wrap;'>
                      <div style='text-align:center;'>
                        <div style='font-size:10px;color:#4a6a8a;letter-spacing:0.5px;'>P/E</div>
                        <div style='font-size:12px;font-weight:600;color:#8aadcc;'>{row.get("pe",0) or "—"}</div>
                      </div>
                      <div style='text-align:center;'>
                        <div style='font-size:10px;color:#4a6a8a;letter-spacing:0.5px;'>GROWTH</div>
                        <div style='font-size:12px;font-weight:600;color:#8aadcc;'>{row.get("growth",0):.1f}%</div>
                      </div>
                      <div style='text-align:center;'>
                        <div style='font-size:10px;color:#4a6a8a;letter-spacing:0.5px;'>MARGIN</div>
                        <div style='font-size:12px;font-weight:600;color:#8aadcc;'>{row.get("margin",0):.1f}%</div>
                      </div>
                      <div style='text-align:center;'>
                        <div style='font-size:10px;color:#4a6a8a;letter-spacing:0.5px;'>RSI</div>
                        <div style='font-size:12px;font-weight:600;color:#8aadcc;'>{row.get("rsi",0):.0f}</div>
                      </div>
                      <div style='text-align:center;'>
                        <div style='font-size:10px;color:#4a6a8a;letter-spacing:0.5px;'>SECTOR</div>
                        <div style='font-size:12px;font-weight:600;color:#8aadcc;'>{(row.get("sector","") or "")[:14]}</div>
                      </div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
            with c_btn:
                if st.button("📊", key=f"analyze_{row['ticker']}", help=f"Analyze {row['ticker']}"):
                    st.session_state.analyze_ticker = row["ticker"]
                    st.switch_page("pages/04_Analysis.py")
    else:
        display = show_df[["ticker","name","composite","rec","price","change_pct",
                            "pe","growth","margin","rsi","trend","sector"]].copy()
        display.columns = ["Ticker","Name","Score","Rec","Price","Chg%","P/E","Growth%","Margin%","RSI","Trend","Sector"]
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Price":  st.column_config.NumberColumn(format="$%.2f"),
                "Chg%":   st.column_config.NumberColumn(format="%.2f%%"),
                "Score":  st.column_config.ProgressColumn(min_value=0, max_value=10, format="%.1f"),
            },
        )
        for _, row in show_df.iterrows():
            if st.button(f"📊 Analyze {row['ticker']}", key=f"tbl_{row['ticker']}"):
                st.session_state.analyze_ticker = row["ticker"]
                st.switch_page("pages/04_Analysis.py")

    # ── Sector Leaders ─────────────────────────────────────────────────────────
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
            tier_color = COLOR_SUCCESS if r["tier"] == 1 else COLOR_WARNING if r["tier"] == 2 else COLOR_DANGER
            with cols[i % 3]:
                st.markdown(f"""
                <div class='card'>
                  <div style='color:#4a6a8a;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;'>{r['sector']}</div>
                  <div style='font-size:22px;font-weight:800;color:#c8d8f0;margin:2px 0;'>{r['ticker']}</div>
                  <div style='color:#6a8aaa;font-size:12px;margin-bottom:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{r['name']}</div>
                  <div style='font-size:24px;font-weight:800;color:{tier_color};'>{r['composite']:.1f}<span style='font-size:12px;color:#4a6a8a;'>/10</span></div>
                  <div style='color:{tier_color};font-weight:700;font-size:12px;margin-top:2px;'>{r['rec']}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("Analyze →", key=f"leader_{r['ticker']}"):
                    st.session_state.analyze_ticker = r["ticker"]
                    st.switch_page("pages/04_Analysis.py")

else:
    if not run:
        st.info("Configure your watchlist above and click **▶ Run Screen** to start.")

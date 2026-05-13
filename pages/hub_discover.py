import streamlit as st
import pandas as pd
from utils.config import TICKERS_US, TICKERS_MX, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER

st.markdown("""
<div class='page-header'>
  <div class='page-title'>🔭 Discover</div>
  <div class='page-subtitle'>Screener · ETF Analysis · Sectors · AI Picks</div>
</div>""", unsafe_allow_html=True)

tab_screen, tab_etf, tab_sectors, tab_picks, tab_inst, tab_crypto = st.tabs([
    "🔍 Screener", "📈 ETF Analysis", "🌐 Sectors & Macro", "⭐ AI Picks", "🏛️ Institutional", "₿ Crypto"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SCREENER
# ══════════════════════════════════════════════════════════════════════════════
with tab_screen:
    from utils.screener import run_screen
    from utils.plots import screener_bar, radar_chart

    market = st.radio("Market", ["United States (NYSE / NASDAQ)", "México (BMV)", "Both Markets"],
                      horizontal=True, key="disc_market")
    if market == "United States (NYSE / NASDAQ)":
        default_tickers = TICKERS_US
    elif market == "México (BMV)":
        default_tickers = TICKERS_MX
    else:
        default_tickers = TICKERS_US + TICKERS_MX

    override = st.session_state.pop("screener_tickers_override", None)
    if override:
        default_tickers = override

    with st.expander("⚙️ Configure Watchlist", expanded=True):
        raw = st.text_area("Tickers (comma-separated)",
                           value=", ".join(default_tickers), height=80, key="disc_tickers_raw")
        tickers = [t.strip().upper() for t in raw.replace("\n", ",").split(",") if t.strip()]

        col1, col2 = st.columns([1, 3])
        with col2:
            wls = st.session_state.get("watchlists", {})
            wl_names = list(wls.keys())
            if wl_names:
                sel_wl = st.selectbox("Load saved watchlist:", ["— none —"] + wl_names, key="disc_wl_sel")
                if sel_wl != "— none —" and st.button("Load", key="disc_wl_load"):
                    tickers = wls[sel_wl]

    with st.expander("🔧 Pre-Screen Filters"):
        fc1, fc2, fc3 = st.columns(3)
        pe_max     = fc1.number_input("Max P/E",              value=100.0, step=5.0,   key="disc_pe")
        rev_min    = fc2.number_input("Min Revenue Growth %", value=-50.0, step=5.0,   key="disc_rev")
        margin_min = fc3.number_input("Min Profit Margin %",  value=-100.0, step=5.0,  key="disc_margin")

    run = st.button("▶ Run Screen", type="primary", disabled=not tickers, key="disc_run")

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
        else:
            from datetime import date
            st.session_state.screen_history.append({"date": date.today().isoformat(),
                                                     "tickers": tickers, "count": len(results)})
            df = pd.DataFrame(results).sort_values("composite", ascending=False).reset_index(drop=True)
            t1 = df[df.tier == 1]; t2 = df[df.tier == 2]; t3 = df[df.tier == 3]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Screened", len(results))
            c2.metric("Tier 1 — BUY",   len(t1))
            c3.metric("Tier 2 — HOLD",  len(t2))
            c4.metric("Tier 3 — AVOID", len(t3))

            col_l, col_r = st.columns(2)
            with col_l: st.plotly_chart(screener_bar(df), use_container_width=True)
            with col_r: st.plotly_chart(radar_chart(df),  use_container_width=True)

            st.divider()
            view = st.radio("View", ["Cards", "Table"], horizontal=True, key="disc_view",
                            label_visibility="collapsed")
            filter_tier = st.radio("Filter", ["All", "Tier 1 — BUY", "Tier 2 — HOLD", "Tier 3 — AVOID"],
                                   horizontal=True, key="disc_tier_filter")
            show_df = (t1 if filter_tier == "Tier 1 — BUY" else
                       t2 if filter_tier == "Tier 2 — HOLD" else
                       t3 if filter_tier == "Tier 3 — AVOID" else df)

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
                            <span style='background:rgba(0,0,0,0.3);border:1px solid {tier_color}55;color:{tier_color};font-size:11px;font-weight:700;padding:2px 10px;border-radius:20px;'>{tier_label}</span>
                            <div>
                              <div style='font-size:14px;font-weight:600;color:#c8d8f0;'>${row.get("price",0):.2f}</div>
                              <div style='font-size:11px;color:{chg_color};'>{chg_arrow} {abs(row.get("change_pct",0)):.2f}%</div>
                            </div>
                            <div style='display:flex;gap:20px;flex-wrap:wrap;'>
                              <div style='text-align:center;'><div style='font-size:10px;color:#4a6a8a;'>P/E</div><div style='font-size:12px;font-weight:600;color:#8aadcc;'>{row.get("pe",0) or "—"}</div></div>
                              <div style='text-align:center;'><div style='font-size:10px;color:#4a6a8a;'>GROWTH</div><div style='font-size:12px;font-weight:600;color:#8aadcc;'>{row.get("growth",0):.1f}%</div></div>
                              <div style='text-align:center;'><div style='font-size:10px;color:#4a6a8a;'>MARGIN</div><div style='font-size:12px;font-weight:600;color:#8aadcc;'>{row.get("margin",0):.1f}%</div></div>
                              <div style='text-align:center;'><div style='font-size:10px;color:#4a6a8a;'>RSI</div><div style='font-size:12px;font-weight:600;color:#8aadcc;'>{row.get("rsi",0):.0f}</div></div>
                            </div>
                          </div>
                        </div>""", unsafe_allow_html=True)
                    with c_btn:
                        if st.button("📊", key=f"disc_analyze_{row['ticker']}"):
                            st.session_state.analyze_ticker = row["ticker"]
                            st.switch_page("pages/hub_ai.py")
            else:
                display = show_df[["ticker","name","composite","rec","price","change_pct",
                                   "pe","growth","margin","rsi","sector"]].copy()
                display.columns = ["Ticker","Name","Score","Rec","Price","Chg%","P/E","Growth%","Margin%","RSI","Sector"]
                st.dataframe(display, use_container_width=True, hide_index=True,
                             column_config={"Price": st.column_config.NumberColumn(format="$%.2f"),
                                            "Chg%": st.column_config.NumberColumn(format="%.2f%%"),
                                            "Score": st.column_config.ProgressColumn(min_value=0, max_value=10, format="%.1f")})
    else:
        if not run:
            st.info("Configure your watchlist above and click **▶ Run Screen** to start.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ETF ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_etf:
    from utils.data import get_etf_data, compute_metrics, get_stock_data
    from utils.plots import multi_line, correlation_heatmap
    from utils.ai import has_key, no_key_banner, chat
    import numpy as np

    with st.expander("⚙️ Configure ETFs", expanded=True):
        raw_etf = st.text_input("ETF Tickers (comma-separated)", value="SPY,QQQ,IWM,EFA,AGG", key="disc_etf_raw")
        etf_tickers = [t.strip().upper() for t in raw_etf.split(",") if t.strip()]
        etf_period  = st.select_slider("History", ["1y","2y","3y","5y"], value="3y", key="disc_etf_period")
        etf_run = st.button("🔍 Analyze ETFs", type="primary", key="disc_etf_run")

    if not etf_run:
        st.info("Configure ETFs above and click **Analyze ETFs**.")
    else:
        with st.spinner(f"Loading {len(etf_tickers)} ETFs…"):
            etfs = get_etf_data(tuple(etf_tickers), etf_period)

        if not etfs:
            st.error("Could not load ETF data.")
        else:
            st.subheader("ETF Profiles")
            cols = st.columns(min(5, len(etfs)))
            for col, (ticker, d) in zip(cols, etfs.items()):
                aum = d["aum"] or 0
                er  = d["expense_ratio"]
                col.markdown(f"""
                <div class='card'>
                  <div style='font-size:20px;font-weight:700;color:white;'>{ticker}</div>
                  <div style='font-size:11px;color:#888;margin-bottom:8px;'>{d['name'][:30]}</div>
                  <div style='font-size:12px;color:#ccc;'><b>AUM:</b> ${aum/1e9:.1f}B</div>
                  <div style='font-size:12px;color:#ccc;'><b>Expense:</b> {er*100:.2f}%</div>
                  <div style='font-size:12px;color:#ccc;'><b>Yield:</b> {d['etf_yield']*100:.2f}%</div>
                </div>""", unsafe_allow_html=True)

            st.divider()
            st.subheader("Performance — Indexed (100 = Start)")
            hist_data = {t: d["hist"] for t, d in etfs.items() if len(d["hist"]) > 0}
            if hist_data:
                st.plotly_chart(multi_line(hist_data, "ETF Performance Comparison", normalize=True),
                                use_container_width=True)

            st.divider()
            st.subheader("Risk & Return Metrics")
            _, spy_hist = get_stock_data("SPY", etf_period)
            spy_rets = spy_hist["Close"].pct_change().dropna() if spy_hist is not None else None
            rows = []
            for ticker, d in etfs.items():
                h = d["hist"]
                if len(h) < 5: continue
                m = compute_metrics(h)
                r = h["Close"].pct_change().dropna()
                def _ret(days):
                    return ((h["Close"].iloc[-1] / h["Close"].iloc[-days] - 1) * 100 if len(h) > days else np.nan)
                beta = np.nan
                if spy_rets is not None and len(r) > 20:
                    aligned = r.align(spy_rets, join="inner")
                    if len(aligned[0]) > 20:
                        cov = np.cov(aligned[0], aligned[1])
                        beta = cov[0, 1] / cov[1, 1] if cov[1, 1] != 0 else np.nan
                rows.append({"ETF": ticker, "1M %": round(_ret(21), 2), "3M %": round(_ret(63), 2),
                             "1Y %": round(_ret(252), 2), "Ann Vol %": round(m.get("volatility", 0)*100, 2),
                             "Max DD %": round(m.get("max_drawdown", 0)*100, 2),
                             "Sharpe": round(m.get("sharpe", 0), 2), "Beta": round(beta, 2) if not np.isnan(beta) else "—"})
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            if len(hist_data) >= 2 and st.checkbox("Show Correlation Heatmap", key="disc_etf_corr"):
                closes = pd.DataFrame({t: h["Close"] for t, h in hist_data.items()}).dropna()
                if len(closes) > 1:
                    st.plotly_chart(correlation_heatmap(closes.pct_change().dropna().corr()),
                                    use_container_width=True)

            if has_key():
                if st.button("🤖 AI ETF Commentary", key="disc_etf_ai"):
                    summary = "\n".join(f"{t}: YTD={d.get('ytd_ret',0)*100:.1f}%, Expense={d['expense_ratio']*100:.2f}%"
                                        for t, d in etfs.items())
                    with st.spinner("Generating commentary…"):
                        resp = chat([{"role": "user", "content": f"Briefly compare these ETFs for a long-term portfolio:\n{summary}"}])
                    if resp: st.markdown(resp)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SECTORS & MACRO
# ══════════════════════════════════════════════════════════════════════════════
with tab_sectors:
    from utils.data import get_market_overview, get_sector_performance, get_stock_data
    from utils.plots import sector_bar
    from utils.config import SECTOR_ETFS

    with st.spinner("Loading market data…"):
        mkt = get_market_overview()

    cols = st.columns(len(mkt))
    for col, (name, d) in zip(cols, mkt.items()):
        pct = d["change_pct"]; arrow = "▲" if pct >= 0 else "▼"
        p = d["price"]
        fmt = f"${p:,.2f}" if name in ("Gold","Oil WTI") else f"{p:.2f}%" if "Yield" in name else f"{p:,.2f}"
        col.metric(name, fmt, f"{arrow} {abs(pct):.2f}%")

    st.divider()
    st.subheader("Market Regime Signal")
    vix_val = mkt.get("VIX", {}).get("price", 20)
    sp_chg  = mkt.get("S&P 500", {}).get("change_pct", 0)
    yld_val = mkt.get("10Y Yield", {}).get("price", 4.5)
    score   = sum([vix_val < 18, yld_val < 4.5, sp_chg > 0])
    regime_color = "#2ca02c" if score >= 3 else "#FFA500" if score >= 2 else "#d62728"
    regime_label = "Risk-On / Bullish" if score >= 3 else "Mixed / Cautious" if score >= 2 else "Risk-Off / Defensive"
    st.markdown(f"""
    <div class='card' style='border-left:3px solid {regime_color};padding:16px 20px;'>
      <div style='font-size:1.2rem;font-weight:700;color:{regime_color};margin-bottom:4px;'>{regime_label}</div>
      <div style='display:flex;gap:24px;margin-top:8px;'>
        <span style='font-size:12px;color:#8aadcc;'>VIX: <strong>{vix_val:.1f}</strong> {"✓" if vix_val < 18 else "⚠"}</span>
        <span style='font-size:12px;color:#8aadcc;'>10Y Yield: <strong>{yld_val:.2f}%</strong> {"✓" if yld_val < 4.5 else "⚠"}</span>
        <span style='font-size:12px;color:#8aadcc;'>S&P Trend: <strong>{sp_chg:+.2f}%</strong> {"✓" if sp_chg > 0 else "⚠"}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("Sector Performance")
    with st.spinner("Loading sector data…"):
        sector_data = get_sector_performance()

    if sector_data:
        st.plotly_chart(sector_bar(sector_data), use_container_width=True)
        sec_cols = st.columns(min(4, len(sector_data)))
        for col, (sec, pct) in zip(sec_cols * 10, sector_data.items()):
            pct = pct if isinstance(pct, (int, float)) else 0
            color = COLOR_SUCCESS if pct >= 0 else COLOR_DANGER
            col.markdown(f"""
            <div class='card' style='text-align:center;padding:12px;'>
              <div style='font-size:11px;color:#4a6a8a;'>{sec}</div>
              <div style='font-size:18px;font-weight:700;color:{color};'>{pct:+.2f}%</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AI PICKS
# ══════════════════════════════════════════════════════════════════════════════
with tab_picks:
    from utils.ai import has_key, no_key_banner, generate_recommendations

    if not has_key():
        no_key_banner("AI recommendations")
    else:
        wls = st.session_state.get("watchlists", {})
        source = st.radio("Ticker source:", ["Default US Watchlist", "Custom"] + list(wls.keys()),
                          horizontal=True, key="disc_picks_source")

        if source == "Default US Watchlist":
            pick_tickers = TICKERS_US
        elif source == "Custom":
            raw_picks = st.text_input("Enter tickers:", ", ".join(TICKERS_US[:10]), key="disc_picks_raw")
            pick_tickers = [t.strip().upper() for t in raw_picks.split(",") if t.strip()]
        else:
            pick_tickers = wls.get(source, TICKERS_US)

        st.caption(f"Using {len(pick_tickers)} tickers: {', '.join(pick_tickers[:12])}{'…' if len(pick_tickers) > 12 else ''}")

        profile = st.session_state.get("profile", {})
        if not profile:
            st.warning("Complete your **Profile** in My Portfolio to get personalized picks.")

        if st.button("🔮 Generate Today's Picks", type="primary", key="disc_picks_run"):
            with st.spinner("Analyzing opportunities with Claude AI…"):
                result = generate_recommendations(pick_tickers, profile)
            if result:
                st.markdown("---")
                st.markdown(result)
                from datetime import date
                st.caption(f"Generated on {date.today().isoformat()}")
            else:
                st.error("Error generating picks. Check your API key in Settings.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — INSTITUTIONAL
# ══════════════════════════════════════════════════════════════════════════════
with tab_inst:
    import yfinance as yf

    st.markdown("<div style='color:#8aadcc;font-size:13px;margin-bottom:16px;'>See what institutional investors hold in your portfolio and watchlist stocks.</div>", unsafe_allow_html=True)

    portfolio  = st.session_state.get("portfolio", [])
    watchlists = st.session_state.get("watchlists", {})
    all_tickers_inst = list({h["ticker"] for h in portfolio})
    for wl in watchlists.values():
        all_tickers_inst.extend(wl)
    all_tickers_inst = sorted(set(all_tickers_inst))[:15]

    if not all_tickers_inst:
        st.info("Add holdings or watchlist tickers to see institutional data.")
    else:
        sel_inst = st.selectbox("Select ticker", all_tickers_inst, key="inst_sel")

        if st.button("🔍 Fetch Institutional Data", key="inst_run"):
            with st.spinner("Fetching institutional holders…"):
                try:
                    t_obj = yf.Ticker(sel_inst)
                    inst_holders = t_obj.institutional_holders
                    major_holders = t_obj.major_holders
                    st.session_state[f"_inst_{sel_inst}"] = {
                        "institutional": inst_holders,
                        "major": major_holders,
                    }
                except Exception as e:
                    st.error(f"Could not fetch data: {e}")

        inst_data = st.session_state.get(f"_inst_{sel_inst}")
        if inst_data:
            maj = inst_data.get("major")
            if maj is not None and not maj.empty:
                st.subheader("📊 Major Holders")
                st.dataframe(maj, use_container_width=True, hide_index=True)

            inst = inst_data.get("institutional")
            if inst is not None and not inst.empty:
                st.subheader(f"🏛️ Top Institutional Holders — {sel_inst}")
                display = inst.copy()
                if "pctHeld" in display.columns:
                    display["pctHeld"] = (display["pctHeld"] * 100).round(2).astype(str) + "%"
                if "Value" in display.columns:
                    display["Value"] = display["Value"].apply(
                        lambda x: f"${x/1e9:.2f}B" if x > 1e9 else f"${x/1e6:.0f}M"
                    )
                st.dataframe(display, use_container_width=True, hide_index=True)
            else:
                st.info("No institutional holder data available for this ticker.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — CRYPTO
# ══════════════════════════════════════════════════════════════════════════════
with tab_crypto:
    import yfinance as yf
    import plotly.graph_objects as go
    from utils.config import COLOR_SUCCESS, COLOR_DANGER, COLOR_PRIMARY

    CRYPTO_TICKERS = {
        "Bitcoin":   "BTC-USD", "Ethereum": "ETH-USD", "BNB":      "BNB-USD",
        "Solana":    "SOL-USD", "XRP":      "XRP-USD", "Cardano":  "ADA-USD",
        "Avalanche": "AVAX-USD","Dogecoin": "DOGE-USD","Polkadot": "DOT-USD",
        "Chainlink": "LINK-USD",
    }

    @st.cache_data(ttl=300)
    def _get_crypto_hist(symbol: str, period: str):
        try:
            hist = yf.Ticker(symbol).history(period=period)
            info = yf.Ticker(symbol).info or {}
            return hist, info
        except Exception:
            return None, {}

    period_c = st.radio("Chart period", ["1d", "7d", "30d", "90d"], horizontal=True, key="crypto_period", index=1)
    selected_crypto = st.multiselect(
        "Select assets", list(CRYPTO_TICKERS.keys()),
        default=["Bitcoin", "Ethereum", "Solana", "BNB"],
        key="crypto_sel",
    )

    if not selected_crypto:
        st.info("Select at least one crypto asset above.")
    else:
        with st.spinner("Fetching crypto prices…"):
            COLS = 3
            crypto_rows = []
            for name in selected_crypto:
                sym = CRYPTO_TICKERS[name]
                try:
                    hist, info = _get_crypto_hist(sym, period_c)
                    if hist is None or hist.empty:
                        continue
                    price = float(hist["Close"].iloc[-1])
                    open_p = float(hist["Close"].iloc[0])
                    chg_pct = (price - open_p) / open_p * 100 if open_p else 0
                    mktcap = info.get("marketCap") or 0
                    crypto_rows.append({
                        "name": name, "symbol": sym, "price": price,
                        "chg_pct": chg_pct, "mktcap": mktcap, "hist": hist,
                    })
                except Exception:
                    continue

        if crypto_rows:
            # Price cards
            for i in range(0, len(crypto_rows), COLS):
                chunk = crypto_rows[i:i + COLS]
                cols  = st.columns(COLS)
                for col, r in zip(cols, chunk):
                    chg_color = COLOR_SUCCESS if r["chg_pct"] >= 0 else COLOR_DANGER
                    chg_arrow = "▲" if r["chg_pct"] >= 0 else "▼"
                    mc_str = f"${r['mktcap']/1e9:.1f}B" if r["mktcap"] > 1e9 else ""
                    price_fmt = f"${r['price']:,.2f}" if r["price"] > 1 else f"${r['price']:.6f}"
                    with col:
                        st.markdown(f"""
                        <div class='card' style='padding:16px;margin-bottom:4px;'>
                          <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                            <div>
                              <div style='font-size:15px;font-weight:800;color:#c8d8f0;'>{r["name"]}</div>
                              <div style='font-size:10px;color:#4a6a8a;'>{r["symbol"]}</div>
                            </div>
                            <div style='text-align:right;'>
                              <div style='font-size:17px;font-weight:700;color:#e8edf8;'>{price_fmt}</div>
                              <div style='font-size:12px;font-weight:600;color:{chg_color};'>{chg_arrow} {abs(r["chg_pct"]):.2f}%</div>
                            </div>
                          </div>
                          {f"<div style='font-size:10px;color:#3a5a7a;margin-top:4px;'>Mkt Cap: {mc_str}</div>" if mc_str else ""}
                        </div>""", unsafe_allow_html=True)

            # Comparison chart (normalized)
            st.divider()
            fig_c = go.Figure()
            palette = [COLOR_PRIMARY, COLOR_SUCCESS, "#F59E0B", "#8B5CF6", "#EF4444",
                       "#14B8A6", "#F97316", "#EC4899", "#06B6D4", "#84CC16"]
            for idx, r in enumerate(crypto_rows):
                y = r["hist"]["Close"]
                yn = y / y.iloc[0] * 100 if len(y) > 0 else y
                fig_c.add_trace(go.Scatter(
                    x=r["hist"].index, y=yn, mode="lines",
                    name=r["name"],
                    line=dict(color=palette[idx % len(palette)], width=2)))
            fig_c.update_layout(
                template="plotly_dark", paper_bgcolor="#09090B", plot_bgcolor="#09090B",
                title="Crypto Performance — Indexed (100 = start of period)",
                yaxis_title="Indexed Value",
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                hovermode="x unified", height=420, font=dict(color="#A1A1AA"),
                legend=dict(orientation="h", y=1.02),
                margin=dict(l=48, r=24, t=44, b=36))
            st.plotly_chart(fig_c, use_container_width=True)

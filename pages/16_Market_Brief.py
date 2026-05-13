import streamlit as st
from datetime import date
from utils.data import get_market_overview, get_sector_performance
from utils.plots import sector_bar
from utils.ai import has_key, no_key_banner, market_brief, morning_brief_ai
from utils.news_aggregator import (
    get_market_news,
    get_bulk_insider_transactions,
    get_earnings_calendar,
    get_macro_events_this_week,
    get_av_sentiment,
)

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📰 Market Intelligence</div>
  <div class='page-subtitle'>Multi-source market data · News · Insiders · Macro · AI Analysis</div>
</div>""", unsafe_allow_html=True)

today_label = date.today().strftime("%A, %B %d, %Y")
st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:16px;'>{today_label} — Live data</div>",
            unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 1, 1])
extended  = c2.checkbox("Extended Thinking", help="Deeper AI analysis (~2× slower)")
gen       = c1.button("🔮 Generate AI Brief", type="primary", disabled=not has_key())

if not has_key():
    st.info("💡 Add your Anthropic API key in **Settings** to unlock AI analysis.")

st.divider()

# ── 1. Market Snapshot ─────────────────────────────────────────────────────────
st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;'>📈 Market Snapshot</div>",
            unsafe_allow_html=True)

with st.spinner("Loading market data…"):
    mkt = get_market_overview()

cols = st.columns(len(mkt))
for col, (name, d) in zip(cols, mkt.items()):
    pct = d["change_pct"]
    p   = d["price"]
    fmt = f"${p:,.2f}" if name in ("Gold","Oil WTI") else \
          f"{p:.2f}%" if "Yield" in name else f"{p:,.2f}"
    col.metric(name, fmt, f"{'▲' if pct>=0 else '▼'} {abs(pct):.2f}%")

st.divider()

# ── 2. Sector Performance ──────────────────────────────────────────────────────
st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;'>🌐 Sector Performance (1 Month)</div>",
            unsafe_allow_html=True)
with st.spinner("Loading sectors…"):
    sec_ret = get_sector_performance("1mo")
st.plotly_chart(sector_bar(sec_ret), use_container_width=True)

st.divider()

# ── Tabs: News · Insiders · Earnings · Macro ───────────────────────────────────
tab_news, tab_insider, tab_earn, tab_macro = st.tabs([
    "📰 News Feed", "🏦 Insider Activity", "📅 Earnings Calendar", "🌐 Macro Events"
])

with tab_news:
    portfolio = st.session_state.get("portfolio", [])
    port_tickers = [h["ticker"] for h in portfolio if h.get("ticker")]

    sub1, sub2 = st.tabs(["Market Headlines", "Portfolio News"])

    with sub1:
        with st.spinner("Aggregating headlines from multiple sources…"):
            news = get_market_news(max_items=20)

        av_key = st.session_state.get("api_keys", {}).get("alpha_vantage", "")
        if av_key:
            spx_sentiment = get_av_sentiment("SPY", av_key)
            if spx_sentiment:
                sc = spx_sentiment.get("sentiment", "Neutral")
                color = "#22c55e" if sc == "Bullish" else "#ef4444" if sc == "Bearish" else "#f59e0b"
                st.markdown(f"""
                <div style='background:rgba(31,119,180,0.06);border:1px solid rgba(31,119,180,0.18);border-radius:10px;padding:12px 18px;margin-bottom:16px;display:flex;align-items:center;gap:16px;'>
                  <span style='font-size:10px;color:#4a6a8a;font-weight:700;letter-spacing:1px;text-transform:uppercase;'>Market Sentiment (Alpha Vantage)</span>
                  <span style='color:{color};font-size:15px;font-weight:800;'>{sc}</span>
                  <span style='color:#4a6a8a;font-size:11px;'>Score: {spx_sentiment.get("score", 0):+.3f}</span>
                </div>""", unsafe_allow_html=True)

        if not news:
            st.info("No headlines available right now. Try again in a few minutes.")
        else:
            # Group by source
            sources = {}
            for n in news:
                s = n.get("source", "Other")
                sources.setdefault(s, []).append(n)

            for source, items in sources.items():
                st.markdown(f"<div style='font-size:10px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin:16px 0 8px 0;'>{source}</div>",
                            unsafe_allow_html=True)
                for n in items:
                    url     = n.get("url", "#")
                    title   = n.get("title", "")
                    pub     = n.get("source", "")
                    d_str   = n.get("date", "")
                    summary = n.get("summary", "")
                    st.markdown(f"""
                    <div class='card' style='padding:12px 16px;margin-bottom:6px;'>
                      <a href='{url}' target='_blank' style='color:#7eb8e8;font-weight:600;font-size:13px;text-decoration:none;'>{title}</a>
                      {"<div style='color:#6a8aaa;font-size:12px;margin-top:4px;'>"+summary+"</div>" if summary else ""}
                      <div style='color:#4a6a8a;font-size:11px;margin-top:4px;'>{pub} &nbsp;·&nbsp; {d_str}</div>
                    </div>""", unsafe_allow_html=True)

    with sub2:
        if not port_tickers:
            st.info("Add holdings in **Portfolio** to see portfolio-specific news here.")
        else:
            from utils.news_aggregator import get_portfolio_news
            with st.spinner(f"Loading news for {len(port_tickers)} holdings…"):
                p_news = get_portfolio_news(port_tickers, max_per_ticker=3)

            if not p_news:
                st.info("No recent news found for your holdings.")
            else:
                for n in p_news:
                    st.markdown(f"""
                    <div class='card' style='padding:12px 16px;margin-bottom:6px;'>
                      <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;'>
                        <span style='background:rgba(31,119,180,0.15);color:#7eb8e8;font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;'>{n.get('ticker','')}</span>
                        <span style='color:#4a6a8a;font-size:11px;'>{n.get('source','')} · {n.get('date','')}</span>
                      </div>
                      <a href='{n.get("url","#")}' target='_blank' style='color:#c8d8f0;font-weight:600;font-size:13px;text-decoration:none;'>{n.get('title','')}</a>
                    </div>""", unsafe_allow_html=True)

with tab_insider:
    portfolio  = st.session_state.get("portfolio", [])
    port_ticks = [h["ticker"] for h in portfolio if h.get("ticker")]
    wl_ticks   = []
    for lst in st.session_state.get("watchlists", {}).values():
        wl_ticks.extend(lst)
    all_ticks = list(dict.fromkeys(port_ticks + wl_ticks))[:12]

    if not all_ticks:
        st.info("Add holdings or watchlists to see insider filings here.")
    else:
        days_back = st.slider("Look-back window (days)", 7, 90, 30, key="insider_days")
        with st.spinner(f"Fetching SEC Form 4 filings for {len(all_ticks)} tickers…"):
            txns = get_bulk_insider_transactions(all_ticks, days=days_back)

        if not txns:
            st.markdown(f"""
            <div class='card' style='text-align:center;color:#4a6a8a;padding:28px;'>
              No Form 4 insider filings found in the last {days_back} days for your holdings.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>{len(txns)} filing(s) found via SEC EDGAR</div>",
                        unsafe_allow_html=True)
            for t in txns:
                st.markdown(f"""
                <div class='card' style='padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
                  <span style='background:rgba(31,119,180,0.15);color:#7eb8e8;font-size:12px;font-weight:700;padding:3px 10px;border-radius:10px;min-width:60px;text-align:center;'>{t.get('ticker','')}</span>
                  <div style='flex:1;'>
                    <div style='color:#c8d8f0;font-size:13px;font-weight:600;'>{t.get('filer','Unknown filer')}</div>
                    <div style='color:#4a6a8a;font-size:11px;margin-top:2px;'>Form {t.get('form','4')} · Filed {t.get('date','')} · Period: {t.get('period','')}</div>
                  </div>
                  <a href='{t.get("edgar_url","#")}' target='_blank' style='color:#4a90d9;font-size:12px;font-weight:600;text-decoration:none;white-space:nowrap;'>View on EDGAR →</a>
                </div>""", unsafe_allow_html=True)

with tab_earn:
    portfolio  = st.session_state.get("portfolio", [])
    port_ticks = [h["ticker"] for h in portfolio if h.get("ticker")]
    wl_ticks   = []
    for lst in st.session_state.get("watchlists", {}).values():
        wl_ticks.extend(lst)
    all_for_earn = list(dict.fromkeys(port_ticks + wl_ticks))[:20]

    if not all_for_earn:
        st.info("Add holdings or watchlists to see upcoming earnings here.")
    else:
        with st.spinner("Loading earnings calendar…"):
            earnings = get_earnings_calendar(all_for_earn)

        if not earnings:
            st.markdown("""
            <div class='card' style='text-align:center;color:#4a6a8a;padding:28px;'>
              No upcoming earnings found for your holdings in the near term.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>{len(earnings)} upcoming earnings event(s)</div>",
                        unsafe_allow_html=True)
            for e in earnings:
                days_away = ""
                try:
                    from datetime import datetime
                    diff = (datetime.strptime(e["date"], "%Y-%m-%d").date() - date.today()).days
                    days_away = f"{diff}d away" if diff >= 0 else "Past"
                    urgency_color = "#ef4444" if diff <= 3 else "#f59e0b" if diff <= 7 else "#22c55e"
                except Exception:
                    urgency_color = "#4a6a8a"

                st.markdown(f"""
                <div class='card' style='padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;gap:16px;'>
                  <span style='background:rgba(31,119,180,0.15);color:#7eb8e8;font-size:13px;font-weight:800;padding:4px 12px;border-radius:10px;min-width:65px;text-align:center;'>{e.get('ticker','')}</span>
                  <div style='flex:1;'>
                    <div style='color:#c8d8f0;font-size:14px;font-weight:600;'>Earnings Report</div>
                    <div style='color:#4a6a8a;font-size:12px;margin-top:2px;'>
                      📅 {e.get('date','')}
                      {"&nbsp;·&nbsp; EPS Est: " + str(e.get('eps_est')) if e.get('eps_est') else ""}
                    </div>
                  </div>
                  <span style='color:{urgency_color};font-size:12px;font-weight:700;'>{days_away}</span>
                </div>""", unsafe_allow_html=True)

with tab_macro:
    with st.spinner("Loading macro events…"):
        macro = get_macro_events_this_week()

    if not macro:
        st.info("No macro events found for this week.")
    else:
        st.markdown("<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>Key economic releases and events this week</div>",
                    unsafe_allow_html=True)
        for ev in macro:
            st.markdown(f"""
            <div class='card' style='padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;gap:16px;'>
              <div style='flex:1;'>
                <div style='color:#c8d8f0;font-size:13px;font-weight:600;'>{ev.get('name','')}</div>
                <div style='color:#4a6a8a;font-size:11px;margin-top:2px;'>{ev.get('source','FRED')} · {ev.get('date','')}</div>
              </div>
            </div>""", unsafe_allow_html=True)

st.divider()

# ── AI Brief ───────────────────────────────────────────────────────────────────
st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;'>🤖 AI Market Intelligence</div>",
            unsafe_allow_html=True)

if not has_key():
    no_key_banner("Market Brief")
elif gen:
    portfolio  = st.session_state.get("portfolio", [])
    port_ticks = [h["ticker"] for h in portfolio if h.get("ticker")]
    wl_ticks   = [t for lst in st.session_state.get("watchlists", {}).values() for t in lst]
    all_ticks  = list(dict.fromkeys(port_ticks + wl_ticks))[:15]

    with st.spinner("Gathering data from all sources…"):
        from utils.news_aggregator import get_portfolio_news
        p_news   = get_portfolio_news(port_ticks)
        insiders = get_bulk_insider_transactions(all_ticks, days=30)
        earnings = get_earnings_calendar(all_ticks)
        macro    = get_macro_events_this_week()

    with st.spinner("Generating brief with Claude AI" + (" (Extended Thinking)" if extended else "") + "…"):
        result = morning_brief_ai(
            market_data=mkt,
            portfolio_tickers=port_ticks,
            portfolio_news=p_news,
            insider_txns=insiders,
            earnings=earnings,
            macro_events=macro,
            extended=extended,
        )

    if result:
        st.markdown(result)
        st.divider()
        col_dl, col_email = st.columns(2)
        col_dl.download_button(
            "⬇️ Download Brief",
            result,
            file_name=f"market_brief_{date.today().isoformat()}.md",
            use_container_width=True,
        )
        if col_email.button("📧 Send as Email", use_container_width=True):
            from utils.morning_brief import (
                build_brief_html, send_brief_email, is_email_configured
            )
            if not is_email_configured():
                st.warning("Configure email in **Morning Brief** settings first.")
            else:
                html = build_brief_html(result, mkt, p_news, insiders, earnings, macro,
                                        username=st.session_state.get("name",""))
                ok, err = send_brief_email(html)
                if ok:
                    st.success("Brief sent to your email!")
                else:
                    st.error(f"Email failed: {err}")
    else:
        st.error("Error generating brief. Check your API key.")
else:
    st.info("Click **Generate AI Brief** above for a comprehensive AI-powered market analysis built from all data sources.")

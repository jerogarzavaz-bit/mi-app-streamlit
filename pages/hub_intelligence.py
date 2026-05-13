import streamlit as st
from datetime import date, timedelta

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📡 Intelligence</div>
  <div class='page-subtitle'>Morning Brief · News · Calendar · Insiders · Transcripts</div>
</div>""", unsafe_allow_html=True)

tab_brief, tab_news, tab_cal, tab_insider, tab_transcript = st.tabs([
    "☀️ Morning Brief", "📰 News", "📅 Calendar", "🏦 Insiders", "🎙️ Transcripts"
])

username = st.session_state.get("username", "")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MORNING BRIEF
# ══════════════════════════════════════════════════════════════════════════════
with tab_brief:
    from utils.data import get_market_overview
    from utils.ai import has_key, morning_brief_ai
    from utils.news_aggregator import (get_portfolio_news, get_bulk_insider_transactions,
                                       get_earnings_calendar, get_macro_events_this_week)
    from utils.morning_brief import (build_brief_html, send_brief_email,
                                     get_email_config, is_email_configured)
    from utils.db import save_user_data, is_configured

    cfg      = get_email_config()
    ai_ok    = has_key()
    email_ok = is_email_configured()
    sched_on = cfg.get("enabled", False)

    cs1, cs2, cs3 = st.columns(3)
    cs1.markdown(f"""
    <div style='background:{"rgba(34,197,94,0.08)" if ai_ok else "rgba(239,68,68,0.08)"};border:1px solid {"rgba(34,197,94,0.25)" if ai_ok else "rgba(239,68,68,0.2)"};border-radius:10px;padding:12px 16px;text-align:center;'>
      <div style='font-size:16px;'>{"✅" if ai_ok else "❌"}</div>
      <div style='color:{"#22c55e" if ai_ok else "#ef4444"};font-size:11px;font-weight:700;margin-top:4px;'>AI {"Active" if ai_ok else "No API Key"}</div>
    </div>""", unsafe_allow_html=True)
    cs2.markdown(f"""
    <div style='background:{"rgba(34,197,94,0.08)" if email_ok else "rgba(245,158,11,0.08)"};border:1px solid {"rgba(34,197,94,0.25)" if email_ok else "rgba(245,158,11,0.2)"};border-radius:10px;padding:12px 16px;text-align:center;'>
      <div style='font-size:16px;'>{"✅" if email_ok else "⚙️"}</div>
      <div style='color:{"#22c55e" if email_ok else "#f59e0b"};font-size:11px;font-weight:700;margin-top:4px;'>Email {"Configured" if email_ok else "Not Set"}</div>
    </div>""", unsafe_allow_html=True)
    cs3.markdown(f"""
    <div style='background:{"rgba(34,197,94,0.08)" if sched_on else "rgba(74,106,138,0.08)"};border:1px solid {"rgba(34,197,94,0.25)" if sched_on else "rgba(74,106,138,0.2)"};border-radius:10px;padding:12px 16px;text-align:center;'>
      <div style='font-size:16px;'>{"⏰" if sched_on else "⏸️"}</div>
      <div style='color:{"#22c55e" if sched_on else "#4a6a8a"};font-size:11px;font-weight:700;margin-top:4px;'>Auto {"On: " + cfg.get("send_time","07:00") if sched_on else "Schedule Off"}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    if not ai_ok:
        st.warning("Add your Anthropic API key in **Settings** to generate AI briefs.")

    col_gen, col_send = st.columns([2, 1])
    gen_btn  = col_gen.button("🔮 Generate Today's Brief", type="primary", disabled=not ai_ok,
                               use_container_width=True, key="intel_brief_gen")
    send_btn = col_send.button("📧 Generate & Send", disabled=not (ai_ok and email_ok),
                                use_container_width=True, key="intel_brief_send")

    if gen_btn or send_btn:
        portfolio  = st.session_state.get("portfolio", [])
        port_ticks = [h["ticker"] for h in portfolio if h.get("ticker")]
        wl_ticks   = [t for lst in st.session_state.get("watchlists", {}).values() for t in lst]
        all_ticks  = list(dict.fromkeys(port_ticks + wl_ticks))[:15]

        with st.spinner("Fetching data from all sources…"):
            mkt      = get_market_overview()
            p_news   = get_portfolio_news(port_ticks)
            insiders = get_bulk_insider_transactions(all_ticks, days=30)
            earnings = get_earnings_calendar(all_ticks)
            macro    = get_macro_events_this_week()

        with st.spinner("Claude AI is writing your brief…"):
            ai_text = morning_brief_ai(market_data=mkt, portfolio_tickers=port_ticks,
                                       portfolio_news=p_news, insider_txns=insiders,
                                       earnings=earnings, macro_events=macro)

        st.session_state["_last_brief_text"]    = ai_text
        st.session_state["_last_brief_mkt"]     = mkt
        st.session_state["_last_brief_pnews"]   = p_news
        st.session_state["_last_brief_insider"]  = insiders
        st.session_state["_last_brief_earnings"] = earnings
        st.session_state["_last_brief_macro"]    = macro
        st.session_state["_last_brief_date"]     = date.today().isoformat()
        st.markdown(ai_text)

        if send_btn:
            html = build_brief_html(ai_text, mkt, p_news, insiders, earnings, macro,
                                    username=st.session_state.get("name", username))
            ok, err = send_brief_email(html)
            if ok:
                st.success(f"✅ Brief sent to {cfg['to_email']}")
                st.session_state[f"_brief_last_sent_{username}"] = date.today().isoformat()
            else:
                st.error(f"Email failed: {err}")

    elif st.session_state.get("_last_brief_date") == date.today().isoformat():
        st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>Showing today's brief — generated earlier this session.</div>", unsafe_allow_html=True)
        st.markdown(st.session_state.get("_last_brief_text", ""))
    else:
        st.markdown("""
        <div class='card' style='text-align:center;color:#4a6a8a;padding:40px;'>
          <div style='font-size:36px;margin-bottom:12px;'>☀️</div>
          <div style='font-size:15px;font-weight:600;color:#6a8aaa;margin-bottom:8px;'>Ready when you are</div>
          <div style='font-size:13px;'>Click <strong style='color:#7eb8e8;'>Generate Today's Brief</strong> for your personalized AI market briefing.</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    with st.expander("⚙️ Email & Schedule Settings"):
        api_keys = st.session_state.get("api_keys", {})
        st.markdown("""
        <div style='background:rgba(31,119,180,0.06);border:1px solid rgba(31,119,180,0.15);border-radius:10px;padding:14px 18px;margin-bottom:16px;'>
          <div style='font-size:13px;color:#8aadcc;line-height:1.8;'>
            <strong style='color:#c8d8f0;'>Gmail setup:</strong> Enable 2FA → myaccount.google.com/apppasswords → Create App Password for "Mail"
          </div>
        </div>""", unsafe_allow_html=True)
        with st.form("intel_brief_email_form"):
            to_email  = st.text_input("Delivery email", value=api_keys.get("brief_email", ""), placeholder="you@example.com")
            smtp_user = st.text_input("Gmail address", value=api_keys.get("brief_smtp_user", ""), placeholder="yourname@gmail.com")
            smtp_pass = st.text_input("Gmail App Password", value=api_keys.get("brief_smtp_password", ""), type="password", placeholder="xxxx xxxx xxxx xxxx")
            c1, c2 = st.columns(2)
            send_time = c1.text_input("Send time (HH:MM)", value=api_keys.get("brief_send_time", "07:00"))
            enabled = c2.checkbox("Enable auto-send on login", value=bool(api_keys.get("brief_enabled", False)))
            if st.form_submit_button("💾 Save", type="primary"):
                api_keys.update({"brief_email": to_email.strip(), "brief_smtp_user": smtp_user.strip(),
                                  "brief_smtp_password": smtp_pass.strip(), "brief_smtp_host": "smtp.gmail.com",
                                  "brief_smtp_port": 587, "brief_send_time": send_time.strip() or "07:00",
                                  "brief_enabled": enabled})
                st.session_state.api_keys = api_keys
                if is_configured(): save_user_data(username)
                st.success("Email settings saved!")
                st.rerun()
        if is_email_configured():
            if st.button("🧪 Send Test Email", key="intel_test_email"):
                test_html = build_brief_html("This is a **test email** from The Bull Monkey. 🎉", {}, [], [], [], [],
                                             username=st.session_state.get("name", username))
                ok, err = send_brief_email(test_html, "🧪 Test — The Bull Monkey")
                if ok: st.success(f"Test sent to {get_email_config()['to_email']}")
                else:  st.error(f"Failed: {err}")

    if st.session_state.get("_last_brief_text"):
        with st.expander("📧 Preview Email Template"):
            mkt_s      = st.session_state.get("_last_brief_mkt", {})
            p_news_s   = st.session_state.get("_last_brief_pnews", [])
            insiders_s = st.session_state.get("_last_brief_insider", [])
            earnings_s = st.session_state.get("_last_brief_earnings", [])
            macro_s    = st.session_state.get("_last_brief_macro", [])
            html = build_brief_html(st.session_state["_last_brief_text"], mkt_s, p_news_s, insiders_s, earnings_s, macro_s,
                                    username=st.session_state.get("name", username))
            st.components.v1.html(html, height=700, scrolling=True)
            st.download_button("⬇️ Download HTML", html,
                               file_name=f"brief_{date.today().isoformat()}.html", mime="text/html")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — NEWS
# ══════════════════════════════════════════════════════════════════════════════
with tab_news:
    from utils.news_aggregator import get_market_news, get_portfolio_news, get_av_sentiment
    from utils.ai import has_key, market_brief

    portfolio     = st.session_state.get("portfolio", [])
    port_tickers  = [h["ticker"] for h in portfolio if h.get("ticker")]

    news_sub1, news_sub2 = st.tabs(["Market Headlines", "Portfolio News"])

    with news_sub1:
        with st.spinner("Aggregating headlines…"):
            news = get_market_news(max_items=20)

        av_key = st.session_state.get("api_keys", {}).get("alpha_vantage", "")
        if av_key:
            spx_sentiment = get_av_sentiment("SPY", av_key)
            if spx_sentiment:
                sc = spx_sentiment.get("sentiment", "Neutral")
                color = "#22c55e" if sc == "Bullish" else "#ef4444" if sc == "Bearish" else "#f59e0b"
                st.markdown(f"""
                <div style='background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px 16px;margin-bottom:16px;display:inline-block;'>
                  <span style='font-size:11px;color:#4a6a8a;letter-spacing:1px;text-transform:uppercase;'>Market Sentiment (AV)</span>
                  <span style='color:{color};font-weight:700;font-size:14px;margin-left:12px;'>{sc}</span>
                </div>""", unsafe_allow_html=True)

        if news:
            for n in news:
                badge = n.get("source", "")
                st.markdown(f"""
                <div class='card' style='padding:12px 16px;margin-bottom:8px;'>
                  <div style='display:flex;align-items:flex-start;gap:10px;'>
                    <span style='background:rgba(79,142,247,0.15);color:#7eb8e8;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;white-space:nowrap;flex-shrink:0;'>{badge}</span>
                    <div>
                      <a href='{n.get("url","#")}' target='_blank' style='color:#c8d8f0;font-weight:600;font-size:13px;text-decoration:none;'>{n.get("title","")}</a>
                      <div style='color:#4a6a8a;font-size:11px;margin-top:3px;'>{n.get("date","")}</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No headlines available right now. Try again in a moment.")

        if has_key():
            if st.button("🤖 Generate AI Market Brief", type="primary", key="intel_ai_brief"):
                extended = st.checkbox("Extended Thinking", key="intel_brief_ext")
                with st.spinner("Analyzing markets with Claude AI…"):
                    result = market_brief(extended=extended)
                if result: st.markdown(result)

    with news_sub2:
        if not port_tickers:
            st.info("Add holdings to **My Portfolio** to see portfolio-specific news.")
        else:
            with st.spinner(f"Fetching news for {len(port_tickers)} portfolio tickers…"):
                p_news = get_portfolio_news(port_tickers)
            if p_news:
                for n in p_news:
                    ticker_tag = n.get("ticker", "")
                    st.markdown(f"""
                    <div class='card' style='padding:12px 16px;margin-bottom:8px;'>
                      <div style='display:flex;align-items:flex-start;gap:10px;'>
                        <span style='background:rgba(79,142,247,0.15);color:#7eb8e8;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;'>{ticker_tag}</span>
                        <div>
                          <a href='{n.get("url","#")}' target='_blank' style='color:#c8d8f0;font-weight:600;font-size:13px;text-decoration:none;'>{n.get("title","")}</a>
                          <div style='color:#4a6a8a;font-size:11px;margin-top:3px;'>{n.get("source","")} · {n.get("date","")}</div>
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No recent portfolio news found.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
with tab_cal:
    from utils.data import get_earnings_calendar as _get_earnings_cal
    from utils.news_aggregator import get_macro_events_this_week
    from utils.config import TICKERS_US, TICKERS_MX
    import pandas as pd

    cal_sub1, cal_sub2 = st.tabs(["Earnings", "Macro Events"])

    with cal_sub1:
        source_cal = st.radio("Ticker source:", ["US Default", "México", "My Portfolio", "Custom"],
                              horizontal=True, key="intel_cal_source")
        portfolio_cal = st.session_state.get("portfolio", [])

        if source_cal == "US Default":
            cal_tickers = TICKERS_US
        elif source_cal == "México":
            cal_tickers = TICKERS_MX
        elif source_cal == "My Portfolio":
            cal_tickers = [h["ticker"] for h in portfolio_cal if h.get("ticker")]
            if not cal_tickers:
                st.info("No portfolio holdings. Add holdings in My Portfolio.")
                cal_tickers = TICKERS_US
        else:
            raw_cal = st.text_input("Enter tickers:", ", ".join(TICKERS_US[:8]), key="intel_cal_raw")
            cal_tickers = [t.strip().upper() for t in raw_cal.split(",") if t.strip()]

        wls_cal = st.session_state.get("watchlists", {})
        if wls_cal:
            sel_wl_cal = st.selectbox("Or use watchlist:", ["— none —"] + list(wls_cal.keys()), key="intel_cal_wl")
            if sel_wl_cal != "— none —":
                cal_tickers = wls_cal[sel_wl_cal]

        if st.button(f"📆 Load Earnings ({len(cal_tickers)} tickers)", type="primary", key="intel_cal_run"):
            with st.spinner("Fetching earnings dates…"):
                events = _get_earnings_cal(tuple(cal_tickers))

            today = date.today()
            upcoming = [e for e in events if e["earnings_date"].date() >= today]
            this_week = [e for e in upcoming if e["earnings_date"].date() <= today + timedelta(days=7)]

            c1, c2, c3 = st.columns(3)
            c1.metric("Upcoming (≤30d)", len([e for e in upcoming if e["earnings_date"].date() <= today + timedelta(days=30)]))
            c2.metric("This Week", len(this_week))
            c3.metric("Tickers Checked", len(cal_tickers))

            if upcoming:
                df_earn = pd.DataFrame([{
                    "Ticker":    e["ticker"], "Company": e["name"],
                    "Date":      e["earnings_date"].strftime("%b %d, %Y"),
                    "Days Away": (e["earnings_date"].date() - today).days,
                    "EPS Est.":  f"${e['eps_estimate']:.2f}" if e["eps_estimate"] else "N/A",
                } for e in sorted(upcoming, key=lambda x: x["earnings_date"])])
                st.dataframe(df_earn, use_container_width=True, hide_index=True)
            else:
                st.info("No upcoming earnings found for these tickers.")

    with cal_sub2:
        with st.spinner("Loading macro events…"):
            macro_events = get_macro_events_this_week()
        if macro_events:
            for ev in macro_events:
                st.markdown(f"""
                <div class='card' style='padding:10px 16px;margin-bottom:6px;'>
                  <div style='font-weight:600;color:#c8d8f0;font-size:13px;'>{ev.get('name','')}</div>
                  <div style='color:#4a6a8a;font-size:11px;margin-top:2px;'>{ev.get('date','')}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No macro events data available right now.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — INSIDER ACTIVITY
# ══════════════════════════════════════════════════════════════════════════════
with tab_insider:
    from utils.news_aggregator import get_bulk_insider_transactions
    import pandas as pd

    portfolio_ins = st.session_state.get("portfolio", [])
    wls_ins       = st.session_state.get("watchlists", {})
    port_ticks_ins = [h["ticker"] for h in portfolio_ins if h.get("ticker")]
    wl_ticks_ins   = [t for lst in wls_ins.values() for t in lst]
    default_ins    = list(dict.fromkeys(port_ticks_ins + wl_ticks_ins))[:15]

    if not default_ins:
        st.info("Add holdings or watchlists to track insider activity for your securities.")
        default_ins = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]

    c1, c2 = st.columns([3, 1])
    days_ins = c2.slider("Days back", 7, 90, 30, key="intel_insider_days")
    tickers_ins_raw = c1.text_input("Tickers to track:", ", ".join(default_ins[:10]),
                                     key="intel_insider_tickers")
    tickers_ins = [t.strip().upper() for t in tickers_ins_raw.split(",") if t.strip()]

    if st.button("🔍 Load Insider Filings", type="primary", key="intel_insider_run"):
        with st.spinner(f"Querying SEC EDGAR for {len(tickers_ins)} tickers…"):
            txns = get_bulk_insider_transactions(tickers_ins, days=days_ins)

        if txns:
            st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>Found {len(txns)} filings in the last {days_ins} days</div>", unsafe_allow_html=True)
            df_ins = pd.DataFrame([{
                "Ticker":    t.get("ticker",""),
                "Filer":     t.get("filer",""),
                "Filed":     t.get("date",""),
                "Form":      t.get("form",""),
                "EDGAR":     t.get("edgar_url",""),
            } for t in txns])
            st.dataframe(df_ins, use_container_width=True, hide_index=True,
                         column_config={"EDGAR": st.column_config.LinkColumn()})
        else:
            st.info(f"No insider filings found for the selected tickers in the last {days_ins} days.")
    else:
        st.markdown("""
        <div class='card' style='text-align:center;color:#4a6a8a;padding:32px;'>
          <div style='font-size:32px;margin-bottom:8px;'>🏦</div>
          <div style='font-size:14px;'>Click <strong style='color:#7eb8e8;'>Load Insider Filings</strong> to query SEC EDGAR Form 4 filings for your tickers.</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TRANSCRIPTS
# ══════════════════════════════════════════════════════════════════════════════
with tab_transcript:
    from utils.ai import has_key, no_key_banner, analyze_transcript

    if not has_key():
        no_key_banner("transcript analysis")
    else:
        method = st.radio("Source:", ["Paste transcript", "Upload .txt file"], horizontal=True, key="intel_tx_method")
        transcript = ""
        if method == "Paste transcript":
            transcript = st.text_area("Paste the full earnings call transcript:",
                                      height=280, placeholder="Q4 2025 Earnings Call\nCEO: Good afternoon…",
                                      key="intel_tx_area")
        else:
            uploaded = st.file_uploader("Upload transcript (.txt)", type=["txt"], key="intel_tx_upload")
            if uploaded:
                transcript = uploaded.read().decode("utf-8", errors="ignore")
                st.success(f"Loaded {len(transcript):,} characters")
                with st.expander("Preview"):
                    st.text(transcript[:1000] + "…")

        ticker_hint = st.text_input("Ticker hint (optional)", placeholder="NVDA", key="intel_tx_ticker")
        if st.button("🔍 Analyze Transcript", type="primary", disabled=not transcript, key="intel_tx_run"):
            with st.spinner("Analyzing with Claude AI…"):
                result = analyze_transcript(transcript)
            if result:
                st.markdown("---")
                if ticker_hint:
                    st.subheader(f"Transcript Analysis — {ticker_hint.upper()}")
                st.markdown(result)
                st.download_button("⬇️ Download Analysis", result,
                                   file_name=f"transcript_{ticker_hint or 'analysis'}.md",
                                   key="intel_tx_dl")
        elif not transcript:
            st.markdown("""
            <div class='card' style='text-align:center;color:#4a6a8a;padding:32px;'>
              <div style='font-size:32px;margin-bottom:8px;'>🎙️</div>
              <div style='font-size:14px;'>Paste or upload an earnings call transcript, then click Analyze.</div>
              <div style='font-size:12px;margin-top:8px;color:#3a5a7a;'>Claude extracts tone, guidance, risks, and analyst concerns.</div>
            </div>""", unsafe_allow_html=True)

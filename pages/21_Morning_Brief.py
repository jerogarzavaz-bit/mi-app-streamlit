import streamlit as st
from datetime import date, datetime
from utils.data import get_market_overview
from utils.ai import has_key, morning_brief_ai
from utils.news_aggregator import (
    get_portfolio_news, get_bulk_insider_transactions,
    get_earnings_calendar, get_macro_events_this_week,
)
from utils.morning_brief import (
    build_brief_html, send_brief_email,
    get_email_config, is_email_configured,
)
from utils.db import save_user_data, is_configured

username = st.session_state.get("username", "")

def _autosave():
    if is_configured():
        save_user_data(username)

st.markdown("""
<div class='page-header'>
  <div class='page-title'>☀️ Morning Brief</div>
  <div class='page-subtitle'>Your personalized AI-powered daily market briefing — delivered before the open</div>
</div>""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_brief, tab_schedule, tab_preview = st.tabs(["📋 Generate Brief", "⚙️ Schedule & Email", "📧 Preview Email"])

# ─────────────────────────── TAB 1: Generate ──────────────────────────────────
with tab_brief:
    cfg = get_email_config()
    api_keys = st.session_state.get("api_keys", {})

    # Status row
    cs1, cs2, cs3 = st.columns(3)
    ai_ok = has_key()
    email_ok = is_email_configured()
    sched_on = cfg.get("enabled", False)

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
    gen_btn  = col_gen.button("🔮 Generate Today's Brief", type="primary",
                               disabled=not ai_ok, use_container_width=True)
    send_btn = col_send.button("📧 Generate & Send", disabled=not (ai_ok and email_ok),
                                use_container_width=True)

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
            ai_text = morning_brief_ai(
                market_data=mkt,
                portfolio_tickers=port_ticks,
                portfolio_news=p_news,
                insider_txns=insiders,
                earnings=earnings,
                macro_events=macro,
            )

        st.session_state["_last_brief_text"]    = ai_text
        st.session_state["_last_brief_mkt"]     = mkt
        st.session_state["_last_brief_pnews"]   = p_news
        st.session_state["_last_brief_insider"]  = insiders
        st.session_state["_last_brief_earnings"] = earnings
        st.session_state["_last_brief_macro"]    = macro
        st.session_state["_last_brief_date"]     = date.today().isoformat()

        st.markdown(ai_text)

        if send_btn:
            html = build_brief_html(
                ai_text, mkt, p_news, insiders, earnings, macro,
                username=st.session_state.get("name", username),
            )
            ok, err = send_brief_email(html)
            if ok:
                st.success(f"✅ Brief sent to {cfg['to_email']}")
                st.session_state[f"_brief_last_sent_{username}"] = date.today().isoformat()
            else:
                st.error(f"Email failed: {err}")

    elif st.session_state.get("_last_brief_date") == date.today().isoformat():
        st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>Showing today's brief — generated earlier this session.</div>",
                    unsafe_allow_html=True)
        st.markdown(st.session_state.get("_last_brief_text", ""))
    else:
        st.markdown("""
        <div class='card' style='text-align:center;color:#4a6a8a;padding:40px;'>
          <div style='font-size:36px;margin-bottom:12px;'>☀️</div>
          <div style='font-size:15px;font-weight:600;color:#6a8aaa;margin-bottom:8px;'>Ready when you are</div>
          <div style='font-size:13px;'>Click <strong style='color:#7eb8e8;'>Generate Today's Brief</strong> to get your personalized AI market briefing.</div>
          <div style='font-size:12px;margin-top:12px;color:#3a5a7a;'>
            Sources: Yahoo Finance · Reuters · CNBC · SEC EDGAR · FRED Macro Calendar
          </div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────── TAB 2: Schedule ──────────────────────────────────
with tab_schedule:
    st.subheader("Email & Schedule Configuration")
    st.markdown("""
    <div style='background:rgba(31,119,180,0.06);border:1px solid rgba(31,119,180,0.15);border-radius:10px;padding:16px 20px;margin-bottom:20px;'>
      <div style='font-size:13px;color:#8aadcc;line-height:1.8;'>
        <strong style='color:#c8d8f0;'>How to set up Gmail sending:</strong><br>
        1. Enable <strong>2-Factor Authentication</strong> on your Google account<br>
        2. Go to <strong>myaccount.google.com/apppasswords</strong><br>
        3. Create an App Password for "Mail" / "Other (Stock Analyzer)"<br>
        4. Paste the 16-character password below (not your regular Gmail password)
      </div>
    </div>""", unsafe_allow_html=True)

    api_keys = st.session_state.get("api_keys", {})

    def _save_key(k, v):
        api_keys[k] = v
        st.session_state.api_keys = api_keys
        _autosave()

    with st.form("brief_email_form"):
        to_email = st.text_input("📧 Delivery email",
                                  value=api_keys.get("brief_email", ""),
                                  placeholder="you@example.com")
        smtp_user = st.text_input("Gmail address (sender)",
                                   value=api_keys.get("brief_smtp_user", ""),
                                   placeholder="yourname@gmail.com")
        smtp_pass = st.text_input("Gmail App Password (16 chars)",
                                   value=api_keys.get("brief_smtp_password", ""),
                                   type="password",
                                   placeholder="xxxx xxxx xxxx xxxx")
        c1, c2 = st.columns(2)
        send_time = c1.text_input("Send time (HH:MM, 24h)",
                                   value=api_keys.get("brief_send_time", "07:00"),
                                   placeholder="07:00")
        enabled = c2.checkbox("Enable auto-send on login",
                               value=bool(api_keys.get("brief_enabled", False)))

        if st.form_submit_button("💾 Save Email Settings", type="primary"):
            api_keys["brief_email"]         = to_email.strip()
            api_keys["brief_smtp_user"]     = smtp_user.strip()
            api_keys["brief_smtp_password"] = smtp_pass.strip()
            api_keys["brief_smtp_host"]     = "smtp.gmail.com"
            api_keys["brief_smtp_port"]     = 587
            api_keys["brief_send_time"]     = send_time.strip() or "07:00"
            api_keys["brief_enabled"]       = enabled
            st.session_state.api_keys = api_keys
            _autosave()
            st.success("Email settings saved!")
            st.rerun()

    # Test button
    if is_email_configured():
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        if st.button("🧪 Send Test Email", use_container_width=False):
            test_html = build_brief_html(
                "This is a **test email** from The Bull Monkey. Your Morning Brief is configured correctly! 🎉",
                market_data={},
                portfolio_news=[],
                insider_txns=[],
                earnings=[],
                macro_events=[],
                username=st.session_state.get("name", username),
            )
            ok, err = send_brief_email(test_html, subject="🧪 Test — The Bull Monkey Morning Brief")
            if ok:
                st.success(f"Test email sent to {get_email_config()['to_email']}")
            else:
                st.error(f"Failed: {err}")
    else:
        st.info("Fill in email settings above and save to enable sending.")

# ─────────────────────────── TAB 3: Preview ───────────────────────────────────
with tab_preview:
    brief_text = st.session_state.get("_last_brief_text", "")
    if not brief_text:
        st.info("Generate a brief first (in the **Generate Brief** tab) to preview the email template here.")
    else:
        mkt      = st.session_state.get("_last_brief_mkt", {})
        p_news   = st.session_state.get("_last_brief_pnews", [])
        insiders = st.session_state.get("_last_brief_insider", [])
        earnings = st.session_state.get("_last_brief_earnings", [])
        macro    = st.session_state.get("_last_brief_macro", [])

        html = build_brief_html(
            brief_text, mkt, p_news, insiders, earnings, macro,
            username=st.session_state.get("name", username),
        )

        st.markdown("<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>Email preview (rendered HTML)</div>",
                    unsafe_allow_html=True)
        st.components.v1.html(html, height=900, scrolling=True)

        col_dl, col_send = st.columns(2)
        col_dl.download_button(
            "⬇️ Download HTML",
            html,
            file_name=f"morning_brief_{date.today().isoformat()}.html",
            mime="text/html",
            use_container_width=True,
        )
        if col_send.button("📧 Send Now", type="primary", use_container_width=True):
            if not is_email_configured():
                st.warning("Configure email in the **Schedule & Email** tab first.")
            else:
                ok, err = send_brief_email(html)
                if ok:
                    cfg2 = get_email_config()
                    st.success(f"Brief sent to {cfg2['to_email']}")
                    st.session_state[f"_brief_last_sent_{username}"] = date.today().isoformat()
                else:
                    st.error(f"Email failed: {err}")

import streamlit as st
from utils.config import GLOBAL_CSS

st.set_page_config(
    page_title="The Bull Monkey",
    page_icon="🐵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Login page extra styles ────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes loginIn {
    from { opacity: 0; transform: translateY(20px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes floatY {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-10px); }
}
.login-wrap { animation: loginIn 0.5s cubic-bezier(0.16,1,0.3,1) both; }

div[data-testid="stForm"] {
    max-width: 380px;
    margin: 0 auto;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: 16px;
    padding: 28px 28px 22px 28px;
    box-shadow: var(--shadow-lg);
}
div[data-testid="stForm"] input {
    background: var(--bg-base) !important;
    border: 1px solid var(--border-default) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 13.5px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 9px 13px !important;
    transition: border-color 0.15s !important;
}
div[data-testid="stForm"] input:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.08) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session defaults ───────────────────────────────────────────────────────────
def _init_defaults():
    defaults = {
        "api_keys":       {"anthropic": "", "alpha_vantage": "", "fred": "", "fmp": ""},
        "portfolio":      [],
        "watchlists":     {},
        "analyses":       [],
        "screen_history": [],
        "profile":        {},
        "alerts":         [],
        "chat_messages":  [],
        "period":         "1y",
        "periodo_label":  "1 año",
        "data_provider":  "yfinance",
        "analyze_ticker": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_defaults()


# ── Y Logo SVG (inline) ────────────────────────────────────────────────────────
Y_LOGO_SVG = """<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ygrad" x1="6" y1="3" x2="22" y2="25" gradientUnits="userSpaceOnUse">
      <stop stop-color="#4f8ef7"/>
      <stop offset="1" stop-color="#9c6cff"/>
    </linearGradient>
  </defs>
  <path d="M6 3.5 L14 14.5 L22 3.5" stroke="url(#ygrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M14 14.5 L14 24.5" stroke="url(#ygrad)" stroke-width="2.5" stroke-linecap="round"/>
</svg>"""


# ── Login page ─────────────────────────────────────────────────────────────────
def _show_login(authenticator):
    st.markdown(f"""
    <div class='login-wrap'>
    <div style='text-align:center;padding:60px 0 40px 0;'>

      <!-- Logo mark -->
      <div style='display:inline-flex;align-items:center;justify-content:center;
                  width:72px;height:72px;
                  background:linear-gradient(135deg,#4f8ef7,#9c6cff);
                  border-radius:22px;
                  box-shadow:0 8px 32px rgba(79,142,247,0.35);
                  margin:0 auto 20px auto;
                  font-size:38px;line-height:1;
                  animation:floatY 4s ease-in-out infinite;'>🐵</div>

      <!-- Wordmark -->
      <div style='font-family:"Plus Jakarta Sans",sans-serif;font-size:28px;font-weight:900;
                  background:linear-gradient(135deg,#f0f0f6 30%,#9c6cff 100%);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;letter-spacing:-1px;line-height:1.1;margin-bottom:8px;'>
        The Bull Monkey
      </div>

      <div style='font-size:11px;color:#3d4452;letter-spacing:3px;font-weight:700;
                  text-transform:uppercase;font-family:"Space Grotesk",sans-serif;
                  margin-bottom:6px;'>AI Financial Intelligence</div>

      <div style='display:flex;justify-content:center;gap:24px;margin-top:16px;'>
        <span style='color:#252830;font-size:11px;font-family:"Space Grotesk",sans-serif;'>
          ⚡ Real-Time Data
        </span>
        <span style='color:#252830;font-size:11px;font-family:"Space Grotesk",sans-serif;'>
          ◆ Claude AI
        </span>
        <span style='color:#252830;font-size:11px;font-family:"Space Grotesk",sans-serif;'>
          ☁ Cloud Sync
        </span>
      </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        authenticator.login(fields={
            "Form name": "Sign in",
            "Username":  "Username",
            "Password":  "Password",
            "Login":     "Sign in →",
        })
        status = st.session_state.get("authentication_status")
        if status is False:
            st.error("Incorrect credentials. Please try again.")

    st.markdown("""
    <div style='text-align:center;color:#252830;font-size:11px;margin-top:60px;
                font-family:"Space Grotesk",sans-serif;letter-spacing:0.3px;'>
      The Bull Monkey &nbsp;·&nbsp; Powered by Claude AI &nbsp;·&nbsp; © 2025
    </div>
    """, unsafe_allow_html=True)


# ── Load user data after login ─────────────────────────────────────────────────
def _load_after_login(username: str):
    if st.session_state.get(f"_loaded_{username}"):
        return
    from utils.db import load_user_data, is_configured
    if is_configured():
        ok = load_user_data(username)
        st.session_state["_loaded_from_cloud"] = ok
    else:
        st.session_state["_loaded_from_cloud"] = False
    st.session_state[f"_loaded_{username}"] = True


# ── Alert checker ──────────────────────────────────────────────────────────────
def _check_alerts():
    from utils.data import get_stock_data
    for a in st.session_state.get("alerts", []):
        if a.get("triggered"):
            continue
        try:
            info, _ = get_stock_data(a["ticker"], "5d")
            if info is None:
                continue
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            hit = (a["condition"] == "Price >" and price > a["threshold"]) or \
                  (a["condition"] == "Price <" and price < a["threshold"])
            if hit:
                a["triggered"]    = True
                a["triggered_at"] = price
                st.toast(f"Alert fired: {a['ticker']} {a['condition']} "
                         f"${a['threshold']:.2f} — now ${price:.2f}", icon="🔔")
        except Exception:
            pass


# ── Morning Brief auto-send ────────────────────────────────────────────────────
def _check_morning_brief(username: str):
    try:
        from utils.morning_brief import should_send_today, build_brief_html, send_brief_email
        from utils.ai import has_key
        if not should_send_today(username) or not has_key():
            return
        import datetime
        st.session_state[f"_brief_last_sent_{username}"] = datetime.date.today().isoformat()

        from utils.data import get_market_overview
        from utils.news_aggregator import (
            get_portfolio_news, get_bulk_insider_transactions,
            get_earnings_calendar, get_macro_events_this_week,
        )
        from utils.ai import morning_brief_ai

        portfolio  = st.session_state.get("portfolio", [])
        port_ticks = [h["ticker"] for h in portfolio if h.get("ticker")]
        wl_ticks   = [t for lst in st.session_state.get("watchlists", {}).values() for t in lst]
        all_ticks  = list(dict.fromkeys(port_ticks + wl_ticks))[:15]

        mkt      = get_market_overview()
        p_news   = get_portfolio_news(port_ticks)
        insiders = get_bulk_insider_transactions(all_ticks, days=30)
        earnings = get_earnings_calendar(all_ticks)
        macro    = get_macro_events_this_week()
        ai_text  = morning_brief_ai(
            market_data=mkt, portfolio_tickers=port_ticks,
            portfolio_news=p_news, insider_txns=insiders,
            earnings=earnings, macro_events=macro,
        )
        html = build_brief_html(
            ai_text, mkt, p_news, insiders, earnings, macro,
            username=st.session_state.get("name", username),
        )
        ok, _ = send_brief_email(html)
        if ok:
            st.toast("Morning Brief sent to your inbox", icon="☀️")
    except Exception:
        pass


# ── Auth ───────────────────────────────────────────────────────────────────────
from utils.auth import get_authenticator

authenticator = get_authenticator()
auth_status   = st.session_state.get("authentication_status")

if auth_status is not True:
    _show_login(authenticator)
    st.stop()

# ── Session setup ──────────────────────────────────────────────────────────────
username     = st.session_state["username"]
display_name = st.session_state.get("name", username)

_load_after_login(username)
_check_alerts()
_check_morning_brief(username)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown(f"""
    <div class='y-sidebar-header'>
      <div style='width:30px;height:30px;flex-shrink:0;
                  background:linear-gradient(135deg,#4f8ef7,#9c6cff);
                  border-radius:8px;
                  display:flex;align-items:center;justify-content:center;
                  font-size:16px;line-height:1;
                  box-shadow:0 2px 8px rgba(79,142,247,0.3);'>🐵</div>
      <div>
        <div class='y-wordmark' style='font-size:13px;letter-spacing:-0.4px;'>The Bull Monkey</div>
        <div class='y-tagline'>AI Financial Intelligence</div>
      </div>
    </div>

    <!-- User badge -->
    <div class='y-user-badge'>
      <div style='font-size:9px;font-weight:700;color:var(--text-muted);letter-spacing:1px;text-transform:uppercase;margin-bottom:3px;font-family:"Space Grotesk",sans-serif;'>Signed in as</div>
      <div style='font-size:13px;font-weight:600;color:var(--text-primary);font-family:"Space Grotesk",sans-serif;'>{display_name}</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick search
    search_ticker = st.text_input(
        "search",
        placeholder="Search ticker  ⌘K",
        key="global_search",
        label_visibility="collapsed",
    )
    if search_ticker and search_ticker.strip():
        st.session_state.analyze_ticker = search_ticker.strip().upper()
        st.session_state._go_analysis = True

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    # Save + Sign out
    from utils.db import save_user_data, is_configured
    c1, c2 = st.columns(2)
    with c1:
        if is_configured():
            if st.button("Save", use_container_width=True):
                if save_user_data(username):
                    st.toast("Saved", icon="✓")
                else:
                    st.error("Save failed")
    with c2:
        authenticator.logout("Sign out", location="sidebar")

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    if not is_configured():
        st.markdown("<div style='font-size:10px;color:var(--text-muted);padding:0 4px;font-family:\"Space Grotesk\",sans-serif;'>Cloud sync not configured</div>",
                    unsafe_allow_html=True)


# ── Navigation ─────────────────────────────────────────────────────────────────
pages = {
    "Dashboard": [
        st.Page("pages/01_Main.py",            title="Overview",         icon="⬡",  default=True),
        st.Page("pages/21_Morning_Brief.py",   title="Morning Brief",    icon="☀️"),
    ],
    "Portfolio": [
        st.Page("pages/06_Portfolio.py",       title="Holdings",         icon="💼"),
        st.Page("pages/18_Watchlist.py",       title="Watchlist",        icon="◎"),
        st.Page("pages/14_Alerts.py",          title="Alerts",           icon="◈"),
        st.Page("pages/02_Profile.py",         title="Profile",          icon="◉"),
    ],
    "Research": [
        st.Page("pages/04_Analysis.py",        title="Deep Analysis",    icon="◆"),
        st.Page("pages/03_Screener.py",        title="Screener",         icon="◇"),
        st.Page("pages/05_Financials.py",      title="Financials",       icon="◈"),
        st.Page("pages/11_ETF_Analysis.py",    title="ETF Analysis",     icon="◉"),
        st.Page("pages/16_Market_Brief.py",    title="Market Intel",     icon="◎"),
        st.Page("pages/07_Sectors.py",         title="Sectors",          icon="⬡"),
        st.Page("pages/13_Calendar.py",        title="Calendar",         icon="◫"),
    ],
    "AI Studio": [
        st.Page("pages/19_AI_Chat.py",         title="AI Chat",          icon="◈"),
        st.Page("pages/08_Memos.py",           title="Memos",            icon="◇"),
        st.Page("pages/10_Recommendations.py", title="AI Picks",         icon="◆"),
        st.Page("pages/17_Transcript.py",      title="Transcript",       icon="◎"),
    ],
    "Tools": [
        st.Page("pages/09_History.py",         title="History",          icon="◫"),
        st.Page("pages/12_Chart_Builder.py",   title="Charts",           icon="◉"),
        st.Page("pages/15_Backtester.py",      title="Backtester",       icon="◇"),
        st.Page("pages/20_Settings.py",        title="Settings",         icon="⬡"),
    ],
}

pg = st.navigation(pages)

if st.session_state.pop("_go_analysis", False):
    st.switch_page("pages/04_Analysis.py")

pg.run()

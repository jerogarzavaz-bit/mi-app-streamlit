import streamlit as st
from pathlib import Path
from utils.config import GLOBAL_CSS, theme_js


# ── Logo helpers ───────────────────────────────────────────────────────────────
def _logo_path(variant: str, theme: str | None = None) -> Path | None:
    """Return Path to logo file if it exists, else None.
    variant: 'mascot' | 'icon'
    theme:   'dark' | 'light' | None → uses session theme
    """
    if theme is None:
        theme = st.session_state.get("theme", "dark")
    p = Path(f"assets/{variant}_{theme}.png")
    return p if p.exists() else None

_icon_path = _logo_path("icon", "dark")  # always dark for browser tab icon
st.set_page_config(
    page_title="The Bull Monkey",
    page_icon=str(_icon_path) if _icon_path else "🐵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Inject theme attribute on <body> so CSS token overrides apply
_theme = st.session_state.get("theme", "dark")
st.markdown(theme_js(_theme), unsafe_allow_html=True)

# ── Login page extra styles ────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes loginIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes breathe {
    0%, 100% { transform: scale(1) translateY(0px); }
    50%       { transform: scale(1.02) translateY(-6px); }
}
.login-wrap { animation: loginIn 0.4s cubic-bezier(0.16,1,0.3,1) both; }

div[data-testid="stForm"] {
    max-width: 360px;
    margin: 0 auto;
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: 20px;
    padding: 28px 26px 22px;
    box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.04);
}
div[data-testid="stForm"] input {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-default) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 9px 13px !important;
    transition: all 0.12s !important;
}
div[data-testid="stForm"] input:focus {
    border-color: rgba(97,114,243,0.5) !important;
    box-shadow: 0 0 0 3px rgba(97,114,243,0.07) !important;
    background: var(--bg-overlay) !important;
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
        "theme":          "dark",
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
    theme = st.session_state.get("theme", "dark")

    # ── Top hero ───────────────────────────────────────────────────────────────
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    st.markdown("<div style='height:56px;'></div>", unsafe_allow_html=True)

    mascot = _logo_path("mascot", theme)
    if mascot:
        # Real mascot image
        _, hero_col, _ = st.columns([1, 1.1, 1])
        with hero_col:
            st.image(str(mascot), width=220)
    else:
        # Fallback animated emoji
        st.markdown("""
        <div style='text-align:center;'>
          <div style='display:inline-flex;align-items:center;justify-content:center;
                      width:80px;height:80px;
                      background:linear-gradient(145deg,#18181B 0%,#1F1F24 100%);
                      border:1px solid rgba(97,114,243,0.2);
                      border-radius:22px;
                      box-shadow:0 0 0 1px rgba(255,255,255,0.04),
                                 0 8px 32px rgba(0,0,0,0.5),
                                 0 0 40px rgba(97,114,243,0.1);
                      margin:0 auto 0;
                      font-size:40px;line-height:1;
                      animation:breathe 5s ease-in-out infinite;'>🐵</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;padding:20px 0 32px;'>
      <div style='font-family:"Syne","Inter",sans-serif;font-size:26px;font-weight:800;
                  color:#FAFAFA;letter-spacing:-1px;line-height:1.1;margin-bottom:6px;'>
        The Bull Monkey
      </div>
      <div style='font-size:10.5px;color:#3F3F46;letter-spacing:2px;font-weight:500;
                  text-transform:uppercase;font-family:"Inter",sans-serif;'>
        AI Financial Intelligence
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Login form ─────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 1.35, 1])
    with col2:
        authenticator.login(fields={
            "Form name": "Sign in",
            "Username":  "Username",
            "Password":  "Password",
            "Login":     "Continue →",
        })
        status = st.session_state.get("authentication_status")
        if status is False:
            st.error("Incorrect credentials.")

    st.markdown("""
    <div style='text-align:center;color:#3F3F46;font-size:10.5px;margin-top:56px;
                font-family:"Inter",sans-serif;letter-spacing:0.2px;'>
      The Bull Monkey &nbsp;·&nbsp; Powered by Claude AI &nbsp;·&nbsp; © 2025
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


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
    # Branding — icon logo or emoji fallback
    _sb_icon = _logo_path("icon")
    if _sb_icon:
        _ic, _tx = st.columns([1, 3.5])
        with _ic:
            st.image(str(_sb_icon), width=32)
        with _tx:
            st.markdown(f"""
            <div style='padding-top:4px;'>
              <div class='y-wordmark'>The Bull Monkey</div>
              <div class='y-tagline'>AI Financial Intelligence</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='y-sidebar-header'>
          <div style='width:28px;height:28px;flex-shrink:0;
                      background:linear-gradient(145deg,#1F1F24,#27272A);
                      border:1px solid rgba(97,114,243,0.2);
                      border-radius:8px;
                      display:flex;align-items:center;justify-content:center;
                      font-size:15px;line-height:1;'>🐵</div>
          <div>
            <div class='y-wordmark'>The Bull Monkey</div>
            <div class='y-tagline'>AI Financial Intelligence</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='y-user-badge'>
      <div style='font-size:9px;font-weight:500;color:var(--text-disabled);letter-spacing:0.8px;text-transform:uppercase;margin-bottom:3px;font-family:"Inter",sans-serif;'>Signed in as</div>
      <div style='font-size:12.5px;font-weight:500;color:var(--text-secondary);font-family:"Inter",sans-serif;letter-spacing:-0.1px;'>{display_name}</div>
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

    # Theme toggle
    _current_theme = st.session_state.get("theme", "dark")
    _theme_label   = "☀️  Light" if _current_theme == "dark" else "🌙  Dark"
    if st.button(_theme_label, use_container_width=True, key="sb_theme_toggle"):
        st.session_state.theme = "light" if _current_theme == "dark" else "dark"
        st.rerun()

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    if not is_configured():
        st.markdown("<div style='font-size:10px;color:var(--text-muted);padding:0 4px;font-family:\"Space Grotesk\",sans-serif;'>Cloud sync not configured</div>",
                    unsafe_allow_html=True)


# ── Navigation ─────────────────────────────────────────────────────────────────
from utils.auth import is_guest as _is_guest

pages = [
    st.Page("pages/01_Main.py",           title="Home",           icon="🏠", default=True),
    st.Page("pages/hub_portfolio.py",     title="My Portfolio",   icon="💼"),
    st.Page("pages/hub_discover.py",      title="Discover",       icon="🔭"),
    st.Page("pages/hub_intelligence.py",  title="Intelligence",   icon="📡"),
    st.Page("pages/hub_ai.py",            title="AI Workspace",   icon="🤖"),
]
if not _is_guest():
    pages.append(st.Page("pages/20_Settings.py", title="Settings", icon="⚙️"))

pg = st.navigation(pages)

if st.session_state.pop("_go_analysis", False):
    st.switch_page("pages/hub_ai.py")

pg.run()

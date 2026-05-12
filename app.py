import streamlit as st
from utils.config import GLOBAL_CSS

st.set_page_config(
    page_title="Stock Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
/* Login page centering */
div[data-testid="stForm"] { max-width: 420px; margin: 0 auto; }
div[data-testid="stForm"] input {
    background: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: white !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session defaults ──────────────────────────────────────────────────────────
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


# ── Login page ────────────────────────────────────────────────────────────────
def _show_login(authenticator):
    st.markdown("""
    <div style='text-align:center; padding: 60px 0 32px 0;'>
      <div style='font-size: 56px;'>📊</div>
      <div style='font-size: 32px; font-weight: 700; color: white; margin-top: 8px;'>
        Stock Analyzer Pro
      </div>
      <div style='font-size: 15px; color: #1f77b4; margin-top: 6px; letter-spacing: 1px;'>
        INSTITUTIONAL-GRADE ANALYSIS
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        authenticator.login(fields={
            "Form name": "Sign in to your account",
            "Username":  "Username",
            "Password":  "Password",
            "Login":     "Sign In",
        })

        status = st.session_state.get("authentication_status")
        if status is False:
            st.error("Incorrect username or password. Try again.")

    st.markdown("""
    <div style='text-align:center; color:#555; font-size:12px; margin-top:48px;'>
      Stock Analyzer Pro &nbsp;·&nbsp; Powered by Claude AI &amp; yfinance
    </div>
    """, unsafe_allow_html=True)


# ── Load user data from Firestore after login ─────────────────────────────────
def _load_after_login(username: str):
    if st.session_state.get(f"_loaded_{username}"):
        return
    from utils.db import load_user_data, is_configured
    if is_configured():
        load_user_data(username)
    st.session_state[f"_loaded_{username}"] = True


# ── Alert checker (runs on every page load) ───────────────────────────────────
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
                st.toast(f"🔔 Alert: {a['ticker']} {a['condition']} "
                         f"${a['threshold']:.2f} — now ${price:.2f}", icon="🔔")
        except Exception:
            pass


# ── Main ──────────────────────────────────────────────────────────────────────
from utils.auth import get_authenticator

authenticator = get_authenticator()

# Check login status (cookie or form submission)
auth_status = st.session_state.get("authentication_status")

# Not logged in → show login page only
if auth_status is not True:
    _show_login(authenticator)
    st.stop()

# ── Logged in ─────────────────────────────────────────────────────────────────
username     = st.session_state["username"]
display_name = st.session_state.get("name", username)

# Load this user's saved data (once per session)
_load_after_login(username)

# Check alerts
_check_alerts()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:12px 0 4px 0;border-bottom:1px solid #222;margin-bottom:6px;'>
      <span style='font-size:24px;'>📊</span>
      <div style='font-size:12px;font-weight:700;color:#1f77b4;letter-spacing:3px;margin-top:4px;'>
        ANALYST
      </div>
    </div>
    <div style='text-align:center;padding:8px 0 10px 0;border-bottom:1px solid #222;margin-bottom:4px;'>
      <div style='font-size:13px;color:#888;'>Signed in as</div>
      <div style='font-size:14px;font-weight:700;color:white;'>{display_name}</div>
    </div>
    """, unsafe_allow_html=True)

    # Save button
    from utils.db import save_user_data, is_configured
    if is_configured():
        if st.button("💾 Save my data", use_container_width=True):
            if save_user_data(username):
                st.success("Saved!")
            else:
                st.error("Save failed.")
    else:
        st.caption("☁️ Cloud sync: not configured")

    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)
    authenticator.logout("Sign Out", location="sidebar")

# ── Navigation ────────────────────────────────────────────────────────────────
pages = [
    st.Page("pages/01_Main.py",            title="Main",            icon="🏠", default=True),
    st.Page("pages/02_Profile.py",         title="Profile",         icon="👤"),
    st.Page("pages/03_Screener.py",        title="Screener",        icon="🔍"),
    st.Page("pages/04_Analysis.py",        title="Analysis",        icon="📊"),
    st.Page("pages/05_Financials.py",      title="Financials",      icon="💰"),
    st.Page("pages/06_Portfolio.py",       title="Portfolio",       icon="💼"),
    st.Page("pages/07_Sectors.py",         title="Sectors",         icon="🌐"),
    st.Page("pages/08_Memos.py",           title="Memos",           icon="📝"),
    st.Page("pages/09_History.py",         title="History",         icon="📚"),
    st.Page("pages/10_Recommendations.py", title="Recommendations", icon="⭐"),
    st.Page("pages/11_ETF_Analysis.py",    title="ETF Analysis",    icon="📈"),
    st.Page("pages/12_Chart_Builder.py",   title="Chart Builder",   icon="🔧"),
    st.Page("pages/13_Calendar.py",        title="Calendar",        icon="📅"),
    st.Page("pages/14_Alerts.py",          title="Alerts",          icon="🔔"),
    st.Page("pages/15_Backtester.py",      title="Backtester",      icon="⚡"),
    st.Page("pages/16_Market_Brief.py",    title="Market Brief",    icon="📰"),
    st.Page("pages/17_Transcript.py",      title="Transcript",      icon="🎙️"),
    st.Page("pages/18_Watchlist.py",       title="Watchlist",       icon="👁️"),
    st.Page("pages/19_AI_Chat.py",         title="AI Chat",         icon="🤖"),
    st.Page("pages/20_Settings.py",        title="Settings",        icon="⚙️"),
]

pg = st.navigation(pages)
pg.run()

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
@keyframes loginFadeIn {
    from { opacity: 0; transform: translateY(24px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes floatOrb {
    0%, 100% { transform: translateY(0px) scale(1); }
    50%       { transform: translateY(-18px) scale(1.04); }
}
@keyframes rotateSlow {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
.login-wrap {
    animation: loginFadeIn 0.6s cubic-bezier(0.16,1,0.3,1) both;
}
div[data-testid="stForm"] {
    max-width: 400px;
    margin: 0 auto;
    background: linear-gradient(135deg, rgba(17,21,32,0.95) 0%, rgba(14,16,24,0.98) 100%);
    border: 1px solid rgba(31,119,180,0.25);
    border-radius: 18px;
    padding: 32px 32px 24px 32px;
    box-shadow: 0 24px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(31,119,180,0.08),
                inset 0 1px 0 rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
}
div[data-testid="stForm"] input {
    background: rgba(6,8,16,0.8) !important;
    border: 1px solid rgba(31,119,180,0.3) !important;
    color: #e8edf8 !important;
    border-radius: 9px !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stForm"] input:focus {
    border-color: rgba(31,119,180,0.7) !important;
    box-shadow: 0 0 0 3px rgba(31,119,180,0.15) !important;
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
    <div class='login-wrap'>
    <div style='text-align:center; padding: 56px 0 36px 0;'>
      <div style='position:relative;display:inline-block;margin-bottom:16px;'>
        <div style='
          width:80px;height:80px;
          background:linear-gradient(135deg,#1f77b4 0%,#7c3aed 100%);
          border-radius:22px;
          display:flex;align-items:center;justify-content:center;
          font-size:40px;
          box-shadow:0 8px 32px rgba(31,119,180,0.4),0 0 0 1px rgba(124,58,237,0.3);
          margin:0 auto;
          animation: floatOrb 4s ease-in-out infinite;
        '>📊</div>
      </div>
      <div style='
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #e8edf8 30%, #7eb8e8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.8px;
        margin-bottom: 6px;
      '>Stock Analyzer Pro</div>
      <div style='
        font-size: 11px;
        color: #4a90d9;
        letter-spacing: 3px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
      '>Institutional-Grade Analysis</div>
      <div style='display:flex;justify-content:center;gap:20px;margin-top:14px;'>
        <span style='color:#3a5a7a;font-size:11px;'>⚡ Real-Time Data</span>
        <span style='color:#3a5a7a;font-size:11px;'>🤖 Claude AI</span>
        <span style='color:#3a5a7a;font-size:11px;'>☁️ Cloud Sync</span>
      </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        authenticator.login(fields={
            "Form name": "Sign in to your account",
            "Username":  "Username",
            "Password":  "Password",
            "Login":     "Sign In →",
        })

        status = st.session_state.get("authentication_status")
        if status is False:
            st.error("Incorrect username or password. Please try again.")

    st.markdown("""
    <div style='text-align:center; color:#2a3a5a; font-size:11px; margin-top:52px; letter-spacing:0.5px;'>
      Stock Analyzer Pro &nbsp;·&nbsp; Powered by Claude AI &amp; yfinance &nbsp;·&nbsp; © 2025
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
    <div style='padding:16px 4px 14px 4px;border-bottom:1px solid rgba(31,119,180,0.15);margin-bottom:8px;'>
      <div style='display:flex;align-items:center;gap:10px;'>
        <div style='
          width:36px;height:36px;flex-shrink:0;
          background:linear-gradient(135deg,#1f77b4,#7c3aed);
          border-radius:10px;
          display:flex;align-items:center;justify-content:center;
          font-size:18px;
          box-shadow:0 4px 12px rgba(31,119,180,0.35);
        '>📊</div>
        <div>
          <div style='font-size:13px;font-weight:800;color:#c8d8f0;letter-spacing:-0.3px;'>Stock Analyzer</div>
          <div style='font-size:9px;font-weight:700;color:#4a90d9;letter-spacing:2px;'>PRO</div>
        </div>
      </div>
    </div>
    <div style='
      margin:0 0 12px 0;
      padding:10px 12px;
      background:rgba(31,119,180,0.08);
      border:1px solid rgba(31,119,180,0.18);
      border-radius:10px;
    '>
      <div style='font-size:10px;color:#4a6a8a;font-weight:600;letter-spacing:0.5px;margin-bottom:3px;'>SIGNED IN AS</div>
      <div style='font-size:14px;font-weight:700;color:#c8d8f0;'>{display_name}</div>
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

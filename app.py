import streamlit as st
from utils.config import GLOBAL_CSS

st.set_page_config(
    page_title="Stock Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def _init():
    defaults = {
        "api_keys":        {"anthropic": "", "alpha_vantage": "", "fred": "", "fmp": ""},
        "portfolio":       [],
        "watchlists":      {},
        "analyses":        [],
        "screen_history":  [],
        "profile":         {},
        "alerts":          [],
        "chat_messages":   [],
        "period":          "1y",
        "periodo_label":   "1 año",
        "data_provider":   "yfinance",
        "analyze_ticker":  "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── Check & fire alerts on every page load ──────────────────────────────────
def _check_alerts():
    from utils.data import get_stock_data
    fired = []
    for a in st.session_state.alerts:
        if a.get("triggered"):
            continue
        try:
            info, _ = get_stock_data(a["ticker"], "5d")
            if info is None:
                continue
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            cond  = a["condition"]
            thr   = a["threshold"]
            hit   = (cond == "Price >" and price > thr) or \
                    (cond == "Price <" and price < thr)
            if hit:
                a["triggered"]     = True
                a["triggered_at"]  = price
                fired.append(a)
        except Exception:
            pass
    for a in fired:
        st.toast(f"🔔 Alert: {a['ticker']} {a['condition']} ${a['threshold']:.2f} — now ${a['triggered_at']:.2f}", icon="🔔")

_check_alerts()

# ── Navigation ───────────────────────────────────────────────────────────────
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

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px 0;border-bottom:1px solid #222;margin-bottom:8px;'>
      <span style='font-size:26px;'>📊</span>
      <div style='font-size:13px;font-weight:700;color:#1f77b4;letter-spacing:3px;margin-top:4px;'>ANALYST</div>
    </div>""", unsafe_allow_html=True)

pg = st.navigation(pages)
pg.run()

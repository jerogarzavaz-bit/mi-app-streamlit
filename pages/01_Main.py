import streamlit as st
from datetime import date
from utils.data import get_market_overview
from utils.config import COLOR_SUCCESS, COLOR_DANGER

# ── Header ────────────────────────────────────────────────────────────────────
today = date.today().strftime("%A, %B %d, %Y")
st.markdown(f"""
<div class='page-header'>
  <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;'>
    <div>
      <div class='page-title'>📊 Stock Analyzer Pro</div>
      <div class='page-subtitle'>Institutional-Grade Analysis · Powered by Claude AI</div>
    </div>
    <div style='display:flex;align-items:center;gap:10px;'>
      <span class='live-badge'>Live</span>
      <span style='color:#4a5a7a;font-size:12px;'>{today}</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Market Overview ────────────────────────────────────────────────────────────
st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;'>Market Pulse</div>", unsafe_allow_html=True)

with st.spinner(""):
    mkt = get_market_overview()

cols = st.columns(len(mkt))
for col, (name, d) in zip(cols, mkt.items()):
    pct   = d["change_pct"]
    color = "#22c55e" if pct >= 0 else "#ef4444"
    arrow = "▲" if pct >= 0 else "▼"
    price = d["price"]

    fmt = f"${price:,.2f}" if name in ("Gold", "Oil WTI") else \
          f"{price:.2f}%"  if name in ("10Y Yield",) else \
          f"{price:,.2f}"

    col.metric(
        label=name,
        value=fmt,
        delta=f"{arrow} {abs(pct):.2f}%",
        delta_color="normal",
    )

st.divider()

# ── Portfolio Snapshot ─────────────────────────────────────────────────────────
st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;'>My Portfolio</div>", unsafe_allow_html=True)
portfolio = st.session_state.get("portfolio", [])

if not portfolio:
    st.markdown("""
    <div class='card' style='text-align:center;color:#4a6a8a;padding:36px;'>
      <div style='font-size:32px;margin-bottom:10px;'>💼</div>
      <div style='font-size:15px;font-weight:600;color:#6a8aaa;margin-bottom:6px;'>No holdings yet</div>
      <div style='font-size:13px;'>Go to <strong style='color:#7eb8e8;'>Portfolio</strong> to add your first position</div>
    </div>""", unsafe_allow_html=True)
    if st.button("➕ Add Holdings", type="primary"):
        st.switch_page("pages/06_Portfolio.py")
else:
    total = sum(h.get("current_value", 0) for h in portfolio)
    cost  = sum(h.get("cost_basis", 0)    for h in portfolio)
    gain  = total - cost
    pct   = (gain / cost * 100) if cost > 0 else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Value",     f"${total:,.2f}")
    c2.metric("Total Cost",      f"${cost:,.2f}")
    c3.metric("Total Gain/Loss", f"${gain:+,.2f}", f"{pct:+.2f}%")
    c4.metric("Positions",       len(portfolio))

st.divider()

# ── Quick Start & Features ─────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;'>🚀 Quick Start</div>", unsafe_allow_html=True)
    steps = [
        ("1", "Add your holdings in the **Portfolio** page"),
        ("2", "Run the **Screener** to find top-rated stocks"),
        ("3", "Deep **Analysis** with Claude AI scoring"),
        ("4", "Generate professional **Investment Memos**"),
    ]
    for num, text in steps:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:14px;margin-bottom:12px;'>
          <div class='step-num'>{num}</div>
          <span style='color:#8aadcc;font-size:13px;'>{text}</span>
        </div>""", unsafe_allow_html=True)

with col_b:
    st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;'>📖 Features</div>", unsafe_allow_html=True)
    features = [
        ("🔍", "Screener",      "Rank stocks by composite score"),
        ("📊", "Analysis",      "6-dimension deep dive + Claude AI"),
        ("💼", "Portfolio",     "Track positions & rebalance"),
        ("🌐", "Sectors",       "Macro trends & sector leaders"),
        ("📝", "Memos",         "Professional PDF-quality reports"),
        ("⚡", "Backtester",    "Strategy simulation & metrics"),
    ]
    for icon, name, desc in features:
        st.markdown(f"""
        <div class='feature-card'>
          <div class='feature-icon'>{icon}</div>
          <div>
            <div class='feature-name'>{name}</div>
            <div class='feature-desc'>{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ── Recent Analyses ────────────────────────────────────────────────────────────
st.markdown("<div style='font-size:11px;font-weight:700;color:#4a6a8a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;'>Recent Analyses</div>", unsafe_allow_html=True)
analyses = st.session_state.get("analyses", [])

if not analyses:
    st.markdown("""
    <div class='card' style='text-align:center;color:#4a6a8a;padding:28px;'>
      <div style='font-size:26px;margin-bottom:8px;'>📚</div>
      <div style='font-size:13px;'>No analyses yet. Go to <strong style='color:#7eb8e8;'>Analysis</strong> to analyze your first stock.</div>
    </div>""", unsafe_allow_html=True)
else:
    for a in reversed(analyses[-5:]):
        rec   = a.get("rec", "")
        score = a.get("composite", 0)
        tier_class = "tier1" if score >= 6.5 else "tier2" if score >= 4.0 else "tier3"
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        c1.markdown(f"**{a['ticker']}** <span style='color:#4a6a8a;font-size:12px;'>{a.get('name','')}</span>", unsafe_allow_html=True)
        c2.markdown(f"<span class='{tier_class}'>{rec}</span>", unsafe_allow_html=True)
        c3.markdown(f"<span class='stat-pill'>{score:.1f}/10</span>", unsafe_allow_html=True)
        c4.markdown(f"<span style='color:#4a5a7a;font-size:12px;'>{a.get('date','')}</span>", unsafe_allow_html=True)

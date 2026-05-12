import streamlit as st
from datetime import date
from utils.data import get_market_overview
from utils.config import COLOR_SUCCESS, COLOR_DANGER

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class='page-header'>
  <div class='page-title'>📊 Stock Analyzer Pro</div>
  <div class='page-subtitle'>Institutional-Grade Analysis</div>
</div>""", unsafe_allow_html=True)

today = date.today().strftime("%A, %B %d, %Y")
st.caption(today)

# ── Market Overview ───────────────────────────────────────────────────────────
st.subheader("Market Overview")

with st.spinner("Loading market data…"):
    mkt = get_market_overview()

cols = st.columns(len(mkt))
for col, (name, d) in zip(cols, mkt.items()):
    pct   = d["change_pct"]
    color = COLOR_SUCCESS if pct >= 0 else COLOR_DANGER
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

# ── Portfolio Snapshot ────────────────────────────────────────────────────────
st.subheader("Portfolio Snapshot")
portfolio = st.session_state.get("portfolio", [])

if not portfolio:
    st.markdown("""
    <div class='card' style='text-align:center;color:#888;padding:32px;'>
      No holdings yet. Go to <strong>Portfolio</strong> to add your positions.
    </div>""", unsafe_allow_html=True)
    if st.button("➕ Add Holdings"):
        st.switch_page("pages/06_Portfolio.py")
else:
    total = sum(h.get("current_value", 0) for h in portfolio)
    cost  = sum(h.get("cost_basis", 0)    for h in portfolio)
    gain  = total - cost
    pct   = (gain / cost * 100) if cost > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Value",  f"${total:,.2f}")
    c2.metric("Total Gain/Loss", f"${gain:+,.2f}", f"{pct:+.2f}%")
    c3.metric("Positions", len(portfolio))

st.divider()

# ── Quick Start ────────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🚀 Quick Start")
    steps = [
        ("1", "Add your holdings in the **Portfolio** page"),
        ("2", "Run a **Screener** to find top stocks"),
        ("3", "Perform **Deep Analysis** on candidates"),
        ("4", "Generate **Investment Memos**"),
    ]
    for num, text in steps:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px;'>
          <div style='background:#1f77b4;color:white;border-radius:50%;width:26px;height:26px;
               display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;'>{num}</div>
          <span style='color:#ccc;'>{text}</span>
        </div>""", unsafe_allow_html=True)

with col_b:
    st.subheader("📖 Getting Started")
    features = [
        ("🔍 Screener",       "Rank stocks by composite score"),
        ("📊 Analysis",       "Deep dive with Claude AI"),
        ("💼 Portfolio",      "Track & rebalance holdings"),
        ("🌐 Sectors",        "Macro & sector leaders"),
        ("📝 Memos",          "Generate PDF reports"),
        ("📚 History",        "Past analyses archive"),
    ]
    for icon_name, desc in features:
        st.markdown(f"**{icon_name}** — {desc}")

st.divider()

# ── Recent Analyses ────────────────────────────────────────────────────────────
st.subheader("Recent Analyses")
analyses = st.session_state.get("analyses", [])

if not analyses:
    st.markdown("""
    <div class='card' style='text-align:center;color:#888;padding:28px;'>
      No analyses yet. Go to <strong>Analysis</strong> to analyze your first stock.
    </div>""", unsafe_allow_html=True)
else:
    for a in reversed(analyses[-5:]):
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"**{a['ticker']}** — {a.get('name','')}")
        c2.write(a.get("rec", ""))
        c3.write(a.get("date", ""))

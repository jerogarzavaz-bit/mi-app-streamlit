import streamlit as st
from datetime import date
from utils.data import get_market_overview, get_sector_performance
from utils.plots import sector_bar
from utils.ai import has_key, no_key_banner, market_brief

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📰 AI Daily Market Brief</div>
</div>""", unsafe_allow_html=True)
st.caption(f"{date.today().strftime('%A, %B %d, %Y')} — Powered by Claude AI with live market data")

if not has_key():
    no_key_banner("Market Brief")

# ── Controls ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
extended     = col1.checkbox("Extended Thinking (deeper analysis, ~2x slower)")
incl_port    = col2.checkbox("Include My Portfolio")

with st.expander("📧 Email & Schedule Settings"):
    st.info("Email delivery coming soon. For now, copy the brief text manually.")
    email = st.text_input("Your email (optional)", placeholder="you@example.com")

gen = st.button("🔮 Generate Fresh Brief", type="primary", disabled=not has_key())

st.divider()

# ── Market Snapshot ────────────────────────────────────────────────────────────
st.subheader("Market Snapshot")
with st.spinner("Loading market data…"):
    mkt = get_market_overview()

cols = st.columns(len(mkt))
for col, (name, d) in zip(cols, mkt.items()):
    pct = d["change_pct"]; p = d["price"]
    fmt = f"${p:,.2f}" if name in ("Gold","Oil WTI") else \
          f"{p:.2f}%" if "Yield" in name else f"{p:,.2f}"
    col.metric(name, fmt, f"{'▲' if pct>=0 else '▼'} {abs(pct):.2f}%")

# ── Sector Performance ────────────────────────────────────────────────────────
st.subheader("Today's Sector Performance")
with st.spinner("Loading sectors…"):
    sec_ret = get_sector_performance("1mo")
st.plotly_chart(sector_bar(sec_ret), use_container_width=True)

st.divider()

# ── AI Brief ──────────────────────────────────────────────────────────────────
st.subheader("AI Brief")
if not has_key():
    st.info("Add your Anthropic API key in **Settings** to generate the brief.")
elif gen:
    with st.spinner("Generating brief with Claude AI…" + (" (Extended Thinking enabled)" if extended else "")):
        result = market_brief(mkt, extended=extended)
    if result:
        st.markdown(result)
        st.download_button("⬇️ Download Brief",
                           result, file_name=f"brief_{date.today().isoformat()}.md")
    else:
        st.error("Error generating brief. Check your API key.")
else:
    st.info("Click **Generate Fresh Brief** to get today's AI market analysis.")

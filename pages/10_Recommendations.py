import streamlit as st
from utils.ai import has_key, no_key_banner, generate_recommendations
from utils.config import TICKERS_US

st.markdown("""
<div class='page-header'>
  <div class='page-title'>⭐ Daily Stock Recommendations</div>
  <div class='page-subtitle'>AI-powered stock picks updated on demand</div>
</div>""", unsafe_allow_html=True)

if not has_key():
    no_key_banner("AI recommendations")
    st.stop()

# Source selection
wls = st.session_state.get("watchlists", {})
source = st.radio("Ticker source:", ["Default Watchlist (US)", "Custom"] + list(wls.keys()), horizontal=True)

if source == "Default Watchlist (US)":
    tickers = TICKERS_US
elif source == "Custom":
    raw = st.text_input("Enter tickers:", ", ".join(TICKERS_US[:10]))
    tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
else:
    tickers = wls.get(source, TICKERS_US)

st.caption(f"Using {len(tickers)} tickers: {', '.join(tickers[:10])}{'…' if len(tickers) > 10 else ''}")

profile = st.session_state.get("profile", {})
if not profile:
    st.warning("Complete your **Profile** to get personalized picks.")

if st.button("🔮 Generate Today's Recommendations", type="primary"):
    with st.spinner("Analyzing opportunities with Claude AI…"):
        result = generate_recommendations(tickers, profile)
    if result:
        st.markdown("---")
        st.markdown(result)
        from datetime import date
        st.caption(f"Generated on {date.today().isoformat()}")
    else:
        st.error("Error generating recommendations. Check your API key.")

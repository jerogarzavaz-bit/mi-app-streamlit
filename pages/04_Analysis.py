import streamlit as st
from utils.data import get_stock_data
from utils.plots import price_chart, candlestick_chart
from utils.screener import score_stock
from utils.ai import has_key, no_key_banner, analyze_stock
from utils.config import COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING
from datetime import date

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📊 Deep Stock Analysis</div>
  <div class='page-subtitle'>Institutional-grade analysis powered by real-time data + Claude AI</div>
</div>""", unsafe_allow_html=True)

if not has_key():
    st.success("💡 Go to **Settings** to add your Anthropic API key and unlock AI analysis.")

# ── Input ─────────────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([3, 1])
default_ticker = st.session_state.get("analyze_ticker", "")
ticker_input = col_in.text_input("Ticker symbol", value=default_ticker,
                                  placeholder="e.g. NVDA, AAPL, AMXL.MX")
period = st.session_state.get("period", "1y")

analyze = col_btn.button("Analyze", type="primary", use_container_width=True)

if not ticker_input:
    st.info("Enter a ticker symbol above to begin analysis.")
    st.stop()

ticker = ticker_input.strip().upper()
st.session_state.analyze_ticker = ticker

# ── Fetch Data ────────────────────────────────────────────────────────────────
with st.spinner(f"Loading data for {ticker}…"):
    info, hist = get_stock_data(ticker, period)

if info is None or hist is None or len(hist) == 0:
    st.error(f"Could not retrieve data for **{ticker}**. Check the ticker symbol and try again.")
    st.stop()

# ── Header Metrics ────────────────────────────────────────────────────────────
price    = info.get("currentPrice") or info.get("regularMarketPrice") or hist["Close"].iloc[-1]
prev     = info.get("previousClose", price) or price
delta    = price - prev
delta_p  = delta / prev * 100 if prev else 0
name     = info.get("longName", ticker)

st.markdown(f"## {ticker} — {name}")

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Price",       f"${price:.2f}", f"{delta_p:+.2f}%")
pe = info.get("trailingPE")
c2.metric("P/E (TTM)",   f"{pe:.1f}" if pe else "N/A")
mc = info.get("marketCap", 0)
c3.metric("Market Cap",  f"${mc/1e9:.1f}B" if mc else "N/A")
c4.metric("52W High",    f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
c5.metric("52W Low",     f"${info.get('fiftyTwoWeekLow',  0):.2f}")
div = (info.get("dividendYield") or 0) * 100
c6.metric("Div Yield",   f"{div:.2f}%")

# ── Screener Scores ────────────────────────────────────────────────────────────
scores = score_stock(info, hist)
sc_cols = st.columns(7)
tier_color = COLOR_SUCCESS if scores["tier"] == 1 else COLOR_WARNING if scores["tier"] == 2 else COLOR_DANGER
sc_cols[0].metric("Composite", f"{scores['composite']}/10")
sc_cols[1].metric("Valuation",  scores["valuation"])
sc_cols[2].metric("Growth",     scores["growth"])
sc_cols[3].metric("Quality",    scores["quality"])
sc_cols[4].metric("Technical",  scores["technical"])
sc_cols[5].metric("Momentum",   scores["momentum"])
sc_cols[6].metric("Sentiment",  scores["sentiment"])
st.markdown(f"**Recommendation: <span style='color:{tier_color};font-size:20px;'>{scores['rec']}</span>**",
            unsafe_allow_html=True)

st.divider()

# ── Chart ─────────────────────────────────────────────────────────────────────
chart_type = st.radio("Chart type", ["Line + MAs", "Candlestick"], horizontal=True)
period_sel = st.select_slider("Period", options=["30d","100d","6mo","1y","2y","3y","5y"],
                               value=period)
if period_sel != period:
    st.session_state.period = period_sel
    st.rerun()

if chart_type == "Candlestick":
    st.plotly_chart(candlestick_chart(hist, ticker), use_container_width=True)
else:
    st.plotly_chart(price_chart(hist, ticker), use_container_width=True)

st.divider()

# ── Company Info ──────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)
with col_l:
    st.subheader("Company")
    st.write(f"**Sector:** {info.get('sector','N/A')}")
    st.write(f"**Industry:** {info.get('industry','N/A')}")
    st.write(f"**Country:** {info.get('country','N/A')}")
    st.write(f"**Employees:** {info.get('fullTimeEmployees','N/A'):,}" if isinstance(info.get('fullTimeEmployees'), int) else f"**Employees:** {info.get('fullTimeEmployees','N/A')}")
    st.write(f"**Website:** {info.get('website','N/A')}")
with col_r:
    st.subheader("Financials")
    c1, c2 = st.columns(2)
    c1.metric("Revenue Growth",  f"{(info.get('revenueGrowth') or 0)*100:.1f}%")
    c2.metric("Profit Margin",   f"{(info.get('profitMargins') or 0)*100:.1f}%")
    c1.metric("ROE",             f"{(info.get('returnOnEquity') or 0)*100:.1f}%")
    c2.metric("D/E Ratio",       f"{info.get('debtToEquity','N/A')}")
    c1.metric("Current Ratio",   f"{info.get('currentRatio','N/A')}")
    c2.metric("Beta",            f"{info.get('beta','N/A')}")

summary = info.get("longBusinessSummary", "")
if summary:
    st.divider()
    with st.expander("Business Summary"):
        st.write(summary)

st.divider()

# ── AI Analysis ────────────────────────────────────────────────────────────────
st.subheader("🤖 AI Analysis")

if not has_key():
    no_key_banner("AI analysis")
else:
    if analyze or st.button("🔍 Run AI Analysis", type="primary"):
        analysis_box = st.empty()
        full_text = ""
        with st.spinner(f"Analyzing {ticker} with Claude AI…"):
            for chunk in analyze_stock(ticker):
                full_text += chunk
                analysis_box.markdown(full_text + "▌")
        analysis_box.markdown(full_text)

        # Save to history
        st.session_state.analyses.append({
            "ticker":  ticker,
            "name":    name,
            "date":    date.today().isoformat(),
            "rec":     scores["rec"],
            "score":   scores["composite"],
            "text":    full_text,
            "info":    {k: info.get(k) for k in ("sector","industry","currentPrice","marketCap")},
        })
        st.success("Analysis saved to History.")

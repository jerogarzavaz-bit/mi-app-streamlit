import streamlit as st
import pandas as pd
import numpy as np
from utils.data import get_stock_data
from utils.plots import multi_line, candlestick_chart, price_chart, scatter_peer

st.markdown("""
<div class='page-header'>
  <div class='page-title'>🔧 Chart Builder</div>
  <div class='page-subtitle'>Build custom charts to analyse price performance, fundamentals, and peer comparisons</div>
</div>""", unsafe_allow_html=True)

tab_price, tab_fund, tab_peer = st.tabs(["Price & Returns", "Fundamentals Over Time", "Peer Comparison"])

# ── Tab 1: Price & Returns ────────────────────────────────────────────────────
with tab_price:
    periods_map = {"1D":"1d","5D":"5d","1M":"1mo","3M":"3mo","6M":"6mo",
                   "YTD":"ytd","1Y":"1y","2Y":"2y","3Y":"3y","5Y":"5y"}
    sel_period = st.radio("Period", list(periods_map.keys()), horizontal=True, index=6)

    raw = st.text_input("Tickers", value="AAPL, MSFT, GOOGL, AMZN, META, NVDA", key="cb_tickers")
    tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

    col1, col2, col3 = st.columns(3)
    chart_type  = col1.radio("Chart Type", ["Line", "Candlestick"], horizontal=True)
    normalize   = col2.checkbox("Normalize (indexed to 100)")
    show_vol    = col3.checkbox("Show volume bars", value=True)

    if st.button("📊 Build Chart", type="primary", key="cb_build"):
        with st.spinner(f"Loading {len(tickers)} tickers…"):
            hist_data = {}
            for t in tickers[:10]:
                _, h = get_stock_data(t, periods_map[sel_period])
                if h is not None and len(h) > 0:
                    hist_data[t] = h

        if not hist_data:
            st.error("No data loaded.")
        elif len(hist_data) == 1 and chart_type == "Candlestick":
            t = list(hist_data.keys())[0]
            st.plotly_chart(candlestick_chart(hist_data[t], t), use_container_width=True)
        elif chart_type == "Line" or len(hist_data) > 1:
            st.plotly_chart(multi_line(hist_data, "Price Comparison", normalize=normalize),
                            use_container_width=True)
        else:
            t = list(hist_data.keys())[0]
            st.plotly_chart(price_chart(hist_data[t], t), use_container_width=True)
    else:
        st.info("Configure and click **Build Chart**.")

# ── Tab 2: Fundamentals ────────────────────────────────────────────────────────
with tab_fund:
    ticker_f = st.text_input("Ticker", placeholder="AAPL", key="cb_fund_ticker")
    metric_opts = [
        "P/E Ratio (TTM)", "P/B Ratio", "Profit Margin %",
        "ROE %", "Revenue Growth %", "EPS Diluted",
    ]
    metric = st.selectbox("Metric to plot", metric_opts)

    if ticker_f and st.button("Build Fundamentals Chart", key="cb_fund_build"):
        with st.spinner("Loading data…"):
            from utils.data import get_financial_statements
            data = get_financial_statements(ticker_f.upper())
        if not data:
            st.error("Could not load financials.")
        else:
            income = data["income"]
            if income is not None and not income.empty:
                cols = income.columns[:6]
                years = [str(c)[:4] for c in cols]
                import plotly.graph_objects as go
                from utils.plots import _DARK

                if "Revenue" in metric and "Total Revenue" in income.index:
                    vals = [income.loc["Total Revenue", c] / 1e9 for c in cols]
                    fig  = go.Figure(go.Bar(x=years, y=vals, marker_color="#1f77b4"))
                    fig.update_layout(**_DARK, title=f"{ticker_f.upper()} Revenue ($B)", height=360)
                    st.plotly_chart(fig, use_container_width=True)
                elif "Net Income" in metric and "Net Income" in income.index:
                    vals = [income.loc["Net Income", c] / 1e9 for c in cols]
                    fig  = go.Figure(go.Bar(x=years, y=vals,
                        marker_color=["#2ca02c" if v >= 0 else "#d62728" for v in vals]))
                    fig.update_layout(**_DARK, title=f"{ticker_f.upper()} Net Income ($B)", height=360)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Historical data for '{metric}' not available via yfinance.")
            else:
                st.error("No financial data available.")

# ── Tab 3: Peer Comparison ─────────────────────────────────────────────────────
with tab_peer:
    st.write("Compare current-snapshot valuation, profitability, and risk metrics across a peer group.")

    raw_p = st.text_input("Tickers (max 15)", value="AAPL,MSFT,GOOGL,AMZN,META,NVDA,TSLA,JPM,V,UNH",
                           key="cb_peer_tickers")
    peer_tickers = [t.strip().upper() for t in raw_p.split(",") if t.strip()][:15]

    col1, col2, col3 = st.columns(3)
    x_metric = col1.selectbox("X-axis", ["P/E Ratio","P/B Ratio","Forward P/E","EV/EBITDA"], index=0)
    y_metric = col2.selectbox("Y-axis", ["ROE %","Net Margin %","Revenue Growth %","Profit Margin %"], index=0)
    bubble   = col3.selectbox("Bubble size", ["Market Cap","Revenue","None"], index=0)

    if st.button("🔍 Build Peer Chart", type="primary", key="cb_peer_build"):
        with st.spinner("Loading peer data…"):
            rows = []
            for t in peer_tickers:
                info, _ = get_stock_data(t, "5d")
                if not info: continue
                rows.append({
                    "Ticker":           t,
                    "P/E Ratio":        info.get("trailingPE") or 0,
                    "P/B Ratio":        info.get("priceToBook") or 0,
                    "Forward P/E":      info.get("forwardPE") or 0,
                    "EV/EBITDA":        info.get("enterpriseToEbitda") or 0,
                    "ROE %":            (info.get("returnOnEquity") or 0) * 100,
                    "Net Margin %":     (info.get("profitMargins") or 0) * 100,
                    "Revenue Growth %": (info.get("revenueGrowth") or 0) * 100,
                    "Profit Margin %":  (info.get("profitMargins") or 0) * 100,
                    "Market Cap":       info.get("marketCap") or 0,
                    "Revenue":          info.get("totalRevenue") or 0,
                })
        if rows:
            df = pd.DataFrame(rows)
            size_col = "Market Cap" if bubble != "None" else "Market Cap"
            st.plotly_chart(scatter_peer(df, x_metric, y_metric, size_col, "Ticker"),
                            use_container_width=True)
            st.dataframe(df[["Ticker","P/E Ratio","P/B Ratio","ROE %","Net Margin %","Market Cap"]],
                         use_container_width=True, hide_index=True,
                         column_config={"Market Cap": st.column_config.NumberColumn(format="$,.0f")})
        else:
            st.error("Could not load data.")

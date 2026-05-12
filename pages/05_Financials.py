import streamlit as st
import pandas as pd
import numpy as np
from utils.data import get_financial_statements
from utils.plots import financials_bar

st.markdown("""
<div class='page-header'>
  <div class='page-title'>💰 Financial Statements</div>
  <div class='page-subtitle'>Annual &amp; quarterly 3-statement model with year-over-year trends</div>
</div>""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
ticker = col1.text_input("Ticker", placeholder="e.g. AAPL, MSFT, AMXL.MX",
                          value=st.session_state.get("analyze_ticker", ""))
load = col2.button("Load Statements", type="primary", use_container_width=True)

if not ticker:
    st.info("Enter a ticker symbol above to load its financial statements.")
    st.stop()

ticker = ticker.strip().upper()

with st.spinner(f"Loading financials for {ticker}…"):
    data = get_financial_statements(ticker)

if not data:
    st.error(f"Could not load financials for **{ticker}**.")
    st.stop()

freq = st.radio("Frequency", ["Annual", "Quarterly"], horizontal=True)
income    = data["income"]    if freq == "Annual" else data["income_q"]
balance   = data["balance"]   if freq == "Annual" else data["balance_q"]
cashflow  = data["cashflow"]  if freq == "Annual" else data["cash_q"]
info      = data["info"]

def _fmt_row(series: pd.Series) -> pd.Series:
    def fmt(v):
        if pd.isna(v): return "—"
        if abs(v) >= 1e9: return f"${v/1e9:.2f}B"
        if abs(v) >= 1e6: return f"${v/1e6:.0f}M"
        return f"${v:,.0f}"
    return series.map(fmt)

def _yoy(df: pd.DataFrame, row: str) -> list:
    if row not in df.index: return ["—"] * len(df.columns)
    vals = df.loc[row]
    result = ["—"]
    for i in range(1, len(vals)):
        prev = vals.iloc[i]
        curr = vals.iloc[i-1]
        if prev and prev != 0 and not np.isnan(float(prev)):
            pct = (curr - prev) / abs(prev) * 100
            color = "green" if pct >= 0 else "red"
            result.append(f"<span style='color:{color};'>{pct:+.1f}%</span>")
        else:
            result.append("—")
    return result

def _render_df(df: pd.DataFrame, row_map: dict):
    if df is None or df.empty:
        st.warning("No data available.")
        return
    cols = df.columns[:4]
    rows_data = {}
    for label, key in row_map.items():
        if key in df.index:
            rows_data[label] = _fmt_row(df.loc[key, cols])
        else:
            rows_data[label] = ["—"] * len(cols)
    display = pd.DataFrame(rows_data, index=[str(c)[:10] for c in cols]).T
    display.columns = [str(c)[:10] for c in display.columns]
    st.dataframe(display, use_container_width=True)

tab_is, tab_bs, tab_cf, tab_charts = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow", "Trend Charts"])

# ── Income Statement ──────────────────────────────────────────────────────────
with tab_is:
    income_rows = {
        "Revenue":          "Total Revenue",
        "Cost of Revenue":  "Cost Of Revenue",
        "Gross Profit":     "Gross Profit",
        "R&D Expenses":     "Research Development",
        "SG&A Expenses":    "Selling General Administrative",
        "Operating Income": "Operating Income",
        "EBITDA":           "Ebitda",
        "Net Income":       "Net Income",
        "EPS (Diluted)":    "Diluted EPS",
    }
    _render_df(income, income_rows)
    if income is not None and not income.empty:
        cols4 = income.columns[:4]
        st.subheader("Key Margin Ratios")
        mc1, mc2, mc3 = st.columns(3)
        for col_idx, col_date in enumerate(cols4[:3]):
            try:
                rev = income.loc["Total Revenue", col_date]
                gp  = income.loc["Gross Profit",   col_date] if "Gross Profit" in income.index else 0
                oi  = income.loc["Operating Income",col_date] if "Operating Income" in income.index else 0
                ni  = income.loc["Net Income",       col_date] if "Net Income" in income.index else 0
                gm  = gp/rev*100 if rev else 0
                om  = oi/rev*100 if rev else 0
                nm  = ni/rev*100 if rev else 0
                [mc1, mc2, mc3][col_idx].metric(
                    str(col_date)[:7],
                    f"NM: {nm:.1f}%",
                    f"GM: {gm:.1f}% | OM: {om:.1f}%",
                )
            except Exception:
                pass

# ── Balance Sheet ─────────────────────────────────────────────────────────────
with tab_bs:
    bs_rows = {
        "Cash & Equivalents":    "Cash And Cash Equivalents",
        "Short-term Investments":"Short Term Investments",
        "Total Current Assets":  "Total Current Assets",
        "PP&E Net":              "Net PPE",
        "Total Assets":          "Total Assets",
        "Total Current Liab.":   "Total Current Liabilities",
        "Long-Term Debt":        "Long Term Debt",
        "Total Liabilities":     "Total Liabilities Net Minority Interest",
        "Total Equity":          "Stockholders Equity",
        "Retained Earnings":     "Retained Earnings",
    }
    _render_df(balance, bs_rows)
    if balance is not None and not balance.empty:
        st.subheader("Key Ratios")
        bc1, bc2, bc3 = st.columns(3)
        for ci, cd in enumerate(balance.columns[:3]):
            try:
                ca  = balance.loc["Total Current Assets",       cd] if "Total Current Assets" in balance.index else 1
                cl  = balance.loc["Total Current Liabilities",  cd] if "Total Current Liabilities" in balance.index else 1
                te  = balance.loc["Stockholders Equity",        cd] if "Stockholders Equity" in balance.index else 1
                ltd = balance.loc["Long Term Debt",             cd] if "Long Term Debt" in balance.index else 0
                cr  = ca/cl if cl else 0
                de  = ltd/te if te else 0
                [bc1,bc2,bc3][ci].metric(str(cd)[:7], f"CR: {cr:.2f}x", f"D/E: {de:.2f}x")
            except Exception:
                pass

# ── Cash Flow ─────────────────────────────────────────────────────────────────
with tab_cf:
    cf_rows = {
        "Operating Cash Flow":     "Operating Cash Flow",
        "Capital Expenditures":    "Capital Expenditure",
        "Free Cash Flow":          "Free Cash Flow",
        "Investing Cash Flow":     "Investing Cash Flow",
        "Financing Cash Flow":     "Financing Cash Flow",
        "Dividends Paid":          "Cash Dividends Paid",
        "Stock Buybacks":          "Repurchase Of Capital Stock",
    }
    _render_df(cashflow, cf_rows)

# ── Trend Charts ──────────────────────────────────────────────────────────────
with tab_charts:
    if income is not None and not income.empty:
        cols4 = income.columns[:4]
        years = [str(c)[:4] for c in cols4]

        def _get_vals(df, key):
            if key not in df.index: return {}
            return {str(c)[:4]: float(df.loc[key, c])/1e9 for c in cols4
                    if not pd.isna(df.loc[key, c])}

        ch1, ch2 = st.columns(2)
        with ch1:
            rev_d = _get_vals(income, "Total Revenue")
            gp_d  = _get_vals(income, "Gross Profit")
            if rev_d:
                import plotly.graph_objects as go
                from utils.plots import _DARK
                fig = go.Figure()
                fig.add_trace(go.Bar(x=list(rev_d.keys()), y=list(rev_d.values()), name="Revenue", marker_color="#1f77b4"))
                fig.add_trace(go.Bar(x=list(gp_d.keys()),  y=list(gp_d.values()),  name="Gross Profit", marker_color="#2ca02c"))
                fig.update_layout(**_DARK, title="Revenue & Gross Profit ($B)", barmode="group", height=320)
                st.plotly_chart(fig, use_container_width=True)
        with ch2:
            oi_d  = _get_vals(income, "Operating Income")
            ni_d  = _get_vals(income, "Net Income")
            if ni_d:
                import plotly.graph_objects as go
                from utils.plots import _DARK
                fig = go.Figure()
                fig.add_trace(go.Bar(x=list(oi_d.keys()), y=list(oi_d.values()), name="Op. Income", marker_color="#FFA500"))
                fig.add_trace(go.Bar(x=list(ni_d.keys()), y=list(ni_d.values()), name="Net Income",  marker_color="#17becf"))
                fig.update_layout(**_DARK, title="Operating & Net Income ($B)", barmode="group", height=320)
                st.plotly_chart(fig, use_container_width=True)

        if cashflow is not None and not cashflow.empty:
            ch3, ch4 = st.columns(2)
            with ch3:
                ocf = _get_vals(cashflow, "Operating Cash Flow") if cashflow is not None else {}
                fcf = _get_vals(cashflow, "Free Cash Flow")      if cashflow is not None else {}
                if ocf:
                    import plotly.graph_objects as go
                    from utils.plots import _DARK
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=list(ocf.keys()), y=list(ocf.values()), name="Op CF",  marker_color="#1f77b4"))
                    fig.add_trace(go.Bar(x=list(fcf.keys()), y=list(fcf.values()), name="Free CF", marker_color="#2ca02c"))
                    fig.update_layout(**_DARK, title="Cash Flow ($B)", barmode="group", height=320)
                    st.plotly_chart(fig, use_container_width=True)
            with ch4:
                rd  = _get_vals(income,   "Research Development")   if income is not None else {}
                cap = _get_vals(cashflow,  "Capital Expenditure")    if cashflow is not None else {}
                if rd or cap:
                    import plotly.graph_objects as go
                    from utils.plots import _DARK
                    fig = go.Figure()
                    if rd:  fig.add_trace(go.Bar(x=list(rd.keys()),  y=list(rd.values()),  name="R&D",  marker_color="#9467bd"))
                    if cap: fig.add_trace(go.Bar(x=list(cap.keys()), y=[abs(v) for v in cap.values()], name="CapEx", marker_color="#d62728"))
                    fig.update_layout(**_DARK, title="R&D & CapEx ($B)", barmode="group", height=320)
                    st.plotly_chart(fig, use_container_width=True)

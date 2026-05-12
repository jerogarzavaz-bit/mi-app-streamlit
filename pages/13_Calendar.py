import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.data import get_earnings_calendar
from utils.config import TICKERS_US, TICKERS_MX

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📅 Market Calendar</div>
  <div class='page-subtitle'>Earnings schedules, Fed meetings, and key economic releases</div>
</div>""", unsafe_allow_html=True)

tab_earn, tab_eco = st.tabs(["Earnings Calendar", "Economic Calendar"])

# ── Earnings Calendar ─────────────────────────────────────────────────────────
with tab_earn:
    source = st.radio("Ticker source:", [
        "Default Watchlist (US)", "Default Watchlist (México)", "Custom",
    ], horizontal=True)

    if source == "Default Watchlist (US)":
        tickers = TICKERS_US
    elif source == "Default Watchlist (México)":
        tickers = TICKERS_MX
    else:
        raw = st.text_input("Enter tickers:", ", ".join(TICKERS_US[:8]))
        tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

    wls = st.session_state.get("watchlists", {})
    if wls:
        sel_wl = st.selectbox("Or load saved watchlist:", ["— none —"] + list(wls.keys()))
        if sel_wl != "— none —":
            tickers = wls[sel_wl]

    if st.button(f"📆 Load Calendar ({len(tickers)} tickers)", type="primary"):
        with st.spinner("Fetching earnings dates…"):
            events = get_earnings_calendar(tuple(tickers))

        today = date.today()
        upcoming = [e for e in events if e["earnings_date"].date() >= today]
        this_week = [e for e in upcoming
                     if e["earnings_date"].date() <= today + timedelta(days=7)]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tickers", len(tickers))
        c2.metric("Upcoming (≤30 days)", len([e for e in upcoming if e["earnings_date"].date() <= today + timedelta(days=30)]))
        c3.metric("This Week", len(this_week))
        c4.metric("Avg Beat Rate", "N/A")

        if upcoming:
            st.subheader("Earnings Schedule")
            df = pd.DataFrame([{
                "Ticker":     e["ticker"],
                "Company":    e["name"],
                "Date":       e["earnings_date"].strftime("%b %d, %Y"),
                "Days Away":  (e["earnings_date"].date() - today).days,
                "EPS Est.":   f"${e['eps_estimate']:.2f}" if e["eps_estimate"] else "N/A",
            } for e in sorted(upcoming, key=lambda x: x["earnings_date"])])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No upcoming earnings dates found. Data may not be available for all tickers.")
    else:
        st.info("Click **Load Calendar** to fetch upcoming earnings dates.")

# ── Economic Calendar ─────────────────────────────────────────────────────────
with tab_eco:
    today = date.today()

    # FOMC countdown
    fomc_dates = [
        date(2026, 6, 10), date(2026, 7, 28), date(2026, 9, 15),
        date(2026, 11, 3), date(2026, 12, 15),
    ]
    next_fomc = next((d for d in fomc_dates if d >= today), None)
    if next_fomc:
        days_to_fomc = (next_fomc - today).days
        st.markdown(f"""
        <div class='card' style='border-color:#d62728;'>
          <div style='font-size:1.1rem;font-weight:700;color:#d62728;'>
            NEXT FOMC IN {days_to_fomc} DAYS — {next_fomc.strftime("%b %d, %Y")}
          </div>
          <div style='color:#888;margin-top:6px;font-size:13px;'>
            Watch for: rate decision, forward guidance, press conference tone.
            Key phrases: "data dependent", "higher for longer".
          </div>
        </div>""", unsafe_allow_html=True)

    # Economic events
    eco_events = [
        {"name":"CPI Report",        "date": date(2026, 5, 13), "impact":"Very High", "desc":"Consumer Price Index — headline and core YoY % change", "watch":"Core CPI, shelter/OER component, services inflation"},
        {"name":"Retail Sales",       "date": date(2026, 5, 15), "impact":"Medium",    "desc":"Monthly retail sales — key read on consumer spending",  "watch":"Control group ex-autos/gas"},
        {"name":"PCE Inflation",      "date": date(2026, 5, 29), "impact":"High",      "desc":"Fed's preferred inflation gauge",                         "watch":"Core PCE MoM and YoY"},
        {"name":"Jobs Report (NFP)",  "date": date(2026, 6,  5), "impact":"Very High", "desc":"Non-farm payrolls, unemployment rate, wages",             "watch":"Wages growth, labor force participation"},
        {"name":"FOMC Decision",      "date": date(2026, 6, 10), "impact":"Very High", "desc":"Fed rate decision + press conference",                    "watch":"Dot plot, forward guidance language"},
        {"name":"GDP Advance",        "date": date(2026, 7, 30), "impact":"High",      "desc":"First GDP estimate for Q2 2026",                         "watch":"Consumer spending component"},
    ]

    impact_color = {"Very High":"#d62728","High":"#FFA500","Medium":"#4da6ff","Low":"#888"}
    st.subheader("Upcoming Economic Events")

    for e in eco_events:
        days_away = (e["date"] - today).days
        if days_away < 0:
            continue
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div class='card' style='margin-bottom:8px;'>
              <div style='display:flex;justify-content:space-between;align-items:center;'>
                <strong style='font-size:15px;'>{e['name']}</strong>
                <span style='color:#888;font-size:12px;'>{e['date'].strftime("%b %d, %Y")} (in {days_away} days)</span>
              </div>
              <div style='color:#aaa;font-size:13px;margin:4px 0;'>{e['desc']}</div>
              <div style='color:#888;font-size:12px;'>Watch for: {e['watch']}</div>
              <div style='margin-top:8px;'>
                <span style='background:{impact_color.get(e["impact"],"#888")};color:white;
                  padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;'>{e['impact']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

    # Timeline chart
    st.divider()
    st.subheader("6-Month Event Timeline")
    import plotly.graph_objects as go
    from utils.plots import _DARK
    y_map = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}
    color_map = {"Low":"#888","Medium":"#4da6ff","High":"#FFA500","Very High":"#d62728"}
    fig = go.Figure()
    for e in eco_events:
        d = e["date"]
        if (d - today).days < 0 or (d - today).days > 180:
            continue
        fig.add_trace(go.Scatter(
            x=[d], y=[y_map[e["impact"]]],
            mode="markers+text", text=[e["name"]],
            textposition="top center", textfont=dict(size=10),
            marker=dict(size=14, color=color_map[e["impact"]]),
            name=e["name"], showlegend=False,
        ))
    fig.update_layout(**_DARK, title="Upcoming Events",
        yaxis=dict(tickvals=[1,2,3,4], ticktext=["Low","Medium","High","Very High"]),
        height=320)
    st.plotly_chart(fig, use_container_width=True)

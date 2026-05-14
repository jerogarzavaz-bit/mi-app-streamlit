import streamlit as st
import pandas as pd
import io
from datetime import date, datetime
from utils.data import get_stock_data, get_current_price, get_portfolio_history
from utils.plots import portfolio_pie, portfolio_history_chart
from utils.db import save_user_data, is_configured

@st.cache_data(ttl=300)
def _cached_price_row(ticker: str):
    """Fetch price + info for one ticker, cached 5 min."""
    price = get_current_price(ticker)
    try:
        info, _ = get_stock_data(ticker, "5d")
    except Exception:
        info = {}
    return price, info or {}

username = st.session_state.get("username", "")

def _autosave():
    if is_configured():
        save_user_data(username)

st.markdown("""
<div class='page-header'>
  <div class='page-title'>💼 My Portfolio</div>
  <div class='page-subtitle'>Holdings · Watchlists · Alerts · Performance · Investor Profile</div>
</div>""", unsafe_allow_html=True)

tab_ov, tab_perf, tab_opt, tab_div, tab_hold, tab_wl, tab_alerts, tab_profile = st.tabs([
    "📊 Overview", "📈 Performance", "⚖️ Optimizer", "💰 Dividends",
    "✏️ Holdings", "👁️ Watchlist", "🔔 Alerts", "👤 Profile"
])


# ── helpers ───────────────────────────────────────────────────────────────────
def _fetch_price(ticker, purchase_price):
    price = get_current_price(ticker)
    if price and price > 0:
        return price, True
    return purchase_price, False

def _refresh_prices(holdings):
    updated = []
    for h in holdings:
        price, is_live = _fetch_price(h["ticker"], h.get("purchase_price", 0))
        qty       = h.get("quantity", 0)
        buy_price = h.get("purchase_price", 0)
        cost      = buy_price * qty
        value     = price * qty
        gain      = value - cost
        gain_pct  = (gain / cost * 100) if cost else 0
        updated.append({**h, "current_price": price, "is_live": is_live,
                        "current_value": round(value, 2), "cost_basis": round(cost, 2),
                        "gain": round(gain, 2), "gain_pct": round(gain_pct, 2)})
    return updated


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_ov:
    portfolio = st.session_state.get("portfolio", [])
    if not portfolio:
        st.markdown("""
        <div class='card' style='text-align:center;color:#4a6a8a;padding:40px;'>
          <div style='font-size:36px;margin-bottom:12px;'>💼</div>
          <div style='font-size:15px;font-weight:600;color:#6a8aaa;margin-bottom:8px;'>No holdings yet</div>
          <div style='font-size:13px;'>Go to <strong style='color:#7eb8e8;'>Holdings</strong> tab to add your first position or import from Yahoo Finance.</div>
        </div>""", unsafe_allow_html=True)
    else:
        with st.spinner("Fetching live prices…"):
            holdings = _refresh_prices(portfolio)

        stale = [h["ticker"] for h in holdings if not h.get("is_live")]
        if stale:
            st.warning(f"Could not fetch live price for: {', '.join(stale)} — showing purchase price.")

        total_val  = sum(h["current_value"] for h in holdings)
        total_cost = sum(h["cost_basis"]    for h in holdings)
        total_gain = total_val - total_cost
        total_pct  = (total_gain / total_cost * 100) if total_cost else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Value",     f"${total_val:,.2f}")
        c2.metric("Total Cost",      f"${total_cost:,.2f}")
        c3.metric("Total Gain/Loss", f"${total_gain:+,.2f}", f"{total_pct:+.2f}%")
        c4.metric("Positions",       len(holdings))

        col_chart, col_table = st.columns([1, 2])
        with col_chart:
            pie_data = [h for h in holdings if h.get("current_value", 0) > 0]
            if pie_data:
                st.plotly_chart(portfolio_pie(pie_data), use_container_width=True)
        with col_table:
            rows = []
            for h in holdings:
                live_tag = "🟢" if h.get("is_live") else "🔴"
                rows.append({
                    "Ticker": h["ticker"], "Qty": h.get("quantity", 0),
                    "Buy $": h.get("purchase_price", 0), "Live $": h["current_price"],
                    "": live_tag, "Value": h["current_value"],
                    "Gain $": h["gain"], "Gain %": h["gain_pct"],
                    "Weight %": round(h["current_value"] / total_val * 100, 1) if total_val else 0,
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                column_config={
                    "Buy $":    st.column_config.NumberColumn(format="$%.2f"),
                    "Live $":   st.column_config.NumberColumn(format="$%.2f"),
                    "Value":    st.column_config.NumberColumn(format="$%.2f"),
                    "Gain $":   st.column_config.NumberColumn(format="$%+.2f"),
                    "Gain %":   st.column_config.NumberColumn(format="%.2f%%"),
                    "Weight %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
                })
            st.caption("🟢 Live price  ·  🔴 Could not fetch — showing purchase price")

        # Rebalance + Risk in expandable sections
        st.divider()
        with st.expander("🤖 AI Rebalancing Advice"):
            from utils.ai import has_key, no_key_banner, chat
            if not has_key():
                no_key_banner("AI rebalancing advice")
            else:
                if st.button("Generate Rebalancing Advice", type="primary", key="rb_btn_ov"):
                    total = sum(h["current_value"] for h in holdings)
                    ctx = "PORTFOLIO:\n" + "\n".join(
                        f"{h['ticker']}: {h.get('quantity',0)} shares @ ${h['current_price']:.2f} = ${h['current_value']:,.0f} ({h['current_value']/total*100:.1f}%)"
                        for h in holdings)
                    profile = st.session_state.get("profile", {})
                    prompt = f"{ctx}\n\nProfile: Risk={profile.get('riesgo','moderate')}, Style={profile.get('estilo','mixed')}, Objective={profile.get('objetivo','growth')}\n\nProvide specific rebalancing recommendations."
                    with st.spinner("Generating…"):
                        resp = chat([{"role": "user", "content": prompt}])
                    if resp:
                        st.markdown(resp)

        with st.expander("⚡ Risk Analytics"):
            total = sum(h["current_value"] for h in holdings) or 1
            sectors = {}
            for h in holdings:
                _, info = _cached_price_row(h["ticker"])
                sec = info.get("sector", "Unknown") or "Unknown"
                sectors[sec] = sectors.get(sec, 0) + h.get("current_value", 0)
            st.write("**Sector Exposure**")
            for sec, val in sorted(sectors.items(), key=lambda x: -x[1]):
                pct = val / total * 100
                st.progress(pct / 100, text=f"{sec}: {pct:.1f}%")
            top_pct = max(h.get("current_value", 0) for h in holdings) / total * 100
            st.metric("Top Concentration", f"{top_pct:.1f}%",
                      delta="High risk" if top_pct > 30 else "OK",
                      delta_color="inverse" if top_pct > 30 else "normal")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab_perf:
    portfolio = st.session_state.get("portfolio", [])
    if not portfolio:
        st.info("Add holdings first.")
    else:
        import json
        st.markdown("<div style='color:#8aadcc;font-size:13px;margin-bottom:16px;'>Historical portfolio value reconstructed from daily closing prices since your earliest purchase date.</div>", unsafe_allow_html=True)
        with st.spinner("Building performance history…"):
            holdings_for_hist = [
                {"ticker": h["ticker"], "quantity": h.get("quantity", 0),
                 "purchase_date": h.get("purchase_date", "")}
                for h in portfolio if h.get("purchase_date")
            ]
            hist_df = get_portfolio_history(json.dumps(holdings_for_hist))

        if hist_df.empty:
            st.warning("Could not build performance history. Check tickers and purchase dates.")
        else:
            start_val = hist_df["value"].iloc[0]
            end_val   = hist_df["value"].iloc[-1]
            gain      = end_val - start_val
            gain_pct  = (gain / start_val * 100) if start_val else 0
            ath       = hist_df["value"].max()

            m1, m2, m3 = st.columns(3)
            m1.metric("Starting Value", f"${start_val:,.2f}")
            m2.metric("Current Value",  f"${end_val:,.2f}", f"{gain_pct:+.2f}%")
            m3.metric("All-Time High",  f"${ath:,.2f}")
            st.plotly_chart(portfolio_history_chart(hist_df), use_container_width=True)

            st.divider()
            with st.expander("⚡ Stress Test & VaR"):
                from utils.stress_test import run_stress_test, compute_var
                import plotly.graph_objects as go
                from utils.config import COLOR_SUCCESS, COLOR_DANGER

                portfolio_w_vals = st.session_state.get("portfolio", [])
                if not any(h.get("current_value") for h in portfolio_w_vals):
                    st.info("Return to Overview tab first to load live prices.")
                else:
                    c_var, c_stress = st.columns(2)
                    with c_var:
                        st.markdown("**Value at Risk (Historical)**")
                        for conf, days in [(0.95, 1), (0.99, 1), (0.95, 10)]:
                            v = compute_var(portfolio_w_vals, conf, days)
                            label = f"{int(conf*100)}% VaR {days}d"
                            st.metric(label, f"${abs(v['var_usd']):,.0f}",
                                      delta=f"{v['var_pct']:.2f}%", delta_color="inverse")

                    with c_stress:
                        st.markdown("**Run Scenario Analysis**")
                        if st.button("▶ Run Stress Test", key="perf_stress_run"):
                            with st.spinner("Simulating scenarios…"):
                                st.session_state["_stress_results"] = run_stress_test(portfolio_w_vals)

                    stress = st.session_state.get("_stress_results")
                    if stress:
                        rows_s = [{"Scenario": k,
                                   "Impact %": v["portfolio_impact_pct"],
                                   "Impact $": v["portfolio_impact_usd"]}
                                  for k, v in stress.items()]
                        df_s = pd.DataFrame(rows_s).sort_values("Impact %")
                        colors = [COLOR_SUCCESS if r >= 0 else COLOR_DANGER for r in df_s["Impact %"]]
                        fig_s = go.Figure(go.Bar(
                            x=df_s["Impact %"], y=df_s["Scenario"], orientation="h",
                            marker_color=colors,
                            text=[f"${v:+,.0f}" for v in df_s["Impact $"]],
                            textposition="outside"))
                        fig_s.update_layout(
                            template="plotly_dark", paper_bgcolor="#09090B", plot_bgcolor="#09090B",
                            title="Portfolio Stress Test", xaxis_title="Impact (%)",
                            height=380, margin=dict(l=180, r=80, t=44, b=36),
                            font=dict(color="#A1A1AA"))
                        st.plotly_chart(fig_s, use_container_width=True)

        st.divider()
        with st.expander("📊 Portfolio Attribution", expanded=False):
            st.caption("Which holdings drove your P&L? Attribution vs equal-weight benchmark.")
            if portfolio:
                import yfinance as yf
                attr_period = st.selectbox("Period", ["1mo","3mo","6mo","1y"], index=1, key="attr_period")

                if st.button("Calculate Attribution", key="attr_run"):
                    attr_rows = []
                    total_value = sum(h.get("shares",0) * h.get("avg_cost",0) for h in portfolio if h.get("shares") and h.get("avg_cost"))

                    for h in portfolio:
                        t = h.get("ticker","")
                        shares = h.get("shares", 0)
                        cost = h.get("avg_cost", 0)
                        if not t or not shares or not cost:
                            continue
                        try:
                            hist = yf.Ticker(t).history(period=attr_period)
                            if hist.empty:
                                continue
                            start_p = float(hist["Close"].iloc[0])
                            end_p   = float(hist["Close"].iloc[-1])
                            ret_pct = (end_p - start_p) / start_p * 100
                            pos_value = shares * cost
                            weight = pos_value / total_value if total_value else 0
                            contribution = weight * ret_pct
                            attr_rows.append({
                                "Ticker": t,
                                "Weight %": round(weight * 100, 1),
                                "Return %": round(ret_pct, 2),
                                "Contribution %": round(contribution, 2),
                            })
                        except:
                            continue

                    if attr_rows:
                        import pandas as pd
                        import plotly.graph_objects as go
                        from utils.config import COLOR_SUCCESS, COLOR_DANGER

                        df_attr = pd.DataFrame(attr_rows).sort_values("Contribution %", ascending=False)
                        total_contrib = df_attr["Contribution %"].sum()
                        st.metric("Total Portfolio Return (Weighted)", f"{total_contrib:+.2f}%")

                        colors = [COLOR_SUCCESS if v >= 0 else COLOR_DANGER for v in df_attr["Contribution %"]]
                        fig_attr = go.Figure(go.Bar(
                            x=df_attr["Ticker"], y=df_attr["Contribution %"],
                            marker_color=colors, text=[f"{v:+.2f}%" for v in df_attr["Contribution %"]],
                            textposition="outside"))
                        fig_attr.update_layout(
                            template="plotly_dark", paper_bgcolor="#09090B", plot_bgcolor="#09090B",
                            title="Contribution to Portfolio Return (%)", height=350,
                            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                            yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                            font=dict(color="#A1A1AA"), margin=dict(l=48, r=24, t=44, b=36))
                        st.plotly_chart(fig_attr, use_container_width=True)
                        st.dataframe(df_attr, use_container_width=True, hide_index=True)
            else:
                st.info("Add holdings to calculate attribution.")

        with st.expander("📈 Relative Strength vs SPY", expanded=False):
            st.caption("How has your portfolio performed relative to the S&P 500?")
            if portfolio:
                import yfinance as yf
                import pandas as pd
                import plotly.graph_objects as go
                from utils.config import COLOR_PRIMARY, COLOR_SUCCESS

                rs_period = st.selectbox("Period", ["3mo","6mo","1y","2y"], index=2, key="rs_period")
                if st.button("Calculate RS", key="rs_run"):
                    try:
                        spy_hist = yf.Ticker("SPY").history(period=rs_period)["Close"]
                        spy_norm = spy_hist / spy_hist.iloc[0] * 100

                        # Build portfolio indexed returns (equal-weight)
                        port_series = {}
                        for h in portfolio:
                            t = h.get("ticker","")
                            if not t: continue
                            try:
                                hist = yf.Ticker(t).history(period=rs_period)["Close"]
                                if len(hist) > 5:
                                    port_series[t] = hist / hist.iloc[0] * 100
                            except:
                                continue

                        if port_series:
                            df_all = pd.DataFrame(port_series).dropna()
                            port_avg = df_all.mean(axis=1)
                            spy_aligned = spy_norm.reindex(port_avg.index, method="ffill")
                            rs_line = port_avg / spy_aligned * 100

                            fig_rs = go.Figure()
                            fig_rs.add_scatter(x=port_avg.index, y=port_avg, name="My Portfolio",
                                              line=dict(color=COLOR_PRIMARY, width=2))
                            fig_rs.add_scatter(x=spy_aligned.index, y=spy_aligned, name="SPY",
                                              line=dict(color="#888", width=2, dash="dash"))
                            fig_rs.update_layout(
                                template="plotly_dark", paper_bgcolor="#09090B", plot_bgcolor="#09090B",
                                title="Portfolio vs SPY — Indexed (100 = start)", height=380,
                                xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                                yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                                font=dict(color="#A1A1AA"), margin=dict(l=48, r=24, t=44, b=36),
                                hovermode="x unified", legend=dict(orientation="h", y=1.02))
                            st.plotly_chart(fig_rs, use_container_width=True)

                            final_port = port_avg.iloc[-1] - 100
                            final_spy  = spy_aligned.iloc[-1] - 100
                            alpha = final_port - final_spy
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Portfolio Return", f"{final_port:+.1f}%")
                            c2.metric("SPY Return", f"{final_spy:+.1f}%")
                            c3.metric("Alpha", f"{alpha:+.1f}%", delta="outperform" if alpha >= 0 else "underperform",
                                     delta_color="normal" if alpha >= 0 else "inverse")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.info("Add holdings to calculate relative strength.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — OPTIMIZER
# ══════════════════════════════════════════════════════════════════════════════
with tab_opt:
    from utils.portfolio_optimizer import optimize_portfolio
    import plotly.graph_objects as go

    portfolio = st.session_state.get("portfolio", [])
    tickers = list({h["ticker"] for h in portfolio})

    st.markdown("<div style='color:#8aadcc;font-size:13px;margin-bottom:16px;'>Modern Portfolio Theory — find the allocation that maximizes risk-adjusted returns for your current holdings.</div>", unsafe_allow_html=True)

    if len(tickers) < 2:
        st.info("Add at least 2 holdings to run portfolio optimization.")
    else:
        period_opt = st.select_slider("Historical period", ["1y", "2y", "3y", "5y"], value="2y", key="opt_period")
        rf_rate = st.number_input("Risk-free rate (%)", value=4.5, step=0.1, key="opt_rf") / 100

        if st.button("🔢 Run Optimization", type="primary", key="opt_run"):
            with st.spinner("Running Modern Portfolio Theory optimization…"):
                result = optimize_portfolio(tickers, period_opt, rf_rate)

            if not result:
                st.error("Could not fetch enough historical data. Try a shorter period.")
            else:
                st.session_state["_opt_result"] = result

        result = st.session_state.get("_opt_result")
        if result:
            ms = result["max_sharpe"]
            mv = result["min_volatility"]
            eq = result["equal_weight"]
            available_tickers = result["tickers"]

            c1, c2, c3 = st.columns(3)
            for col, port, label, color in [
                (c1, ms, "⭐ Max Sharpe",     "#6172F3"),
                (c2, mv, "🛡️ Min Volatility", "#22C55E"),
                (c3, eq, "⚖️ Equal Weight",   "#F59E0B"),
            ]:
                with col:
                    st.markdown(f"<div class='card' style='border-top:3px solid {color};padding:16px;'>", unsafe_allow_html=True)
                    st.markdown(f"**{label}**")
                    st.metric("Expected Return", f"{port['return']:+.1f}%")
                    st.metric("Volatility",       f"{port['volatility']:.1f}%")
                    st.metric("Sharpe Ratio",     f"{port['sharpe']:.2f}")
                    wdf = pd.DataFrame({"Ticker": list(port["weights"].keys()),
                                        "Weight %": list(port["weights"].values())})
                    st.dataframe(wdf, hide_index=True, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            # Efficient frontier scatter
            st.divider()
            mc = result.get("monte_carlo", [])
            if mc:
                fig_ef = go.Figure()
                fig_ef.add_trace(go.Scatter(
                    x=[p["v"] for p in mc], y=[p["r"] for p in mc],
                    mode="markers", marker=dict(
                        color=[p["s"] for p in mc],
                        colorscale="Viridis", size=3, opacity=0.5,
                        colorbar=dict(title="Sharpe")),
                    name="Portfolios"))
                for port, label, color, sym in [
                    (ms, "Max Sharpe", "#6172F3", "star"),
                    (mv, "Min Vol",    "#22C55E", "diamond"),
                    (eq, "Equal Wt",  "#F59E0B", "circle"),
                ]:
                    fig_ef.add_trace(go.Scatter(
                        x=[port["volatility"]], y=[port["return"]],
                        mode="markers+text", text=[label],
                        textposition="top center",
                        marker=dict(color=color, size=14, symbol=sym),
                        name=label))
                fig_ef.update_layout(
                    template="plotly_dark", paper_bgcolor="#09090B", plot_bgcolor="#09090B",
                    title="Efficient Frontier — 5,000 Random Portfolios",
                    xaxis_title="Annual Volatility (%)", yaxis_title="Annual Return (%)",
                    height=420, font=dict(color="#A1A1AA"))
                st.plotly_chart(fig_ef, use_container_width=True)

            # Rebalancing table
            st.subheader("📋 Suggested Rebalancing (vs Max Sharpe)")
            total_val = sum(h.get("current_value", 0) for h in portfolio)
            rebal_rows = []
            for t in available_tickers:
                curr_val = next((h.get("current_value", 0) for h in portfolio if h["ticker"] == t), 0)
                curr_pct = curr_val / total_val * 100 if total_val else 0
                opt_pct  = ms["weights"].get(t, 0)
                diff     = opt_pct - curr_pct
                rebal_rows.append({
                    "Ticker": t,
                    "Current %": round(curr_pct, 1),
                    "Optimal %": opt_pct,
                    "Difference": round(diff, 1),
                    "Action": "↑ Increase" if diff > 2 else ("↓ Reduce" if diff < -2 else "✓ Hold"),
                })
            st.dataframe(pd.DataFrame(rebal_rows), hide_index=True, use_container_width=True,
                column_config={"Difference": st.column_config.NumberColumn(format="%+.1f%%")})


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DIVIDENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab_div:
    from utils.dividends import get_portfolio_annual_income, get_dividend_data, get_portfolio_dividend_calendar
    import plotly.graph_objects as go
    from utils.config import COLOR_PRIMARY, COLOR_SUCCESS

    portfolio = st.session_state.get("portfolio", [])
    if not portfolio:
        st.info("Add holdings to see dividend analysis.")
    else:
        with st.spinner("Fetching dividend data…"):
            income = get_portfolio_annual_income(portfolio)

        total_val = sum(h.get("current_value", 0) for h in portfolio) or 1
        port_yield = income["total_annual"] / total_val * 100

        m1, m2, m3 = st.columns(3)
        m1.metric("Annual Income",   f"${income['total_annual']:,.2f}")
        m2.metric("Monthly Average", f"${income['total_annual']/12:,.2f}")
        m3.metric("Portfolio Yield", f"{port_yield:.2f}%")

        # Monthly bar chart
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly_vals = [income["monthly_breakdown"].get(i, 0) for i in range(1, 13)]
        fig_div = go.Figure(go.Bar(
            x=months, y=monthly_vals,
            marker_color=COLOR_PRIMARY,
            text=[f"${v:.0f}" for v in monthly_vals],
            textposition="outside"))
        fig_div.update_layout(
            template="plotly_dark", paper_bgcolor="#09090B", plot_bgcolor="#09090B",
            title="Projected Monthly Dividend Income", yaxis_title="Income ($)",
            height=320, font=dict(color="#A1A1AA"), margin=dict(l=48, r=24, t=44, b=36))
        st.plotly_chart(fig_div, use_container_width=True)

        # Per-ticker table
        rows = []
        for h in portfolio:
            t = h["ticker"]
            d = get_dividend_data(t)
            rows.append({
                "Ticker": t,
                "Annual/Share": f"${d['annual_dividend']:.4f}",
                "Yield %": f"{d['yield_pct']:.2f}%",
                "Frequency": d["frequency"],
                "Payout Ratio": f"{d['payout_ratio']:.0f}%",
                "5Y Growth": f"{d['growth_5yr']:+.1f}%",
                "Next Ex-Date": d["ex_date"] or "—",
                "Annual Income": f"${income['by_ticker'].get(t, 0):,.2f}",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

        # Calendar
        with st.expander("📅 Dividend Calendar — Next 12 Months"):
            tickers_tuple = tuple(h["ticker"] for h in portfolio)
            cal = get_portfolio_dividend_calendar(tickers_tuple)
            if cal:
                cal_rows = []
                for e in cal:
                    qty = next((h.get("quantity", 0) for h in portfolio if h["ticker"] == e["ticker"]), 0)
                    cal_rows.append({
                        "Ticker": e["ticker"],
                        "Ex-Date": e["ex_date"],
                        "Amount/Share": f"${e['amount']:.4f}",
                        "Estimated Income": f"${e['amount']*qty:.2f}",
                        "Frequency": e["frequency"],
                    })
                st.dataframe(pd.DataFrame(cal_rows), hide_index=True, use_container_width=True)
            else:
                st.info("No upcoming ex-dividend dates found for your holdings.")

        st.divider()
        with st.expander("🔄 DRIP Simulator — Dividend Reinvestment", expanded=False):
            st.caption("See how reinvesting dividends compounds your returns over time.")
            drip_ticker = st.text_input("Ticker", value="AAPL", key="drip_ticker").upper().strip()
            drip_shares = st.number_input("Starting shares", value=100, min_value=1, key="drip_shares")
            drip_years  = st.slider("Years to simulate", 1, 30, 10, key="drip_years")

            if st.button("▶ Run DRIP Simulation", key="drip_run"):
                import yfinance as yf
                import pandas as pd
                import plotly.graph_objects as go
                from utils.config import COLOR_PRIMARY, COLOR_SUCCESS

                with st.spinner("Running simulation…"):
                    try:
                        tk = yf.Ticker(drip_ticker)
                        hist = tk.history(period=f"{drip_years}y")
                        if hist.empty:
                            st.error("No data found.")
                        else:
                            # Normalize dividends and simulate DRIP
                            divs = hist["Dividends"][hist["Dividends"] > 0]
                            prices = hist["Close"]

                            shares_drip = float(drip_shares)
                            shares_no_drip = float(drip_shares)
                            drip_values = []
                            nodrip_values = []
                            dates = []

                            for date, price in prices.items():
                                # Pay dividends on ex-dates
                                if date in divs.index:
                                    div_amount = divs[date]
                                    cash_div = shares_drip * div_amount
                                    new_shares = cash_div / price
                                    shares_drip += new_shares
                                drip_values.append(shares_drip * price)
                                nodrip_values.append(shares_no_drip * price)
                                dates.append(date)

                            start_val = nodrip_values[0] if nodrip_values else 0
                            end_drip = drip_values[-1] if drip_values else 0
                            end_nodrip = nodrip_values[-1] if nodrip_values else 0

                            c1, c2, c3 = st.columns(3)
                            c1.metric("Starting Value", f"${start_val:,.0f}")
                            c2.metric("Without DRIP", f"${end_nodrip:,.0f}", f"{(end_nodrip/start_val-1)*100:+.1f}%")
                            c3.metric("With DRIP", f"${end_drip:,.0f}", f"{(end_drip/start_val-1)*100:+.1f}%",
                                     delta_color="normal")

                            fig_drip = go.Figure()
                            fig_drip.add_scatter(x=dates, y=drip_values, name="With DRIP",
                                                line=dict(color=COLOR_SUCCESS, width=2))
                            fig_drip.add_scatter(x=dates, y=nodrip_values, name="Without DRIP",
                                                line=dict(color="#888", width=2, dash="dash"))
                            fig_drip.update_layout(
                                template="plotly_dark", paper_bgcolor="#09090B", plot_bgcolor="#09090B",
                                title=f"{drip_ticker} — DRIP vs No DRIP ({drip_years}Y)",
                                height=380, hovermode="x unified",
                                xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                                yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                                font=dict(color="#A1A1AA"), margin=dict(l=48, r=24, t=44, b=36),
                                legend=dict(orientation="h", y=1.02))
                            st.plotly_chart(fig_drip, use_container_width=True)
                            st.caption(f"Final shares with DRIP: {shares_drip:.2f} vs {drip_shares} without DRIP")
                    except Exception as e:
                        st.error(f"Simulation error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — HOLDINGS (tab_hold)
# ══════════════════════════════════════════════════════════════════════════════
with tab_hold:
    portfolio = st.session_state.get("portfolio", [])

    def _parse_yf_csv(file):
        try:
            content = file.read().decode("utf-8", errors="replace")
            df = pd.read_csv(io.StringIO(content))
            df.columns = [c.strip() for c in df.columns]
            holdings = []
            for _, row in df.iterrows():
                ticker = str(row.get("Symbol", "")).strip().upper()
                if not ticker or ticker == "NAN":
                    continue
                buy_price = None
                for col in ("Purchase Price", "Cost", "Avg Cost", "Buy Price"):
                    v = row.get(col)
                    if v and str(v).strip() not in ("", "N/A", "nan"):
                        try:
                            buy_price = float(str(v).replace("$", "").replace(",", ""))
                            break
                        except ValueError:
                            pass
                qty = None
                for col in ("Quantity", "Shares", "Qty"):
                    v = row.get(col)
                    if v and str(v).strip() not in ("", "N/A", "nan"):
                        try:
                            qty = float(str(v).replace(",", ""))
                            break
                        except ValueError:
                            pass
                purchase_date = None
                for col in ("Trade Date", "Purchase Date", "Date Acquired"):
                    v = row.get(col)
                    if v and str(v).strip() not in ("", "N/A", "nan"):
                        purchase_date = str(v).strip()
                        break
                holdings.append({
                    "ticker": ticker, "quantity": qty if qty else 1.0,
                    "purchase_price": buy_price if buy_price else 0.0,
                    "purchase_date": purchase_date or date.today().isoformat(),
                    "_needs_price": buy_price is None,
                })
            return holdings
        except Exception as e:
            st.error(f"Could not parse CSV: {e}")
            return []

    with st.expander("📥 Import from Yahoo Finance", expanded=False):
        st.markdown("""
        <div style='background:rgba(31,119,180,0.08);border:1px solid rgba(31,119,180,0.2);border-radius:10px;padding:14px 18px;margin-bottom:10px;'>
          <div style='color:#8aadcc;font-size:13px;line-height:1.8;'>
            <strong style='color:#c8d8f0;'>Export from Yahoo Finance:</strong><br>
            1. Go to <strong>finance.yahoo.com → My Portfolio</strong><br>
            2. Click the <strong>Download</strong> button (↓ icon, top right)<br>
            3. Upload the <code>.csv</code> below
          </div>
        </div>""", unsafe_allow_html=True)
        uploaded_csv = st.file_uploader("Upload Yahoo Finance CSV", type=["csv"], key="yf_csv_hub")
        if uploaded_csv:
            parsed = _parse_yf_csv(uploaded_csv)
            if parsed:
                needs_price = [h["ticker"] for h in parsed if h.get("_needs_price")]
                st.markdown(f"**{len(parsed)} holdings found:**")
                preview_rows = [{"Ticker": h["ticker"], "Qty": h["quantity"],
                                 "Buy Price": f"${h['purchase_price']:.2f}" if not h.get("_needs_price") else "⚠️ Missing",
                                 "Date": h["purchase_date"]} for h in parsed]
                st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)
                if needs_price:
                    st.warning(f"Purchase price missing for: {', '.join(needs_price)}. Will import as $0.00.")
                col_imp, col_rep = st.columns(2)
                if col_imp.button("➕ Add to holdings", type="primary", key="yf_add_hub"):
                    existing = {h["ticker"] for h in portfolio}
                    added = 0
                    for h in parsed:
                        clean = {k: v for k, v in h.items() if not k.startswith("_")}
                        if clean["ticker"] not in existing:
                            portfolio.append(clean)
                            added += 1
                    st.session_state.portfolio = portfolio
                    _autosave()
                    st.success(f"Imported {added} new holdings.")
                    st.rerun()
                if col_rep.button("🔄 Replace all", key="yf_rep_hub"):
                    st.session_state.portfolio = [{k: v for k, v in h.items() if not k.startswith("_")} for h in parsed]
                    _autosave()
                    st.success(f"Replaced with {len(parsed)} holdings.")
                    st.rerun()

    st.subheader("Add Position")
    with st.form("add_holding_hub", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        new_ticker = c1.text_input("Ticker", placeholder="AAPL")
        new_qty    = c2.number_input("Quantity", min_value=0.001, value=1.0, step=1.0)
        new_price  = c3.number_input("Purchase Price ($)", min_value=0.01, value=100.0, step=0.01)
        new_date   = c4.date_input("Purchase Date", value=date.today())
        if st.form_submit_button("➕ Add Position", type="primary"):
            if new_ticker:
                portfolio.append({"ticker": new_ticker.strip().upper(), "quantity": float(new_qty),
                                  "purchase_price": float(new_price), "purchase_date": str(new_date)})
                st.session_state.portfolio = portfolio
                _autosave()
                st.success(f"Added {new_ticker.upper()} — {new_qty} shares @ ${new_price:.2f}")
                st.rerun()

    if portfolio:
        tickers_seen = {}
        for i, h in enumerate(portfolio):
            tickers_seen.setdefault(h.get("ticker", ""), []).append(i)
        dupes = {t: idxs for t, idxs in tickers_seen.items() if len(idxs) > 1}
        if dupes:
            st.warning(f"Duplicate tickers: **{', '.join(dupes.keys())}**")
            if st.button("🧹 Remove duplicates"):
                seen = set()
                deduped = []
                for h in portfolio:
                    t = h.get("ticker", "")
                    if t not in seen:
                        seen.add(t)
                        deduped.append(h)
                st.session_state.portfolio = deduped
                _autosave()
                st.rerun()

        st.subheader("Current Holdings")
        editing = st.session_state.get("_editing_holding_hub")
        for i, h in enumerate(portfolio):
            ticker = h.get("ticker", "")
            qty    = h.get("quantity", 0)
            price  = h.get("purchase_price", 0.0)
            pdate  = h.get("purchase_date", "")
            if editing == i:
                with st.form(key=f"edit_form_hub_{i}"):
                    st.markdown(f"**Editing {ticker}**")
                    ec1, ec2, ec3, ec4 = st.columns(4)
                    e_qty   = ec1.number_input("Qty",      min_value=0.001, value=float(qty),   step=1.0,  key=f"hq_{i}")
                    e_price = ec2.number_input("Price ($)", min_value=0.0,  value=float(price), step=0.01, key=f"hp_{i}")
                    e_date  = ec3.text_input("Date",       value=str(pdate), key=f"hd_{i}")
                    save_c, cancel_c = st.columns(2)
                    if save_c.form_submit_button("💾 Save", type="primary", use_container_width=True):
                        portfolio[i]["quantity"]       = float(e_qty)
                        portfolio[i]["purchase_price"] = float(e_price)
                        portfolio[i]["purchase_date"]  = e_date.strip()
                        st.session_state.portfolio = portfolio
                        st.session_state._editing_holding_hub = None
                        _autosave()
                        st.rerun()
                    if cancel_c.form_submit_button("✕ Cancel", use_container_width=True):
                        st.session_state._editing_holding_hub = None
                        st.rerun()
            else:
                c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1])
                c1.write(f"**{ticker}**")
                c2.write(f"{qty} shares")
                c3.write(f"${price:.2f}")
                c4.write(pdate)
                if c5.button("✏️", key=f"hub_edit_{i}"):
                    st.session_state._editing_holding_hub = i
                    st.rerun()
                if c6.button("🗑️", key=f"hub_del_{i}"):
                    portfolio.pop(i)
                    st.session_state.portfolio = portfolio
                    _autosave()
                    st.rerun()
    else:
        st.info("No holdings yet. Add your first position above or import from Yahoo Finance.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — WATCHLIST
# ══════════════════════════════════════════════════════════════════════════════
with tab_wl:
    watchlists = st.session_state.get("watchlists", {})

    col1, col2 = st.columns([3, 1])
    wl_name_new = col1.text_input("New watchlist name", placeholder="Tech Picks, Dividend Plays…",
                                   label_visibility="collapsed", key="wl_hub_name")
    if col2.button("➕ Create", key="wl_hub_create") and wl_name_new:
        wl_name_new = wl_name_new.strip()
        if wl_name_new.lower() not in {k.lower() for k in watchlists}:
            watchlists[wl_name_new] = []
            st.session_state.watchlists = watchlists
            _autosave()
            st.success(f"Created: {wl_name_new}")
            st.rerun()
        else:
            st.warning("A watchlist with that name already exists.")

    with st.expander("📥 Import from Yahoo Finance CSV"):
        wl_csv = st.file_uploader("Upload CSV", type=["csv"], key="wl_hub_csv")
        import_name = st.text_input("Save as:", placeholder="My YF Watchlist", key="wl_hub_import_name")
        if wl_csv and import_name:
            try:
                content = wl_csv.read().decode("utf-8", errors="replace")
                df_wl = pd.read_csv(io.StringIO(content))
                df_wl.columns = [c.strip() for c in df_wl.columns]
                col_name = next((c for c in df_wl.columns if c.lower() in ("symbol", "ticker")), df_wl.columns[0])
                raw_tickers = [str(v).strip().upper() for v in df_wl[col_name]
                               if str(v).strip() and str(v).strip().upper() != "NAN"]
                st.write(f"Found **{len(raw_tickers)}** tickers: {', '.join(raw_tickers[:10])}{'…' if len(raw_tickers)>10 else ''}")
                if st.button("✅ Import", type="primary", key="wl_hub_import_btn"):
                    watchlists[import_name] = list(dict.fromkeys(raw_tickers))
                    st.session_state.watchlists = watchlists
                    _autosave()
                    st.success(f"Imported {len(raw_tickers)} tickers.")
                    st.rerun()
            except Exception as e:
                st.error(f"Could not parse CSV: {e}")

    if not watchlists:
        st.info("Create your first watchlist above.")
    else:
        selected = st.selectbox("Select watchlist:", list(watchlists.keys()), key="wl_hub_sel")
        tickers = watchlists.get(selected, [])

        c1, c2, c3 = st.columns([3, 1, 1])
        add_raw = c1.text_input("Add tickers:", placeholder="AAPL, MSFT, NVDA",
                                 label_visibility="collapsed", key="wl_hub_add_raw")
        if c2.button("➕ Add", use_container_width=True, key="wl_hub_add_btn"):
            new_tickers = [t.strip().upper() for t in add_raw.split(",") if t.strip()]
            tickers = list(dict.fromkeys(tickers + new_tickers))
            watchlists[selected] = tickers
            st.session_state.watchlists = watchlists
            _autosave()
            st.rerun()
        if c3.button("🗑️ Delete", use_container_width=True, key="wl_hub_del_list"):
            del watchlists[selected]
            st.session_state.watchlists = watchlists
            _autosave()
            st.rerun()

        if tickers:
            with st.spinner(f"Loading live prices for {len(tickers)} tickers…"):
                rows = []
                for t in tickers:
                    price, info = _cached_price_row(t)
                    curr = price or info.get("currentPrice") or info.get("regularMarketPrice") or 0
                    prev = info.get("previousClose", curr) or curr
                    chg  = ((curr - prev) / prev * 100) if prev else 0
                    rows.append({
                        "_ticker": t, "Ticker": t, "Name": info.get("shortName", t),
                        "Price": round(curr, 2), "Chg %": round(chg, 2),
                        "52W High": info.get("fiftyTwoWeekHigh") or 0,
                        "52W Low":  info.get("fiftyTwoWeekLow") or 0,
                        "Mkt Cap":  (info.get("marketCap") or 0) / 1e9,
                        "Sector":   info.get("sector", ""),
                    })

            if rows:
                positive = sum(1 for r in rows if r["Chg %"] >= 0)
                st.markdown(f"""
                <div style='display:flex;gap:16px;margin-bottom:16px;'>
                  <span style='color:#22c55e;font-size:12px;font-weight:600;'>▲ {positive} up</span>
                  <span style='color:#ef4444;font-size:12px;font-weight:600;'>▼ {len(rows)-positive} down</span>
                </div>""", unsafe_allow_html=True)

                COLS = 3
                for i in range(0, len(rows), COLS):
                    chunk = rows[i:i+COLS]
                    cols  = st.columns(COLS)
                    for col, r in zip(cols, chunk):
                        with col:
                            chg_color = "#22c55e" if r["Chg %"] >= 0 else "#ef4444"
                            chg_arrow = "▲" if r["Chg %"] >= 0 else "▼"
                            h52  = r["52W High"]
                            l52  = r["52W Low"]
                            curr = r["Price"]
                            range_pct = max(0, min(100, ((curr - l52) / (h52 - l52) * 100) if h52 > l52 else 50))
                            mc_str = f"${r['Mkt Cap']:.1f}B" if r["Mkt Cap"] > 0 else ""
                            st.markdown(f"""
                            <div class='card' style='padding:16px;margin-bottom:4px;'>
                              <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;'>
                                <div>
                                  <div style='font-size:16px;font-weight:800;color:#c8d8f0;'>{r['Ticker']}</div>
                                  <div style='font-size:11px;color:#4a6a8a;white-space:nowrap;overflow:hidden;max-width:130px;text-overflow:ellipsis;'>{r['Name']}</div>
                                </div>
                                <div style='text-align:right;'>
                                  <div style='font-size:18px;font-weight:700;color:#e8edf8;'>${curr:.2f}</div>
                                  <div style='font-size:12px;font-weight:600;color:{chg_color};'>{chg_arrow} {abs(r["Chg %"]):.2f}%</div>
                                </div>
                              </div>
                              {"<div style='font-size:10px;color:#4a6a8a;margin-bottom:4px;'>" + r['Sector'] + "</div>" if r['Sector'] else ""}
                              {f"<div style='font-size:10px;color:#3a5a7a;margin-bottom:6px;'>{mc_str}</div>" if mc_str else ""}
                              <div>
                                <div style='display:flex;justify-content:space-between;font-size:9px;color:#3a5a7a;margin-bottom:2px;'>
                                  <span>52W L ${l52:.0f}</span><span>52W H ${h52:.0f}</span>
                                </div>
                                <div style='background:rgba(255,255,255,0.06);border-radius:4px;height:4px;overflow:hidden;'>
                                  <div style='width:{range_pct:.0f}%;height:100%;background:linear-gradient(90deg,#1f77b4,#7c3aed);border-radius:4px;'></div>
                                </div>
                              </div>
                            </div>""", unsafe_allow_html=True)
                            c_a, c_r = st.columns(2)
                            if c_a.button("📊", key=f"wl_hub_an_{r['_ticker']}_{selected}", help="Analyze", use_container_width=True):
                                st.session_state.analyze_ticker = r["_ticker"]
                                st.switch_page("pages/hub_ai.py")
                            if c_r.button("✕", key=f"wl_hub_rm_{r['_ticker']}_{selected}", help="Remove", use_container_width=True):
                                tickers.remove(r["_ticker"])
                                watchlists[selected] = tickers
                                st.session_state.watchlists = watchlists
                                _autosave()
                                st.rerun()
        else:
            st.info("Add tickers to this watchlist above.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — ALERTS
# ══════════════════════════════════════════════════════════════════════════════
with tab_alerts:
    alerts = st.session_state.get("alerts", [])

    if st.button("🔄 Check Alerts Now", key="hub_check_alerts"):
        fired_count = 0
        for a in alerts:
            if a.get("triggered"):
                continue
            try:
                info, _ = get_stock_data(a["ticker"], "5d")
                price = (info or {}).get("currentPrice") or (info or {}).get("regularMarketPrice") or 0
                hit = (a["condition"] == "Price >" and price > a["threshold"]) or \
                      (a["condition"] == "Price <" and price < a["threshold"])
                if hit:
                    a["triggered"]    = True
                    a["triggered_at"] = price
                    a["triggered_ts"] = datetime.now().isoformat()
                    fired_count += 1
                    st.success(f"🔔 {a['ticker']} {a['condition']} ${a['threshold']:.2f} — now: ${price:.2f}")
            except Exception:
                pass
        st.session_state.alerts = alerts
        if fired_count == 0:
            st.info("No new alerts triggered.")

    with st.expander("➕ Add New Alert", expanded=not alerts):
        with st.form("new_alert_hub", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            ticker    = c1.text_input("Ticker", placeholder="AAPL, NVDA…")
            condition = c2.selectbox("Condition", ["Price >", "Price <"])
            threshold = c3.number_input("Threshold ($)", value=100.0, step=0.5)
            note = st.text_input("Notes (optional)", placeholder="Buy target, stop-loss…")
            if st.form_submit_button("🔔 Create Alert", type="primary"):
                if ticker:
                    alerts.append({"ticker": ticker.strip().upper(), "condition": condition,
                                   "threshold": threshold, "note": note, "triggered": False,
                                   "created_at": datetime.now().isoformat()})
                    st.session_state.alerts = alerts
                    _autosave()
                    st.success(f"Alert created for {ticker.upper()}")
                    st.rerun()

    active    = [a for a in alerts if not a.get("triggered")]
    triggered = [a for a in alerts if a.get("triggered")]
    c1, c2, c3 = st.columns(3)
    c1.metric("Active", len(active))
    c2.metric("Triggered", len(triggered))
    c3.metric("Total", len(alerts))

    if active:
        st.subheader("Active Alerts")
        for i, a in enumerate(alerts):
            if a.get("triggered"):
                continue
            curr_price = get_current_price(a["ticker"]) or 0
            threshold  = a["threshold"]
            if curr_price and threshold:
                if a["condition"] == "Price >":
                    pct_away = (threshold - curr_price) / curr_price * 100
                    prox_str = f"${curr_price:.2f} — {abs(pct_away):.1f}% {'above ✅' if curr_price >= threshold else 'below target'}"
                    prox_col = "#22c55e" if curr_price >= threshold else ("#f59e0b" if abs(pct_away) < 5 else "#8aadcc")
                else:
                    pct_away = (curr_price - threshold) / curr_price * 100
                    prox_str = f"${curr_price:.2f} — {abs(pct_away):.1f}% {'below ✅' if curr_price <= threshold else 'above target'}"
                    prox_col = "#22c55e" if curr_price <= threshold else ("#f59e0b" if abs(pct_away) < 5 else "#8aadcc")
            else:
                prox_str, prox_col = "—", "#4a6a8a"

            c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 2, 2, 1])
            c1.write(f"**{a['ticker']}**")
            c2.write(a["condition"])
            c3.write(f"${threshold:.2f}")
            c4.markdown(f"<span style='color:{prox_col};font-size:12px;font-weight:600;'>{prox_str}</span>", unsafe_allow_html=True)
            c5.write(a.get("note", ""))
            if c6.button("🗑️", key=f"hub_del_alert_{i}"):
                alerts.pop(i)
                st.session_state.alerts = alerts
                _autosave()
                st.rerun()
    else:
        st.info("No active alerts. Create one above.")

    if triggered:
        st.subheader("Triggered Alerts")
        df_t = pd.DataFrame([{"Ticker": a["ticker"], "Condition": a["condition"],
                               "Threshold": a["threshold"], "Triggered At": a.get("triggered_at",""),
                               "When": a.get("triggered_ts","")[:10], "Note": a.get("note","")}
                              for a in triggered])
        st.dataframe(df_t, use_container_width=True, hide_index=True)
        if st.button("Clear Triggered", key="hub_clear_triggered"):
            st.session_state.alerts = [a for a in alerts if not a.get("triggered")]
            _autosave()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — PROFILE
# ══════════════════════════════════════════════════════════════════════════════
with tab_profile:
    if "profile_step" not in st.session_state:
        st.session_state.profile_step = 1

    TOTAL_STEPS = 6
    step = st.session_state.profile_step
    st.progress((step - 1) / (TOTAL_STEPS - 1), text=f"Step {step} of {TOTAL_STEPS}")
    st.markdown("---")

    p = st.session_state.get("profile", {})

    if step == 1:
        st.subheader("Step 1 — Basic Info")
        name = st.text_input("Your name", value=p.get("nombre", ""), key="pr_name")
        age  = st.slider("Age", 18, 80, value=p.get("edad", 30), key="pr_age")
        stage_opts = ["Just starting out (early career, building savings)",
                      "Mid-career (established income, some investments)",
                      "Pre-retirement (planning for retirement)",
                      "Retired (living on savings)"]
        stage = st.radio("Life stage", stage_opts, index=p.get("stage_idx", 0), key="pr_stage")
        if st.button("Next →", key="pr_next1"):
            p.update({"nombre": name, "edad": age, "stage": stage, "stage_idx": stage_opts.index(stage)})
            st.session_state.profile = p
            st.session_state.profile_step = 2
            st.rerun()

    elif step == 2:
        st.subheader("Step 2 — Risk Mindset")
        st.write("*The market drops 30% in one month. What do you realistically do?*")
        opts = ["Sell everything and move to cash immediately",
                "Sell some positions to reduce the pain",
                "Hold tight and wait for recovery",
                "Hold and start looking for buying opportunities",
                "Aggressively add more — I love a sale"]
        riesgo = st.radio("Select:", opts, index=p.get("riesgo_idx", 4), key="pr_risk")
        mapping = {"Sell everything": "Very Conservative", "Sell some": "Conservative",
                   "Hold tight": "Moderate", "Hold and start": "Aggressive", "Aggressively": "Very Aggressive"}
        label = next((v for k, v in mapping.items() if riesgo.startswith(k)), "Moderate")
        col1, col2 = st.columns(2)
        if col1.button("← Back", key="pr_back2"): st.session_state.profile_step = 1; st.rerun()
        if col2.button("Next →", key="pr_next2"):
            p.update({"riesgo": label, "riesgo_raw": riesgo, "riesgo_idx": opts.index(riesgo)})
            st.session_state.profile = p; st.session_state.profile_step = 3; st.rerun()

    elif step == 3:
        st.subheader("Step 3 — Experience")
        exp_opts = ["Less than 1 year", "1-3 years", "3-7 years", "7-15 years", "More than 15 years"]
        exp = st.radio("How long have you been actively investing?", exp_opts, index=p.get("exp_idx", 0), key="pr_exp")
        instruments = st.multiselect("Which instruments have you traded?",
            ["Individual stocks", "ETFs / Index funds", "Crypto", "Options", "Bonds", "Real estate"],
            default=p.get("instruments", ["Individual stocks", "ETFs / Index funds"]), key="pr_inst")
        col1, col2 = st.columns(2)
        if col1.button("← Back", key="pr_back3"): st.session_state.profile_step = 2; st.rerun()
        if col2.button("Next →", key="pr_next3"):
            p.update({"experiencia": exp, "exp_idx": exp_opts.index(exp), "instruments": instruments})
            st.session_state.profile = p; st.session_state.profile_step = 4; st.rerun()

    elif step == 4:
        st.subheader("Step 4 — Preferences")
        style_opts = ["Passive / Index", "Dividend growth", "Value investing",
                      "Growth investing", "Momentum", "Mixed"]
        estilo = st.radio("Investment style:", style_opts, index=p.get("estilo_idx", 5), key="pr_style")
        objetivo_opts = ["Growth", "Income", "Balanced", "Speculation", "Capital preservation"]
        objetivo = st.selectbox("Primary objective:", objetivo_opts, index=p.get("obj_idx", 0), key="pr_obj")
        markets = st.multiselect("Markets:", ["US (NYSE / NASDAQ)", "México (BMV)", "Asia / Emerging", "Global"],
                                 default=p.get("markets", ["US (NYSE / NASDAQ)"]), key="pr_markets")
        col1, col2 = st.columns(2)
        if col1.button("← Back", key="pr_back4"): st.session_state.profile_step = 3; st.rerun()
        if col2.button("Next →", key="pr_next4"):
            p.update({"estilo": estilo, "estilo_idx": style_opts.index(estilo),
                      "objetivo": objetivo, "obj_idx": objetivo_opts.index(objetivo), "markets": markets})
            st.session_state.profile = p; st.session_state.profile_step = 5; st.rerun()

    elif step == 5:
        st.subheader("Step 5 — Financial Situation")
        horizon_opts = ["Short-term (< 1 year)", "Medium-term (1-5 years)",
                        "Long-term (5-15 years)", "Very long-term (15+ years)"]
        horizon = st.radio("Time horizon:", horizon_opts, index=p.get("horizon_idx", 2), key="pr_horizon")
        portfolio_size = st.select_slider("Approximate portfolio size:",
            options=["< $10k", "$10k – $50k", "$50k – $200k", "$200k – $1M", "$1M+"],
            value=p.get("portfolio_size", "$50k – $200k"), key="pr_size")
        col1, col2 = st.columns(2)
        if col1.button("← Back", key="pr_back5"): st.session_state.profile_step = 4; st.rerun()
        if col2.button("Next →", key="pr_next5"):
            p.update({"horizon": horizon, "horizon_idx": horizon_opts.index(horizon), "portfolio_size": portfolio_size})
            st.session_state.profile = p; st.session_state.profile_step = 6; st.rerun()

    elif step == 6:
        st.subheader("Step 6 — Review")
        if p:
            rows = {"Name": p.get("nombre","—"), "Age": str(p.get("edad","—")),
                    "Risk": p.get("riesgo","—"), "Experience": p.get("experiencia","—"),
                    "Style": p.get("estilo","—"), "Objective": p.get("objetivo","—"),
                    "Horizon": p.get("horizon","—"), "Portfolio Size": p.get("portfolio_size","—"),
                    "Markets": ", ".join(p.get("markets", []))}
            for k, v in rows.items():
                c1, c2 = st.columns([1, 2])
                c1.write(f"**{k}**"); c2.write(v)
        else:
            st.warning("Complete the previous steps first.")
        col1, col2 = st.columns(2)
        if col1.button("← Back", key="pr_back6"): st.session_state.profile_step = 5; st.rerun()
        if col2.button("✅ Save Profile", type="primary", key="pr_save"):
            st.session_state.profile = p
            _autosave()
            st.success("Profile saved! All AI analyses will be personalized for you.")
            st.session_state.profile_step = 1

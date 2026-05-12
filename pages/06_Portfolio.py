import streamlit as st
import pandas as pd
from datetime import date
from utils.data import get_stock_data
from utils.plots import portfolio_pie
from utils.db import save_user_data, is_configured

def _autosave():
    if is_configured():
        save_user_data(st.session_state.get("username", ""))

st.markdown("""
<div class='page-header'>
  <div class='page-title'>💼 Portfolio Manager</div>
  <div class='page-subtitle'>Track positions, analyze performance, get AI rebalancing advice</div>
</div>""", unsafe_allow_html=True)

portfolio = st.session_state.get("portfolio", [])

def _refresh_prices(holdings):
    updated = []
    for h in holdings:
        try:
            info, _ = get_stock_data(h["ticker"], "5d")
            price = info.get("currentPrice") or info.get("regularMarketPrice") or h["purchase_price"]
        except Exception:
            price = h["purchase_price"]
        qty        = h["quantity"]
        cost       = h["purchase_price"] * qty
        value      = price * qty
        gain       = value - cost
        gain_pct   = (gain / cost * 100) if cost else 0
        updated.append({**h, "current_price": round(price, 2),
                        "current_value": round(value, 2), "cost_basis": round(cost, 2),
                        "gain": round(gain, 2), "gain_pct": round(gain_pct, 2)})
    return updated

tab_ov, tab_edit, tab_rb, tab_risk = st.tabs(["Overview", "Edit Holdings", "Rebalance", "Risk Analytics"])

# ── Edit Holdings ─────────────────────────────────────────────────────────────
with tab_edit:
    st.subheader("Add Position")
    with st.form("add_holding", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        new_ticker = c1.text_input("Ticker", placeholder="AAPL")
        new_qty    = c2.number_input("Quantity", min_value=0.001, value=1.0, step=1.0)
        new_price  = c3.number_input("Avg Purchase Price ($)", min_value=0.01, value=100.0)
        new_date   = c4.date_input("Purchase Date", value=date.today())
        add = st.form_submit_button("➕ Add Position", type="primary")
        if add and new_ticker:
            portfolio.append({
                "ticker":         new_ticker.strip().upper(),
                "quantity":       new_qty,
                "purchase_price": new_price,
                "purchase_date":  str(new_date),
            })
            st.session_state.portfolio = portfolio
            _autosave()
            st.success(f"Added {new_ticker.upper()} ☁️")
            st.rerun()

    if portfolio:
        st.subheader("Current Holdings")
        for i, h in enumerate(portfolio):
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
            c1.write(f"**{h['ticker']}**")
            c2.write(f"{h['quantity']} shares")
            c3.write(f"${h['purchase_price']:.2f}")
            c4.write(h.get("purchase_date", ""))
            if c5.button("🗑️", key=f"del_{i}"):
                portfolio.pop(i)
                st.session_state.portfolio = portfolio
                _autosave()
                st.rerun()
    else:
        st.info("No holdings yet. Add your first position above.")

# ── Overview ──────────────────────────────────────────────────────────────────
with tab_ov:
    if not portfolio:
        st.markdown("""
        <div class='card' style='text-align:center;color:#888;padding:32px;'>
          No holdings yet. Go to <strong>Edit Holdings</strong> to add your positions.
        </div>""", unsafe_allow_html=True)
    else:
        with st.spinner("Refreshing prices…"):
            holdings = _refresh_prices(portfolio)
        st.session_state.portfolio = holdings

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
            st.plotly_chart(portfolio_pie(holdings), use_container_width=True)

        with col_table:
            df = pd.DataFrame([{
                "Ticker":     h["ticker"],
                "Qty":        h["quantity"],
                "Avg Cost":   h["purchase_price"],
                "Curr Price": h["current_price"],
                "Value":      h["current_value"],
                "Gain $":     h["gain"],
                "Gain %":     h["gain_pct"],
                "Weight %":   round(h["current_value"] / total_val * 100, 1) if total_val else 0,
            } for h in holdings])
            st.dataframe(df, use_container_width=True, hide_index=True,
                column_config={
                    "Avg Cost":   st.column_config.NumberColumn(format="$%.2f"),
                    "Curr Price": st.column_config.NumberColumn(format="$%.2f"),
                    "Value":      st.column_config.NumberColumn(format="$%.2f"),
                    "Gain $":     st.column_config.NumberColumn(format="$%+.2f"),
                    "Gain %":     st.column_config.NumberColumn(format="%.2f%%"),
                    "Weight %":   st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
                })

# ── Rebalance ─────────────────────────────────────────────────────────────────
with tab_rb:
    st.subheader("Rebalancing Advisor")
    if not portfolio:
        st.info("Add holdings first.")
    else:
        from utils.ai import has_key, no_key_banner, chat
        if not has_key():
            no_key_banner("AI rebalancing advice")
        else:
            if st.button("🤖 Generate Rebalancing Advice", type="primary"):
                holdings = _refresh_prices(portfolio)
                total    = sum(h["current_value"] for h in holdings)
                ctx = "PORTFOLIO:\n" + "\n".join(
                    f"{h['ticker']}: {h['quantity']} shares @ ${h['current_price']:.2f} = ${h['current_value']:,.0f} ({h['current_value']/total*100:.1f}%)"
                    for h in holdings)
                profile = st.session_state.get("profile", {})
                prompt  = f"{ctx}\n\nProfile: Risk={profile.get('riesgo','moderate')}, Style={profile.get('estilo','mixed')}, Objective={profile.get('objetivo','growth')}\n\nProvide specific rebalancing recommendations: overweight/underweight positions, concentration risks, suggested target weights, and 2-3 tactical changes."
                with st.spinner("Generating advice…"):
                    resp = chat([{"role": "user", "content": prompt}])
                if resp:
                    st.markdown(resp)

# ── Risk Analytics ────────────────────────────────────────────────────────────
with tab_risk:
    st.subheader("Risk Analytics")
    if not portfolio:
        st.info("Add holdings first.")
    else:
        holdings = _refresh_prices(portfolio)
        total    = sum(h["current_value"] for h in holdings)

        # Sector & concentration
        tickers   = [h["ticker"] for h in holdings]
        sectors   = {}
        for h in holdings:
            try:
                info, _ = get_stock_data(h["ticker"], "5d")
                sec = info.get("sector", "Unknown") if info else "Unknown"
            except Exception:
                sec = "Unknown"
            sectors[sec] = sectors.get(sec, 0) + h.get("current_value", 0)

        st.write("**Sector Exposure**")
        for sec, val in sorted(sectors.items(), key=lambda x: -x[1]):
            pct = val / total * 100 if total else 0
            st.progress(pct / 100, text=f"{sec}: {pct:.1f}%")

        top_pct = max(h.get("current_value", 0) for h in holdings) / total * 100 if total else 0
        st.metric("Top Concentration", f"{top_pct:.1f}%",
                  delta="High risk" if top_pct > 30 else "OK",
                  delta_color="inverse" if top_pct > 30 else "normal")

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data import get_stock_data
from utils.db import save_user_data, is_configured

def _autosave():
    if is_configured():
        save_user_data(st.session_state.get("username", ""))

st.markdown("""
<div class='page-header'>
  <div class='page-title'>🔔 Price Alerts</div>
  <div class='page-subtitle'>Set thresholds — alerts fire automatically on every page load</div>
</div>""", unsafe_allow_html=True)

alerts = st.session_state.get("alerts", [])

# ── Manual check ──────────────────────────────────────────────────────────────
if st.button("🔄 Check Alerts Now"):
    fired_count = 0
    for a in alerts:
        if a.get("triggered"):
            continue
        try:
            info, _ = get_stock_data(a["ticker"], "5d")
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            hit = (a["condition"] == "Price >" and price > a["threshold"]) or \
                  (a["condition"] == "Price <" and price < a["threshold"])
            if hit:
                a["triggered"]    = True
                a["triggered_at"] = price
                a["triggered_ts"] = datetime.now().isoformat()
                fired_count += 1
                st.success(f"🔔 {a['ticker']} {a['condition']} ${a['threshold']:.2f} — current: ${price:.2f}")
        except Exception:
            pass
    st.session_state.alerts = alerts
    if fired_count == 0:
        st.info("No new alerts triggered.")

st.divider()

# ── Add New Alert ─────────────────────────────────────────────────────────────
with st.expander("➕ Add New Alert", expanded=not alerts):
    with st.form("new_alert", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        ticker    = c1.text_input("Ticker", placeholder="AAPL, NVDA, AMXL.MX…")
        condition = c2.selectbox("Condition", ["Price >", "Price <", "Change % >", "Change % <"])
        threshold = c3.number_input("Threshold", value=100.0, step=0.5)
        note = st.text_input("Notes (optional)", placeholder="e.g. Buy target, stop-loss…")
        if st.form_submit_button("🔔 Create Alert", type="primary"):
            if ticker:
                alerts.append({
                    "ticker":     ticker.strip().upper(),
                    "condition":  condition,
                    "threshold":  threshold,
                    "note":       note,
                    "triggered":  False,
                    "created_at": datetime.now().isoformat(),
                })
                st.session_state.alerts = alerts
                _autosave()
                st.success(f"Alert created for {ticker.upper()}")
                st.rerun()

st.divider()

# ── Stats ─────────────────────────────────────────────────────────────────────
active    = [a for a in alerts if not a.get("triggered")]
triggered = [a for a in alerts if a.get("triggered")]
c1, c2, c3 = st.columns(3)
c1.metric("Active Alerts",     len(active))
c2.metric("Triggered (Total)", len(triggered))
c3.metric("Total Alerts",      len(alerts))

# ── Active Alerts Table ───────────────────────────────────────────────────────
st.subheader("Active Alerts")
if not active:
    st.markdown("""
    <div class='card' style='text-align:center;color:#888;padding:28px;'>
      No active alerts. Add one above.
    </div>""", unsafe_allow_html=True)
else:
    for i, a in enumerate(alerts):
        if a.get("triggered"):
            continue
        c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 3, 1])
        c1.write(f"**{a['ticker']}**")
        c2.write(a["condition"])
        c3.write(f"${a['threshold']:.2f}")
        c4.write(a.get("note", ""))
        if c5.button("🗑️", key=f"del_alert_{i}"):
            alerts.pop(i)
            st.session_state.alerts = alerts
            _autosave()
            st.rerun()

# ── Triggered Alerts ──────────────────────────────────────────────────────────
if triggered:
    st.subheader("Triggered Alerts")
    df = pd.DataFrame([{
        "Ticker":        a["ticker"],
        "Condition":     a["condition"],
        "Threshold":     a["threshold"],
        "Triggered At":  a.get("triggered_at",""),
        "When":          a.get("triggered_ts","")[:10],
        "Note":          a.get("note",""),
    } for a in triggered])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("Clear Triggered Alerts"):
        st.session_state.alerts = [a for a in alerts if not a.get("triggered")]
        _autosave()
        st.rerun()

import streamlit as st
from datetime import date
from utils.data import get_market_overview, get_market_sparklines
from utils.plots import sparkline
from utils.config import COLOR_SUCCESS, COLOR_DANGER

today = date.today().strftime("%a, %b %d %Y")

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex;align-items:flex-start;justify-content:space-between;
            margin-bottom:1.8rem;padding-bottom:1.2rem;
            border-bottom:1px solid var(--border-subtle);flex-wrap:wrap;gap:8px;'>
  <div>
    <div style='font-family:"Plus Jakarta Sans",sans-serif;font-size:1.7rem;font-weight:900;
                color:var(--text-primary);letter-spacing:-0.8px;line-height:1.2;'>Overview</div>
    <div style='font-size:0.8rem;color:var(--text-muted);margin-top:4px;
                font-family:"Space Grotesk",sans-serif;'>Your financial command center</div>
  </div>
  <div style='display:flex;align-items:center;gap:10px;padding-top:4px;'>
    <span class='live-badge'>Live</span>
    <span style='color:var(--text-muted);font-size:11px;font-family:"Space Grotesk",sans-serif;'>{today}</span>
  </div>
</div>""", unsafe_allow_html=True)

# ── Market Pulse ───────────────────────────────────────────────────────────────
st.markdown("<div class='y-section-label'>Market Pulse</div>", unsafe_allow_html=True)

with st.spinner(""):
    mkt    = get_market_overview()
    sparks = get_market_sparklines()

cols = st.columns(len(mkt))
for col, (name, d) in zip(cols, mkt.items()):
    pct   = d["change_pct"]
    price = d["price"]
    color = "#34d399" if pct >= 0 else "#fb7185"
    arrow = "▲" if pct >= 0 else "▼"
    fmt   = f"${price:,.2f}" if name in ("Gold","Oil WTI") else \
            f"{price:.2f}%" if name == "10Y Yield" else f"{price:,.2f}"
    with col:
        st.metric(label=name, value=fmt, delta=f"{arrow} {abs(pct):.2f}%", delta_color="normal")
        series = sparks.get(name, [])
        if len(series) > 3:
            st.plotly_chart(sparkline(series), use_container_width=True,
                            config={"displayModeBar": False}, key=f"spark_{name}")

st.divider()

# ── Portfolio snapshot ─────────────────────────────────────────────────────────
portfolio = st.session_state.get("portfolio", [])

col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("<div class='y-section-label'>Portfolio</div>", unsafe_allow_html=True)

    if not portfolio:
        st.markdown("""
        <div class='card' style='text-align:center;padding:32px 24px;'>
          <div style='font-size:28px;margin-bottom:10px;opacity:0.4;'>💼</div>
          <div style='font-size:14px;font-weight:600;color:var(--text-secondary);margin-bottom:6px;'>No holdings yet</div>
          <div style='font-size:12px;color:var(--text-muted);'>
            Go to <strong style='color:var(--accent-blue);'>Holdings</strong> to add your first position
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("+ Add Holdings", type="primary"):
            st.switch_page("pages/hub_portfolio.py")
    else:
        total = sum(h.get("current_value", 0) for h in portfolio)
        cost  = sum(h.get("cost_basis", 0)    for h in portfolio)
        gain  = total - cost
        pct   = (gain / cost * 100) if cost > 0 else 0

        # Summary metrics — compact row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Value",  f"${total:,.0f}")
        m2.metric("Cost Basis",   f"${cost:,.0f}")
        m3.metric("P&L",          f"${gain:+,.0f}", f"{pct:+.2f}%")
        m4.metric("Positions",    str(len(portfolio)))

        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        # Top positions table (compact)
        sorted_port = sorted(portfolio, key=lambda x: x.get("current_value", 0), reverse=True)
        for h in sorted_port[:5]:
            ticker = h.get("ticker", "")
            val    = h.get("current_value", 0)
            cost_h = h.get("cost_basis", 0)
            pnl    = val - cost_h
            pnl_pct = (pnl / cost_h * 100) if cost_h else 0
            chg_color = "#34d399" if pnl >= 0 else "#fb7185"
            pct_total = (val / total * 100) if total else 0

            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:12px;padding:8px 0;
                        border-bottom:1px solid var(--border-subtle);'>
              <span class='ticker-chip'>{ticker}</span>
              <div style='flex:1;'>
                <div style='background:var(--bg-overlay);border-radius:3px;height:3px;overflow:hidden;'>
                  <div style='width:{min(pct_total,100):.0f}%;height:100%;
                              background:linear-gradient(90deg,var(--accent-blue),var(--accent-violet));
                              border-radius:3px;'></div>
                </div>
              </div>
              <span style='font-family:"JetBrains Mono",monospace;font-size:12px;
                           font-weight:600;color:var(--text-secondary);min-width:60px;text-align:right;'>
                ${val:,.0f}
              </span>
              <span style='font-family:"JetBrains Mono",monospace;font-size:11px;
                           color:{chg_color};min-width:50px;text-align:right;font-weight:600;'>
                {pnl_pct:+.1f}%
              </span>
            </div>""", unsafe_allow_html=True)

        if len(portfolio) > 5:
            if st.button(f"View all {len(portfolio)} positions →", type="secondary"):
                st.switch_page("pages/hub_portfolio.py")

with col_right:
    # ── Active Alerts ──────────────────────────────────────────────────────────
    alerts = [a for a in st.session_state.get("alerts", []) if not a.get("triggered")]
    st.markdown(f"<div class='y-section-label'>Active Alerts <span style='color:var(--accent-blue);font-size:11px;'>({len(alerts)})</span></div>",
                unsafe_allow_html=True)

    if not alerts:
        st.markdown("""
        <div class='card' style='text-align:center;padding:18px;'>
          <div style='font-size:11px;color:var(--text-muted);'>No active alerts</div>
          <div style='font-size:10px;color:var(--text-disabled);margin-top:4px;'>Set price thresholds in Alerts</div>
        </div>""", unsafe_allow_html=True)
    else:
        for a in alerts[:4]:
            cond_color = "#34d399" if ">" in a["condition"] else "#fb7185"
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;padding:7px 0;
                        border-bottom:1px solid var(--border-subtle);'>
              <span class='ticker-chip'>{a['ticker']}</span>
              <span style='font-size:11px;color:var(--text-muted);flex:1;font-family:"Space Grotesk",sans-serif;'>
                {a['condition']}
              </span>
              <span style='font-family:"JetBrains Mono",monospace;font-size:12px;
                           font-weight:600;color:{cond_color};'>
                ${a['threshold']:.2f}
              </span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Watchlists quick view ──────────────────────────────────────────────────
    watchlists = st.session_state.get("watchlists", {})
    st.markdown(f"<div class='y-section-label'>Watchlists <span style='color:var(--accent-blue);font-size:11px;'>({len(watchlists)})</span></div>",
                unsafe_allow_html=True)

    if not watchlists:
        st.markdown("""
        <div class='card' style='text-align:center;padding:18px;'>
          <div style='font-size:11px;color:var(--text-muted);'>No watchlists yet</div>
        </div>""", unsafe_allow_html=True)
    else:
        for wl_name, tickers in list(watchlists.items())[:3]:
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;padding:7px 0;
                        border-bottom:1px solid var(--border-subtle);'>
              <div style='flex:1;'>
                <div style='font-size:12px;font-weight:600;color:var(--text-primary);
                            font-family:"Space Grotesk",sans-serif;'>{wl_name}</div>
                <div style='font-size:10px;color:var(--text-muted);margin-top:1px;
                            font-family:"Space Grotesk",sans-serif;'>
                  {', '.join(tickers[:4])}{'…' if len(tickers)>4 else ''}
                </div>
              </div>
              <span class='badge badge-muted'>{len(tickers)}</span>
            </div>""", unsafe_allow_html=True)

st.divider()

# ── Quick Actions + Features ───────────────────────────────────────────────────
col_qs, col_feat = st.columns(2, gap="large")

with col_qs:
    st.markdown("<div class='y-section-label'>Quick Start</div>", unsafe_allow_html=True)
    steps = [
        ("Add holdings in <strong>My Portfolio</strong>",          "pages/hub_portfolio.py"),
        ("Run the <strong>Screener</strong> for top picks",       "pages/hub_discover.py"),
        ("Deep <strong>Analysis</strong> with AI scoring",        "pages/hub_ai.py"),
        ("Generate <strong>Morning Brief</strong> by email",      "pages/hub_intelligence.py"),
    ]
    for i, (text, page) in enumerate(steps, 1):
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:10px;cursor:default;'>
          <div class='step-num'>{i}</div>
          <span style='font-size:12.5px;color:var(--text-secondary);font-family:"Space Grotesk",sans-serif;'>{text}</span>
        </div>""", unsafe_allow_html=True)

with col_feat:
    st.markdown("<div class='y-section-label'>Features</div>", unsafe_allow_html=True)
    features = [
        ("◆", "Deep Analysis",   "6-dimension scoring + Claude AI"),
        ("◇", "Screener",        "Rank stocks across sectors"),
        ("💼", "Portfolio",      "Track & rebalance positions"),
        ("◈", "AI Chat",         "Portfolio advisor, 24/7"),
        ("☀️", "Morning Brief",  "AI market briefing by email"),
        ("⚡", "Backtester",     "Strategy simulation"),
    ]
    for icon, name, desc in features:
        st.markdown(f"""
        <div class='feature-card'>
          <div class='feature-icon'>{icon}</div>
          <div>
            <div class='feature-name'>{name}</div>
            <div class='feature-desc'>{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ── Recent Analyses ────────────────────────────────────────────────────────────
analyses = st.session_state.get("analyses", [])

st.markdown("<div class='y-section-label'>Recent Analyses</div>", unsafe_allow_html=True)

if not analyses:
    st.markdown("""
    <div class='card' style='text-align:center;padding:24px;'>
      <div style='font-size:11px;color:var(--text-muted);'>No analyses yet</div>
      <div style='font-size:10px;color:var(--text-disabled);margin-top:4px;'>
        Go to <strong style='color:var(--accent-blue);'>Deep Analysis</strong> to get started
      </div>
    </div>""", unsafe_allow_html=True)
else:
    for a in reversed(analyses[-5:]):
        score      = a.get("score", a.get("composite", 0)) or 0
        rec        = a.get("rec", "")
        tier_color = "#34d399" if score >= 6.5 else "#fbbf24" if score >= 4.0 else "#fb7185"

        c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 1])
        c1.markdown(f"<span class='ticker-chip'>{a['ticker']}</span>", unsafe_allow_html=True)
        c2.markdown(f"<span style='color:var(--text-muted);font-size:11px;font-family:\"Space Grotesk\",sans-serif;'>{a.get('name','')}</span>", unsafe_allow_html=True)
        c3.markdown(f"<span style='color:{tier_color};font-size:11px;font-weight:700;font-family:\"Space Grotesk\",sans-serif;'>{rec}</span>", unsafe_allow_html=True)
        c4.markdown(f"<span class='stat-pill'>{score:.1f}</span>", unsafe_allow_html=True)
        c5.markdown(f"<span style='color:var(--text-muted);font-size:11px;font-family:\"Space Grotesk\",sans-serif;'>{a.get('date','')}</span>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import io
from utils.data import get_current_price, get_stock_data
from utils.db import save_user_data, is_configured

def _autosave():
    if is_configured():
        save_user_data(st.session_state.get("username", ""))

st.markdown("""
<div class='page-header'>
  <div class='page-title'>👁️ Watchlists</div>
  <div class='page-subtitle'>Track, compare, and analyze your saved tickers in one place</div>
</div>""", unsafe_allow_html=True)

watchlists = st.session_state.get("watchlists", {})

# ── Create New ─────────────────────────────────────────────────────────────────
if not watchlists:
    st.markdown("""
    <div class='card' style='text-align:center;color:#4a6a8a;padding:28px;'>
      You have no watchlists yet. Create one below to get started.
    </div>""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
wl_name_new = col1.text_input("Watchlist name", placeholder="Tech Picks, Dividend Portfolio…",
                               label_visibility="collapsed")
if col2.button("➕ Create") and wl_name_new:
    if wl_name_new not in watchlists:
        watchlists[wl_name_new] = []
        st.session_state.watchlists = watchlists
        _autosave()
        st.success(f"Created watchlist: {wl_name_new}")
        st.rerun()
    else:
        st.warning("A watchlist with that name already exists.")

st.divider()

# ── Import from Yahoo Finance CSV ──────────────────────────────────────────────
with st.expander("📥 Import Watchlist from Yahoo Finance"):
    st.markdown("""
    <div style='color:#8aadcc;font-size:13px;line-height:1.8;'>
      <strong>How to export from Yahoo Finance:</strong><br>
      1. Go to <strong>finance.yahoo.com</strong> → sign in → <strong>My Portfolio</strong><br>
      2. Open any watchlist and click the <strong>Download</strong> button (↓)<br>
      3. Upload the CSV below — the app will read all ticker symbols
    </div>
    """, unsafe_allow_html=True)

    wl_csv = st.file_uploader("Upload Yahoo Finance Watchlist CSV", type=["csv"], key="wl_csv")
    import_name = st.text_input("Save as watchlist name:", placeholder="My YF Watchlist", key="wl_import_name")

    if wl_csv and import_name:
        try:
            content = wl_csv.read().decode("utf-8", errors="replace")
            df_wl   = pd.read_csv(io.StringIO(content))
            df_wl.columns = [c.strip() for c in df_wl.columns]
            col_name = next((c for c in df_wl.columns if c.lower() in ("symbol", "ticker")), df_wl.columns[0])
            raw_tickers = [str(v).strip().upper() for v in df_wl[col_name]
                           if str(v).strip() and str(v).strip().upper() != "NAN"]
            st.write(f"Found **{len(raw_tickers)}** tickers: {', '.join(raw_tickers[:10])}{'…' if len(raw_tickers)>10 else ''}")
            if st.button("✅ Import as Watchlist", type="primary", key="wl_import_btn"):
                watchlists[import_name] = list(dict.fromkeys(raw_tickers))
                st.session_state.watchlists = watchlists
                _autosave()
                st.success(f"Imported {len(raw_tickers)} tickers into '{import_name}'")
                st.rerun()
        except Exception as e:
            st.error(f"Could not parse CSV: {e}")

st.divider()

if not watchlists:
    st.stop()

# ── Select Watchlist ───────────────────────────────────────────────────────────
selected = st.selectbox("Select watchlist:", list(watchlists.keys()))
tickers  = watchlists.get(selected, [])

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    add_raw = st.text_input("Add tickers:", placeholder="AAPL, MSFT, NVDA",
                             label_visibility="collapsed")
with col2:
    if st.button("➕ Add", use_container_width=True):
        new_tickers = [t.strip().upper() for t in add_raw.split(",") if t.strip()]
        tickers = list(dict.fromkeys(tickers + new_tickers))
        watchlists[selected] = tickers
        st.session_state.watchlists = watchlists
        _autosave()
        st.rerun()
with col3:
    if st.button("🗑️ Delete List", use_container_width=True):
        del watchlists[selected]
        st.session_state.watchlists = watchlists
        _autosave()
        st.rerun()

if not tickers:
    st.info("Add tickers to this watchlist above.")
    st.stop()

st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:4px;'>{len(tickers)} tickers</div>",
            unsafe_allow_html=True)

# ── Live Prices (auto-load) ────────────────────────────────────────────────────
with st.spinner(f"Loading live prices for {len(tickers)} tickers…"):
    rows = []
    for t in tickers:
        price = get_current_price(t)
        try:
            info, _ = get_stock_data(t, "5d")
        except Exception:
            info = {}
        if info is None:
            info = {}

        curr = price or info.get("currentPrice") or info.get("regularMarketPrice") or 0
        prev = info.get("previousClose", curr) or curr
        chg  = ((curr - prev) / prev * 100) if prev else 0
        rows.append({
            "_ticker":    t,
            "Ticker":     t,
            "Name":       info.get("shortName", t),
            "Price":      round(curr, 2),
            "Chg %":      round(chg, 2),
            "52W High":   info.get("fiftyTwoWeekHigh") or 0,
            "52W Low":    info.get("fiftyTwoWeekLow") or 0,
            "Mkt Cap":    (info.get("marketCap") or 0) / 1e9,
            "Sector":     info.get("sector", ""),
        })

# ── Render cards ──────────────────────────────────────────────────────────────
st.subheader(f"{selected}")

if rows:
    # Summary bar
    positive = sum(1 for r in rows if r["Chg %"] >= 0)
    negative = len(rows) - positive
    st.markdown(f"""
    <div style='display:flex;gap:16px;margin-bottom:16px;'>
      <span style='color:#22c55e;font-size:12px;font-weight:600;'>▲ {positive} up</span>
      <span style='color:#ef4444;font-size:12px;font-weight:600;'>▼ {negative} down</span>
    </div>""", unsafe_allow_html=True)

    # Card grid
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
                range_pct = ((curr - l52) / (h52 - l52) * 100) if h52 > l52 else 50
                range_pct = max(0, min(100, range_pct))
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
                  <div style='margin-bottom:2px;'>
                    <div style='display:flex;justify-content:space-between;font-size:9px;color:#3a5a7a;margin-bottom:2px;'>
                      <span>52W L ${l52:.0f}</span><span>52W H ${h52:.0f}</span>
                    </div>
                    <div style='background:rgba(255,255,255,0.06);border-radius:4px;height:4px;overflow:hidden;'>
                      <div style='width:{range_pct:.0f}%;height:100%;background:linear-gradient(90deg,#1f77b4,#7c3aed);border-radius:4px;'></div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

                c_a, c_r = st.columns(2)
                if c_a.button("📊", key=f"an_{r['_ticker']}_{selected}", help="Analyze",
                               use_container_width=True):
                    st.session_state.analyze_ticker = r["_ticker"]
                    st.switch_page("pages/04_Analysis.py")
                if c_r.button("✕", key=f"rm_{r['_ticker']}_{selected}", help="Remove",
                               use_container_width=True):
                    tickers.remove(r["_ticker"])
                    watchlists[selected] = tickers
                    st.session_state.watchlists = watchlists
                    _autosave()
                    st.rerun()

st.divider()

# ── Quick actions ──────────────────────────────────────────────────────────────
if st.button("🔍 Run Screener on this list", type="primary"):
    st.session_state["screener_tickers_override"] = tickers
    st.switch_page("pages/03_Screener.py")

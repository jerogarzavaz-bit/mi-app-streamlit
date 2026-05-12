import streamlit as st
import pandas as pd
from utils.data import get_stock_data
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
    <div class='card' style='text-align:center;color:#888;padding:28px;'>
      You have no watchlists yet. Create one below to get started.
    </div>""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
wl_name = col1.text_input("Watchlist name", placeholder="Tech Picks, Dividend Portfolio…")
if col2.button("➕ Create") and wl_name:
    if wl_name not in watchlists:
        watchlists[wl_name] = []
        st.session_state.watchlists = watchlists
        _autosave()
        st.success(f"Created watchlist: {wl_name}")
        st.rerun()
    else:
        st.warning("A watchlist with that name already exists.")

st.divider()

# ── Import Watchlist from Yahoo Finance CSV ────────────────────────────────────
with st.expander("📥 Import Watchlist from Yahoo Finance"):
    import pandas as pd, io
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
            df_wl = pd.read_csv(io.StringIO(content))
            df_wl.columns = [c.strip() for c in df_wl.columns]
            col = next((c for c in df_wl.columns if c.lower() in ("symbol", "ticker")), df_wl.columns[0])
            raw_tickers = [str(v).strip().upper() for v in df_wl[col] if str(v).strip() and str(v).strip().upper() != "NAN"]
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
    add_raw = st.text_input("Add tickers:", placeholder="AAPL, MSFT, NVDA")
with col2:
    if st.button("➕ Add"):
        new_tickers = [t.strip().upper() for t in add_raw.split(",") if t.strip()]
        tickers = list(dict.fromkeys(tickers + new_tickers))  # dedup
        watchlists[selected] = tickers
        st.session_state.watchlists = watchlists
        _autosave()
        st.rerun()
with col3:
    if st.button("🗑️ Delete List"):
        del watchlists[selected]
        st.session_state.watchlists = watchlists
        _autosave()
        st.rerun()

if not tickers:
    st.info("Add tickers to this watchlist above.")
    st.stop()

# ── View & Remove ──────────────────────────────────────────────────────────────
st.subheader(f"{selected} — {len(tickers)} stocks")
cols_per_row = 5
for i in range(0, len(tickers), cols_per_row):
    row_tickers = tickers[i:i+cols_per_row]
    row_cols    = st.columns(cols_per_row)
    for col, t in zip(row_cols, row_tickers):
        with col:
            st.markdown(f"**{t}**")
            if st.button("✕", key=f"rm_{t}_{selected}", help=f"Remove {t}"):
                tickers.remove(t)
                watchlists[selected] = tickers
                st.session_state.watchlists = watchlists
                st.rerun()

st.divider()

# ── Live Prices ────────────────────────────────────────────────────────────────
if st.button("📊 Load Live Prices", type="primary"):
    with st.spinner("Fetching prices…"):
        rows = []
        for t in tickers:
            info, _ = get_stock_data(t, "5d")
            if info:
                price  = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                prev   = info.get("previousClose", price) or price
                chg    = ((price - prev) / prev * 100) if prev else 0
                rows.append({
                    "Ticker":  t,
                    "Name":    info.get("shortName", t),
                    "Price":   round(price, 2),
                    "Chg %":   round(chg, 2),
                    "52W High":info.get("fiftyTwoWeekHigh", 0),
                    "52W Low": info.get("fiftyTwoWeekLow",  0),
                    "Sector":  info.get("sector", "N/A"),
                })
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True,
            column_config={
                "Price":    st.column_config.NumberColumn(format="$%.2f"),
                "Chg %":    st.column_config.NumberColumn(format="%.2f%%"),
                "52W High": st.column_config.NumberColumn(format="$%.2f"),
                "52W Low":  st.column_config.NumberColumn(format="$%.2f"),
            })
        # Quick actions
        col1, col2 = st.columns(2)
        if col1.button("🔍 Run Screener on this list"):
            from utils.config import TICKERS_US
            st.session_state["screener_tickers_override"] = tickers
            st.switch_page("pages/03_Screener.py")

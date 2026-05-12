import streamlit as st
import pandas as pd
from datetime import date
from utils.data import get_stock_data, get_current_price
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


def _fetch_price(ticker: str, purchase_price: float) -> tuple[float, bool]:
    """Return (live_price, is_live). Falls back to purchase_price only as last resort."""
    price = get_current_price(ticker)
    if price and price > 0:
        return price, True
    return purchase_price, False


def _refresh_prices(holdings: list) -> list:
    updated = []
    for h in holdings:
        price, is_live = _fetch_price(h["ticker"], h.get("purchase_price", 0))
        qty        = h.get("quantity", 0)
        buy_price  = h.get("purchase_price", 0)
        cost       = buy_price * qty
        value      = price * qty
        gain       = value - cost
        gain_pct   = (gain / cost * 100) if cost else 0
        updated.append({
            **h,
            "current_price":  price,
            "is_live":        is_live,
            "current_value":  round(value, 2),
            "cost_basis":     round(cost, 2),
            "gain":           round(gain, 2),
            "gain_pct":       round(gain_pct, 2),
        })
    return updated


def _parse_yf_csv(file) -> list[dict]:
    """
    Parse a Yahoo Finance portfolio CSV export.
    YF columns (portfolio): Symbol, Current Price, Date, Time, Change, Open,
    High, Low, Volume, Trade Date, Purchase Price, Quantity, Commission, ...
    YF columns (watchlist): Symbol, Current Price, Date, Time, Change, ...
    Returns list of holding dicts compatible with this app.
    """
    import io
    try:
        content = file.read().decode("utf-8", errors="replace")
        df = pd.read_csv(io.StringIO(content))
        df.columns = [c.strip() for c in df.columns]
        holdings = []
        for _, row in df.iterrows():
            ticker = str(row.get("Symbol", "")).strip().upper()
            if not ticker or ticker == "NAN":
                continue
            # Purchase price: try multiple column names YF uses
            buy_price = None
            for col in ("Purchase Price", "Cost", "Avg Cost", "Buy Price"):
                v = row.get(col)
                if v and str(v).strip() not in ("", "N/A", "nan"):
                    try:
                        buy_price = float(str(v).replace("$", "").replace(",", ""))
                        break
                    except ValueError:
                        pass
            # Quantity
            qty = None
            for col in ("Quantity", "Shares", "Qty"):
                v = row.get(col)
                if v and str(v).strip() not in ("", "N/A", "nan"):
                    try:
                        qty = float(str(v).replace(",", ""))
                        break
                    except ValueError:
                        pass
            # Purchase date
            purchase_date = None
            for col in ("Trade Date", "Purchase Date", "Date Acquired"):
                v = row.get(col)
                if v and str(v).strip() not in ("", "N/A", "nan"):
                    purchase_date = str(v).strip()
                    break
            holdings.append({
                "ticker":         ticker,
                "quantity":       qty if qty else 1.0,
                "purchase_price": buy_price if buy_price else 0.0,
                "purchase_date":  purchase_date or date.today().isoformat(),
                "_from_yf":       True,
                "_needs_price":   buy_price is None,
            })
        return holdings
    except Exception as e:
        st.error(f"Could not parse CSV: {e}")
        return []


tab_ov, tab_edit, tab_rb, tab_risk = st.tabs(["Overview", "Edit Holdings", "Rebalance", "Risk Analytics"])

# ── Edit Holdings ──────────────────────────────────────────────────────────────
with tab_edit:

    # ── Yahoo Finance Import ───────────────────────────────────────────────────
    with st.expander("📥 Import from Yahoo Finance", expanded=False):
        st.markdown("""
        <div style='background:rgba(31,119,180,0.08);border:1px solid rgba(31,119,180,0.2);
             border-radius:10px;padding:16px 18px;margin-bottom:12px;'>
          <div style='font-weight:700;color:#7eb8e8;margin-bottom:8px;'>
            How to export your Yahoo Finance portfolio:
          </div>
          <div style='color:#8aadcc;font-size:13px;line-height:1.8;'>
            1. Go to <strong>finance.yahoo.com</strong> → sign in → <strong>My Portfolio</strong><br>
            2. Open your portfolio and click the <strong>Download</strong> button (↓ icon, top right)<br>
            3. A <code>.csv</code> file will download — upload it below
          </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_csv = st.file_uploader(
            "Upload Yahoo Finance CSV", type=["csv"], key="yf_csv_upload",
            help="Download from Yahoo Finance → My Portfolio → Download (↓)"
        )

        if uploaded_csv:
            parsed = _parse_yf_csv(uploaded_csv)
            if parsed:
                needs_price = [h["ticker"] for h in parsed if h.get("_needs_price")]

                st.markdown(f"**{len(parsed)} holdings found:**")
                preview_rows = []
                for h in parsed:
                    preview_rows.append({
                        "Ticker":         h["ticker"],
                        "Quantity":       h["quantity"],
                        "Purchase Price": f"${h['purchase_price']:.2f}" if not h.get("_needs_price") else "⚠️ Not in CSV",
                        "Purchase Date":  h["purchase_date"],
                    })
                st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

                if needs_price:
                    st.warning(
                        f"⚠️ **{', '.join(needs_price)}**: purchase price not found in CSV. "
                        "These will be imported with price $0.00 — edit them manually after import."
                    )

                col_imp, col_rep = st.columns(2)
                if col_imp.button("➕ Add to existing holdings", type="primary", key="yf_add"):
                    existing_tickers = {h["ticker"] for h in portfolio}
                    added = 0
                    for h in parsed:
                        clean = {k: v for k, v in h.items() if not k.startswith("_")}
                        if clean["ticker"] not in existing_tickers:
                            portfolio.append(clean)
                            added += 1
                    st.session_state.portfolio = portfolio
                    _autosave()
                    st.success(f"Imported {added} new holdings (skipped {len(parsed)-added} duplicates).")
                    st.rerun()

                if col_rep.button("🔄 Replace all holdings", key="yf_replace"):
                    clean_parsed = [{k: v for k, v in h.items() if not k.startswith("_")} for h in parsed]
                    st.session_state.portfolio = clean_parsed
                    _autosave()
                    st.success(f"Replaced portfolio with {len(clean_parsed)} holdings from Yahoo Finance.")
                    st.rerun()

    st.divider()

    # ── Manual Add ────────────────────────────────────────────────────────────
    st.subheader("Add Position Manually")
    with st.form("add_holding", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        new_ticker = c1.text_input("Ticker", placeholder="AAPL")
        new_qty    = c2.number_input("Quantity", min_value=0.001, value=1.0, step=1.0)
        new_price  = c3.number_input("Purchase Price ($)", min_value=0.01, value=100.0, step=0.01)
        new_date   = c4.date_input("Purchase Date", value=date.today())
        add = st.form_submit_button("➕ Add Position", type="primary")
        if add and new_ticker:
            portfolio.append({
                "ticker":         new_ticker.strip().upper(),
                "quantity":       float(new_qty),
                "purchase_price": float(new_price),
                "purchase_date":  str(new_date),
            })
            st.session_state.portfolio = portfolio
            _autosave()
            st.success(f"Added {new_ticker.upper()} — {new_qty} shares @ ${new_price:.2f}")
            st.rerun()

    if portfolio:
        # Deduplicate warning
        tickers_seen = {}
        for i, h in enumerate(portfolio):
            t = h.get("ticker", "")
            tickers_seen.setdefault(t, []).append(i)
        dupes = {t: idxs for t, idxs in tickers_seen.items() if len(idxs) > 1}
        if dupes:
            st.warning(f"⚠️ Duplicate tickers: **{', '.join(dupes.keys())}**. Click below to keep only the first entry of each.")
            if st.button("🧹 Remove duplicates", key="dedup_btn"):
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
        st.caption("Click ✏️ on any row to correct the quantity, purchase price or date.")

        editing = st.session_state.get("_editing_holding")

        for i, h in enumerate(portfolio):
            ticker = h.get("ticker", "")
            qty    = h.get("quantity", 0)
            price  = h.get("purchase_price", 0.0)
            pdate  = h.get("purchase_date", "")

            if editing == i:
                # ── Inline edit form ──────────────────────────────────────────
                with st.form(key=f"edit_form_{i}"):
                    st.markdown(f"**Editing {ticker}**")
                    ec1, ec2, ec3, ec4 = st.columns(4)
                    e_qty   = ec1.number_input("Quantity",       min_value=0.001, value=float(qty),   step=1.0,  key=f"eq_{i}")
                    e_price = ec2.number_input("Purchase Price ($)", min_value=0.0,  value=float(price), step=0.01, key=f"ep_{i}")
                    e_date  = ec3.text_input("Purchase Date",    value=str(pdate), key=f"ed_{i}")
                    ec4.write("")
                    save_btn, cancel_btn = st.columns(2)
                    if save_btn.form_submit_button("💾 Save", type="primary", use_container_width=True):
                        portfolio[i]["quantity"]       = float(e_qty)
                        portfolio[i]["purchase_price"] = float(e_price)
                        portfolio[i]["purchase_date"]  = e_date.strip()
                        st.session_state.portfolio     = portfolio
                        st.session_state._editing_holding = None
                        _autosave()
                        st.rerun()
                    if cancel_btn.form_submit_button("✕ Cancel", use_container_width=True):
                        st.session_state._editing_holding = None
                        st.rerun()
            else:
                # ── Read row ──────────────────────────────────────────────────
                c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1])
                c1.write(f"**{ticker}**")
                c2.write(f"{qty} shares")
                c3.write(f"${price:.2f} / share")
                c4.write(pdate)
                if c5.button("✏️", key=f"edit_{i}", help="Edit this holding"):
                    st.session_state._editing_holding = i
                    st.rerun()
                if c6.button("🗑️", key=f"del_{i}", help="Remove"):
                    portfolio.pop(i)
                    st.session_state.portfolio = portfolio
                    _autosave()
                    st.rerun()
    else:
        st.info("No holdings yet. Add your first position above or import from Yahoo Finance.")

# ── Overview ───────────────────────────────────────────────────────────────────
with tab_ov:
    if not portfolio:
        st.markdown("""
        <div class='card' style='text-align:center;color:#888;padding:32px;'>
          No holdings yet. Go to <strong>Edit Holdings</strong> to add your positions.
        </div>""", unsafe_allow_html=True)
    else:
        with st.spinner("Fetching live prices…"):
            holdings = _refresh_prices(portfolio)

        stale = [h["ticker"] for h in holdings if not h.get("is_live")]
        if stale:
            st.warning(f"⚠️ Could not fetch live price for: {', '.join(stale)} — showing purchase price as fallback.")

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
            rows = []
            for h in holdings:
                live_tag = "🟢" if h.get("is_live") else "🔴"
                rows.append({
                    "Ticker":          h["ticker"],
                    "Qty":             h.get("quantity", 0),
                    "Purchase Price":  h.get("purchase_price", 0),
                    "Live Price":      h["current_price"],
                    "":                live_tag,
                    "Value":           h["current_value"],
                    "Gain $":          h["gain"],
                    "Gain %":          h["gain_pct"],
                    "Weight %":        round(h["current_value"] / total_val * 100, 1) if total_val else 0,
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True,
                column_config={
                    "Purchase Price": st.column_config.NumberColumn(format="$%.2f",  help="Price you paid per share"),
                    "Live Price":     st.column_config.NumberColumn(format="$%.2f",  help="Current market price  🟢=live  🔴=unavailable"),
                    "Value":          st.column_config.NumberColumn(format="$%.2f"),
                    "Gain $":         st.column_config.NumberColumn(format="$%+.2f"),
                    "Gain %":         st.column_config.NumberColumn(format="%.2f%%"),
                    "Weight %":       st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
                })
            st.caption("🟢 Live price  ·  🔴 Could not fetch — showing purchase price (gain = $0)")

# ── Rebalance ──────────────────────────────────────────────────────────────────
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
                    f"{h['ticker']}: {h.get('quantity',0)} shares @ ${h['current_price']:.2f} = ${h['current_value']:,.0f} ({h['current_value']/total*100:.1f}%)"
                    for h in holdings)
                profile = st.session_state.get("profile", {})
                prompt  = f"{ctx}\n\nProfile: Risk={profile.get('riesgo','moderate')}, Style={profile.get('estilo','mixed')}, Objective={profile.get('objetivo','growth')}\n\nProvide specific rebalancing recommendations: overweight/underweight positions, concentration risks, suggested target weights, and 2-3 tactical changes."
                with st.spinner("Generating advice…"):
                    resp = chat([{"role": "user", "content": prompt}])
                if resp:
                    st.markdown(resp)

# ── Risk Analytics ─────────────────────────────────────────────────────────────
with tab_risk:
    st.subheader("Risk Analytics")
    if not portfolio:
        st.info("Add holdings first.")
    else:
        holdings = _refresh_prices(portfolio)
        total    = sum(h["current_value"] for h in holdings)

        sectors = {}
        for h in holdings:
            try:
                info, _ = get_stock_data(h["ticker"], "5d")
                sec = (info or {}).get("sector", "Unknown")
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

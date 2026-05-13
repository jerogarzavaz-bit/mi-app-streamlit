import streamlit as st
import pandas as pd

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📚 Analysis History</div>
  <div class='page-subtitle'>Every analysis and screen is saved automatically</div>
</div>""", unsafe_allow_html=True)

analyses    = st.session_state.get("analyses", [])
screen_hist = st.session_state.get("screen_history", [])

tab_analyses, tab_screens, tab_compare = st.tabs(["Deep Analyses", "Screen History", "Compare"])

with tab_analyses:
    if not analyses:
        st.markdown("""
        <div class='card' style='text-align:center;color:#4a6a8a;padding:36px;'>
          <div style='font-size:32px;margin-bottom:10px;'>📊</div>
          <div style='font-size:15px;font-weight:600;color:#6a8aaa;margin-bottom:6px;'>No analyses yet</div>
          <div style='font-size:13px;'>Go to <strong style='color:#7eb8e8;'>Deep Analysis</strong> to run your first stock analysis</div>
        </div>""", unsafe_allow_html=True)
    else:
        # ── Controls ──────────────────────────────────────────────────────────
        cc1, cc2, cc3 = st.columns([3, 1, 1])
        search = cc1.text_input("🔍 Search ticker or company", "", label_visibility="collapsed",
                                 placeholder="Search ticker or company…")
        sort_by = cc2.selectbox("Sort", ["Newest", "Highest Score", "A–Z"], label_visibility="collapsed")
        if cc3.button("🗑️ Clear All", type="secondary"):
            st.session_state.analyses = []
            st.rerun()

        filtered = [a for a in analyses
                    if search.upper() in a["ticker"].upper()
                    or search.lower() in a.get("name","").lower()] if search else list(analyses)

        if sort_by == "Newest":
            filtered = list(reversed(filtered))
        elif sort_by == "Highest Score":
            filtered = sorted(filtered, key=lambda x: x.get("score", x.get("composite", 0)) or 0, reverse=True)
        else:
            filtered = sorted(filtered, key=lambda x: x["ticker"])

        st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>{len(filtered)} result{'s' if len(filtered)!=1 else ''}</div>", unsafe_allow_html=True)

        for a in filtered:
            score    = a.get("score", a.get("composite", 0)) or 0
            rec      = a.get("rec", "N/A")
            ticker   = a["ticker"]
            name     = a.get("name", "")
            date_str = a.get("date", "")
            info_d   = a.get("info", {})
            sector   = info_d.get("sector", "")
            industry = info_d.get("industry", "")
            px       = info_d.get("currentPrice", 0) or 0
            mc       = (info_d.get("marketCap", 0) or 0) / 1e9

            if score >= 6.5:
                tier_color = "#22c55e"
                tier_bg    = "rgba(34,197,94,0.08)"
                tier_label = "BUY"
            elif score >= 4.0:
                tier_color = "#f59e0b"
                tier_bg    = "rgba(245,158,11,0.08)"
                tier_label = "HOLD"
            else:
                tier_color = "#ef4444"
                tier_bg    = "rgba(239,68,68,0.08)"
                tier_label = "AVOID"

            bar_w = int(score / 10 * 100)

            with st.expander(f"**{ticker}** · {name or ticker}  ·  {date_str}  ·  {rec}", expanded=False):
                left, right = st.columns([3, 1])
                with left:
                    # Score bar
                    st.markdown(f"""
                    <div style='margin-bottom:14px;'>
                      <div style='display:flex;align-items:center;gap:12px;margin-bottom:6px;'>
                        <span style='font-size:28px;font-weight:800;color:{tier_color};'>{score:.1f}</span>
                        <span style='font-size:11px;color:#4a6a8a;'>/ 10</span>
                        <span style='
                          background:{tier_bg};
                          border:1px solid {tier_color}44;
                          color:{tier_color};
                          font-size:11px;font-weight:700;
                          padding:3px 10px;border-radius:20px;
                        '>{tier_label}</span>
                        <span style='color:#4a6a8a;font-size:12px;'>{rec}</span>
                      </div>
                      <div style='background:rgba(255,255,255,0.05);border-radius:6px;height:6px;overflow:hidden;'>
                        <div style='width:{bar_w}%;height:100%;background:linear-gradient(90deg,{tier_color}88,{tier_color});border-radius:6px;'></div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Metadata chips
                    chips = []
                    if sector:   chips.append(sector)
                    if industry: chips.append(industry)
                    if px:       chips.append(f"${px:.2f} at analysis")
                    if mc:       chips.append(f"${mc:.1f}B mkt cap")
                    if chips:
                        chip_html = "".join(f"<span style='background:rgba(126,184,232,0.1);border:1px solid rgba(126,184,232,0.2);color:#8aadcc;font-size:11px;padding:2px 9px;border-radius:12px;margin-right:6px;'>{c}</span>" for c in chips)
                        st.markdown(f"<div style='margin-bottom:12px;'>{chip_html}</div>", unsafe_allow_html=True)

                    text = a.get("text", "")
                    if text:
                        st.markdown(text[:2000] + ("…" if len(text) > 2000 else ""))

                with right:
                    if st.button("🔍 Re-analyze", key=f"re_{ticker}_{date_str}", use_container_width=True):
                        st.session_state.analyze_ticker = ticker
                        st.switch_page("pages/04_Analysis.py")
                    if st.button("📝 Memo", key=f"memo_{ticker}_{date_str}", use_container_width=True):
                        st.session_state.analyze_ticker = ticker
                        st.switch_page("pages/08_Memos.py")

with tab_screens:
    if not screen_hist:
        st.markdown("""
        <div class='card' style='text-align:center;color:#4a6a8a;padding:36px;'>
          <div style='font-size:26px;margin-bottom:8px;'>🔍</div>
          <div style='font-size:13px;'>No screens run yet — go to <strong style='color:#7eb8e8;'>Screener</strong> to start.</div>
        </div>""", unsafe_allow_html=True)
    else:
        for i, s in enumerate(reversed(screen_hist)):
            d      = s.get("date", "")
            count  = s.get("count", 0)
            tkrs   = s.get("tickers", [])
            st.markdown(f"""
            <div class='card' style='padding:14px 18px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:12px;'>
              <div>
                <span style='color:#c8d8f0;font-weight:700;font-size:14px;'>{d}</span>
                <span style='color:#4a6a8a;font-size:12px;margin-left:12px;'>{count} results · {len(tkrs)} tickers screened</span>
              </div>
              <span style='color:#4a6a8a;font-size:11px;'>{", ".join(tkrs[:5])}{"…" if len(tkrs)>5 else ""}</span>
            </div>""", unsafe_allow_html=True)

        if st.button("🗑️ Clear Screen History"):
            st.session_state.screen_history = []
            st.rerun()

with tab_compare:
    st.subheader("Compare Past Analyses")
    if len(analyses) < 2:
        st.info("Run at least 2 analyses to compare them here.")
    else:
        tickers_done = list({a["ticker"] for a in analyses})
        sel = st.multiselect("Select tickers to compare:", tickers_done, default=tickers_done[:4])
        if sel:
            rows = []
            for t in sel:
                latest = next((a for a in reversed(analyses) if a["ticker"] == t), None)
                if latest:
                    sc = latest.get("score", latest.get("composite", 0)) or 0
                    rows.append({
                        "Ticker":  t,
                        "Name":    latest.get("name", ""),
                        "Date":    latest["date"],
                        "Rec":     latest.get("rec", ""),
                        "Score":   sc,
                        "Sector":  latest.get("info", {}).get("sector", ""),
                    })
            df_cmp = pd.DataFrame(rows)
            st.dataframe(
                df_cmp,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Score": st.column_config.ProgressColumn(min_value=0, max_value=10, format="%.1f"),
                },
            )

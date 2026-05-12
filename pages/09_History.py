import streamlit as st
import pandas as pd

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📚 Analysis History</div>
  <div class='page-subtitle'>Every analysis and screen is saved automatically</div>
</div>""", unsafe_allow_html=True)

analyses      = st.session_state.get("analyses", [])
screen_hist   = st.session_state.get("screen_history", [])

tab_analyses, tab_screens, tab_compare = st.tabs(["Deep Analyses", "Screen History", "Compare"])

with tab_analyses:
    if not analyses:
        st.info("No analyses yet. Run your first analysis in the **Analysis** page.")
    else:
        # Search & filter
        search = st.text_input("🔍 Search ticker or company", "")
        filtered = [a for a in reversed(analyses)
                    if search.upper() in a["ticker"].upper()
                    or search.lower() in a.get("name","").lower()] if search else list(reversed(analyses))

        for a in filtered:
            with st.expander(f"**{a['ticker']}** — {a.get('name','')}  |  {a['date']}  |  {a.get('rec','')}  |  Score: {a.get('score','')}/10"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    text = a.get("text", "")
                    if text:
                        st.markdown(text[:1500] + ("…" if len(text) > 1500 else ""))
                with col2:
                    if st.button("Re-analyze", key=f"re_{a['ticker']}_{a['date']}"):
                        st.session_state.analyze_ticker = a["ticker"]
                        st.switch_page("pages/04_Analysis.py")
                    if st.button("Generate Memo", key=f"memo_{a['ticker']}_{a['date']}"):
                        st.switch_page("pages/08_Memos.py")

        if st.button("🗑️ Clear All Analyses", type="secondary"):
            st.session_state.analyses = []
            st.rerun()

with tab_screens:
    if not screen_hist:
        st.info("No screens run yet. Go to the **Screener** page.")
    else:
        df = pd.DataFrame(list(reversed(screen_hist)))
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("🗑️ Clear Screen History"):
            st.session_state.screen_history = []
            st.rerun()

with tab_compare:
    st.subheader("Compare Past Analyses")
    if len(analyses) < 2:
        st.info("Run at least 2 analyses to compare them here.")
    else:
        tickers_done = list({a["ticker"] for a in analyses})
        sel = st.multiselect("Select tickers to compare:", tickers_done, default=tickers_done[:3])
        if sel:
            rows = []
            for t in sel:
                latest = next((a for a in reversed(analyses) if a["ticker"] == t), None)
                if latest:
                    rows.append({
                        "Ticker": t, "Name": latest.get("name",""), "Date": latest["date"],
                        "Rec": latest.get("rec",""), "Score": latest.get("score",""),
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

import streamlit as st
from utils.ai import has_key, no_key_banner, generate_memo
from utils.data import get_stock_data

st.markdown("""
<div class='page-header'>
  <div class='page-title'>📝 Investment Memo Generator</div>
  <div class='page-subtitle'>Generate professional-grade investment memos from your past analyses</div>
</div>""", unsafe_allow_html=True)

analyses = st.session_state.get("analyses", [])

tab_hist, tab_new = st.tabs(["Generate from Past Analysis", "New Memo"])

with tab_hist:
    if not analyses:
        st.markdown("""
        <div class='card' style='text-align:center;color:#888;padding:36px;'>
          No analyses found. Go to <strong>Analysis</strong> to run your first analysis,
          then come back to generate a memo.
        </div>""", unsafe_allow_html=True)
        if st.button("Go to Analysis"):
            st.switch_page("pages/04_Analysis.py")
    else:
        if not has_key():
            no_key_banner("memo generation")
        else:
            sel = st.selectbox("Select analysis:",
                [f"{a['ticker']} — {a['date']} ({a.get('rec','')})" for a in reversed(analyses)])
            idx = len(analyses) - 1 - [f"{a['ticker']} — {a['date']} ({a.get('rec','')})"
                                        for a in reversed(analyses)].index(sel)
            analysis = analyses[idx]

            st.markdown(f"""
            <div class='card'>
              <strong>{analysis['ticker']}</strong> — {analysis.get('name','')}
              &nbsp;|&nbsp; {analysis['date']} &nbsp;|&nbsp;
              <span class='tier1'>{analysis.get('rec','')}</span>
              &nbsp;| Score: {analysis.get('score','')}/10
            </div>""", unsafe_allow_html=True)

            if st.button("📄 Generate Investment Memo", type="primary"):
                info, _ = get_stock_data(analysis["ticker"], "5d")
                with st.spinner("Generating memo…"):
                    memo = generate_memo(analysis["text"], analysis["ticker"], info or {})
                if memo:
                    st.markdown("---")
                    st.markdown(memo)
                    st.download_button("⬇️ Download Memo (.txt)", memo,
                                       file_name=f"memo_{analysis['ticker']}_{analysis['date']}.txt")

with tab_new:
    st.subheader("Generate memo for any ticker")
    if not has_key():
        no_key_banner("memo generation")
    else:
        ticker = st.text_input("Ticker", placeholder="NVDA")
        if ticker and st.button("Generate Memo", type="primary"):
            info, _ = get_stock_data(ticker.upper(), "1y")
            if info is None:
                st.error("Could not fetch data.")
            else:
                with st.spinner("Analyzing and writing memo…"):
                    from utils.ai import analyze_stock
                    full = ""
                    for c in analyze_stock(ticker.upper()):
                        full += c
                    memo = generate_memo(full, ticker.upper(), info)
                if memo:
                    st.markdown(memo)
                    st.download_button("⬇️ Download Memo", memo,
                                       file_name=f"memo_{ticker.upper()}.txt")

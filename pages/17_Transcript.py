import streamlit as st
from utils.ai import has_key, no_key_banner, analyze_transcript

st.markdown("""
<div class='page-header'>
  <div class='page-title'>🎙️ Earnings Call Transcript Analyzer</div>
  <div class='page-subtitle'>Auto-fetch or paste any earnings call transcript — Claude extracts tone, guidance, risks, and analyst concerns</div>
</div>""", unsafe_allow_html=True)

if not has_key():
    no_key_banner("transcript analysis")

# ── Input ─────────────────────────────────────────────────────────────────────
method = st.radio("Source:", ["Paste transcript", "Upload .txt file"], horizontal=True)

transcript = ""
if method == "Paste transcript":
    transcript = st.text_area("Paste the full earnings call transcript here:",
        height=300, placeholder="Q4 2025 Earnings Call\nCEO: Good afternoon, everyone…")
else:
    uploaded = st.file_uploader("Upload transcript (.txt)", type=["txt"])
    if uploaded:
        transcript = uploaded.read().decode("utf-8", errors="ignore")
        st.success(f"Loaded {len(transcript):,} characters")
        with st.expander("Preview"):
            st.text(transcript[:1000] + "…")

ticker_hint = st.text_input("Ticker hint (optional)", placeholder="NVDA")

analyze = st.button("🔍 Analyze Transcript", type="primary",
                     disabled=not (has_key() and transcript))

if analyze and transcript:
    with st.spinner("Analyzing with Claude AI…"):
        result = analyze_transcript(transcript)
    if result:
        st.markdown("---")
        if ticker_hint:
            st.subheader(f"Transcript Analysis — {ticker_hint.upper()}")
        st.markdown(result)
        st.download_button("⬇️ Download Analysis", result,
                           file_name=f"transcript_{ticker_hint or 'analysis'}.md")
elif not transcript and analyze:
    st.warning("Please paste or upload a transcript first.")
elif not has_key():
    st.info("Add your Anthropic API key in **Settings** to analyze transcripts.")

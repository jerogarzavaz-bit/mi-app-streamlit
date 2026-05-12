import streamlit as st
from utils.ai import has_key, no_key_banner, chat

st.markdown("""
<div class='page-header'>
  <div class='page-title'>🤖 AI Chat Assistant</div>
  <div class='page-subtitle'>Ask anything about your portfolio, watchlists, market conditions, or any stock</div>
</div>""", unsafe_allow_html=True)

if not has_key():
    no_key_banner("AI Chat")

# ── Platform Context ───────────────────────────────────────────────────────────
portfolio  = st.session_state.get("portfolio", [])
watchlists = st.session_state.get("watchlists", {})
analyses   = st.session_state.get("analyses", [])
profile    = st.session_state.get("profile", {})

def _build_ctx():
    lines = []
    if profile:
        lines.append(f"INVESTOR PROFILE: Risk={profile.get('riesgo','N/A')} | Style={profile.get('estilo','N/A')} | Objective={profile.get('objetivo','N/A')}")
    if portfolio:
        lines.append(f"PORTFOLIO ({len(portfolio)} positions):")
        total = sum(h.get("current_value", h.get("purchase_price",0)*h.get("quantity",0)) for h in portfolio)
        for h in portfolio:
            val = h.get("current_value", h.get("purchase_price",0)*h.get("quantity",0))
            lines.append(f"  {h['ticker']}: {h['quantity']} shares | ${val:,.0f} ({val/total*100:.1f}%)" if total else f"  {h['ticker']}: {h['quantity']} shares")
    else:
        lines.append("PORTFOLIO: No positions yet.")
    if watchlists:
        for wl_name, wl_tickers in watchlists.items():
            lines.append(f"WATCHLIST '{wl_name}': {', '.join(wl_tickers[:10])}")
    if analyses:
        recent = analyses[-3:]
        lines.append("RECENT ANALYSES: " + ", ".join(f"{a['ticker']}({a.get('rec','')})" for a in recent))
    return "\n".join(lines)

with st.expander("Platform context loaded"):
    st.text(_build_ctx() or "No portfolio or watchlist data yet.")

# ── Suggested Questions ────────────────────────────────────────────────────────
suggestions = [
    "How is my portfolio positioned in the current macro environment?",
    "Which of my holdings has the most risk right now?",
    "Give me 3 ideas from my watchlist that deserve a closer look this week.",
    "What's the biggest concentration risk in my portfolio?",
    "Explain my portfolio's exposure to rising interest rates.",
    "Which sectors am I over- and under-weight in?",
]

messages = st.session_state.get("chat_messages", [])

if not messages:
    st.subheader("Suggested Questions")
    cols = st.columns(2)
    for i, q in enumerate(suggestions):
        if cols[i % 2].button(q, key=f"sugg_{i}", use_container_width=True):
            messages.append({"role": "user", "content": q})
            st.session_state.chat_messages = messages
            st.rerun()

# ── Chat History ───────────────────────────────────────────────────────────────
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask about your portfolio, any stock, market conditions…",
                        disabled=not has_key())

if prompt:
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            resp = chat(messages, platform_ctx=_build_ctx())
        if resp:
            st.markdown(resp)
            messages.append({"role": "assistant", "content": resp})
        else:
            st.error("Error generating response.")

    st.session_state.chat_messages = messages

# ── Controls ──────────────────────────────────────────────────────────────────
if messages:
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.chat_messages = []
        st.rerun()

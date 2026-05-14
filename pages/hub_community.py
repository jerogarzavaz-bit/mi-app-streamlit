import re
import streamlit as st
from utils.db import post_community_message, get_community_messages, delete_community_message, is_configured
from utils.auth import is_admin, get_user_display_name

st.markdown("""
<div class='page-header'>
  <div class='page-title'>💬 Community</div>
  <div class='page-subtitle'>Chat · Tickers · Ideas · Links</div>
</div>""", unsafe_allow_html=True)

username     = st.session_state.get("username", "")
display_name = get_user_display_name()

if not username:
    st.warning("You must be logged in to use the community chat.")
    st.stop()

if not is_configured():
    st.error("Cloud sync is not configured — community chat requires Firestore.")
    st.stop()

# ── Helpers ────────────────────────────────────────────────────────────────────

_TICKER_RE = re.compile(r'\$([A-Z]{1,5})')
_URL_RE    = re.compile(r'(https?://[^\s]+)')

def _extract_tickers(text: str) -> list:
    return list(dict.fromkeys(_TICKER_RE.findall(text.upper())))

def _render_text(text: str) -> str:
    """Linkify URLs and highlight $TICKER mentions."""
    text = re.sub(_URL_RE, r'<a href="\1" target="_blank" style="color:#7eb8e8;">\1</a>', text)
    text = re.sub(_TICKER_RE, r'<span style="background:rgba(97,114,243,0.18);color:#a5b4fc;font-weight:700;padding:1px 5px;border-radius:4px;">$\1</span>', text)
    return text

def _ts(msg: dict) -> str:
    ts = msg.get("timestamp")
    if ts is None:
        return ""
    try:
        import datetime
        if hasattr(ts, "seconds"):                      # Firestore Timestamp
            dt = datetime.datetime.fromtimestamp(ts.seconds)
        elif hasattr(ts, "isoformat"):
            dt = ts
        else:
            return ""
        return dt.strftime("%b %d · %H:%M")
    except Exception:
        return ""

# ── Layout ─────────────────────────────────────────────────────────────────────

col_main, col_side = st.columns([3, 1])

with col_side:
    st.markdown("""
    <div class='card' style='padding:14px 16px;'>
      <div style='font-weight:700;color:#c8d8f0;margin-bottom:10px;font-size:13px;'>How to use</div>
      <div style='font-size:12px;color:#8aadcc;line-height:1.8;'>
        💬 Share ideas, market takes, and analysis<br>
        <span style='color:#a5b4fc;font-weight:700;'>$AAPL</span> — mention any ticker<br>
        🔗 Paste links — auto-detected<br>
        🗑️ Hover a message to delete yours
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button("🔄 Refresh", use_container_width=True, key="comm_refresh"):
        st.session_state.pop("_comm_msgs", None)
        st.rerun()

    # Trending tickers from recent messages
    all_msgs_side = st.session_state.get("_comm_msgs", [])
    all_tickers_mentioned = []
    for m in all_msgs_side[-50:]:
        all_tickers_mentioned.extend(m.get("tickers", []))
    if all_tickers_mentioned:
        from collections import Counter
        top = Counter(all_tickers_mentioned).most_common(8)
        st.markdown("""
        <div class='card' style='padding:14px 16px;margin-top:0;'>
          <div style='font-weight:700;color:#c8d8f0;margin-bottom:10px;font-size:13px;'>🔥 Trending</div>""",
        unsafe_allow_html=True)
        for ticker, count in top:
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;margin-bottom:6px;'>
              <span style='color:#a5b4fc;font-weight:700;font-size:13px;'>${ticker}</span>
              <span style='color:#4a6a8a;font-size:11px;'>{count} mention{"s" if count>1 else ""}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

with col_main:
    # ── Message input ──────────────────────────────────────────────────────────
    with st.form("comm_send_form", clear_on_submit=True):
        msg_text = st.text_area(
            f"Post as **{display_name}**",
            height=80,
            placeholder="Share an idea, mention $AAPL, or paste a link…",
            key="comm_input",
            label_visibility="visible",
        )
        c1, c2 = st.columns([4, 1])
        submitted = c2.form_submit_button("Send →", type="primary", use_container_width=True)

        if submitted:
            if not msg_text.strip():
                st.warning("Message can't be empty.")
            elif len(msg_text) > 1000:
                st.error("Max 1000 characters.")
            else:
                tickers = _extract_tickers(msg_text)
                ok = post_community_message(username, display_name, msg_text.strip(), tickers)
                if ok:
                    st.session_state.pop("_comm_msgs", None)  # bust cache
                    st.rerun()
                else:
                    st.error("Failed to send. Check Firestore connection.")

    st.divider()

    # ── Load and display messages ──────────────────────────────────────────────
    if "_comm_msgs" not in st.session_state:
        with st.spinner("Loading messages…"):
            st.session_state["_comm_msgs"] = get_community_messages(100)

    msgs = st.session_state.get("_comm_msgs", [])

    if not msgs:
        st.markdown("""
        <div class='card' style='text-align:center;color:#4a6a8a;padding:48px;'>
          <div style='font-size:40px;margin-bottom:12px;'>💬</div>
          <div style='font-size:15px;font-weight:600;color:#6a8aaa;margin-bottom:8px;'>No messages yet</div>
          <div style='font-size:13px;'>Be the first to share a market take or idea!</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='color:#4a6a8a;font-size:12px;margin-bottom:12px;'>{len(msgs)} messages — newest at bottom</div>",
                    unsafe_allow_html=True)

        for msg in msgs:
            is_own    = msg.get("username") == username
            is_admin_ = is_admin()
            name      = msg.get("display_name") or msg.get("username", "?")
            ts_str    = _ts(msg)
            tickers   = msg.get("tickers", [])
            doc_id    = msg.get("id", "")
            text_raw  = msg.get("text", "")
            text_html = _render_text(text_raw)

            avatar_color = "#6172F3" if is_own else "#4a6a8a"
            bg_color = "rgba(97,114,243,0.06)" if is_own else "rgba(255,255,255,0.02)"
            border = "rgba(97,114,243,0.25)" if is_own else "rgba(255,255,255,0.06)"
            align  = "flex-end" if is_own else "flex-start"
            own_label = " <span style='font-size:10px;color:#6172F3;'>(you)</span>" if is_own else ""

            ticker_chips = ""
            for t in tickers:
                ticker_chips += f'<a href="#" style="background:rgba(97,114,243,0.15);color:#a5b4fc;font-size:10px;font-weight:700;padding:2px 7px;border-radius:10px;margin-right:4px;text-decoration:none;">${t}</a>'

            msg_col, del_col = st.columns([20, 1])
            with msg_col:
                st.markdown(f"""
                <div style='display:flex;justify-content:{align};margin-bottom:10px;'>
                  <div style='max-width:88%;background:{bg_color};border:1px solid {border};border-radius:14px;padding:12px 16px;'>
                    <div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'>
                      <span style='width:28px;height:28px;border-radius:50%;background:{avatar_color};display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;flex-shrink:0;'>{name[0].upper()}</span>
                      <span style='font-weight:700;color:#c8d8f0;font-size:13px;'>{name}{own_label}</span>
                      <span style='color:#3a5a7a;font-size:11px;'>{ts_str}</span>
                    </div>
                    <div style='color:#d0d8e8;font-size:13px;line-height:1.6;word-break:break-word;'>{text_html}</div>
                    {f'<div style="margin-top:8px;">{ticker_chips}</div>' if ticker_chips else ""}
                  </div>
                </div>""", unsafe_allow_html=True)

            with del_col:
                if (is_own or is_admin_) and doc_id:
                    if st.button("🗑️", key=f"del_msg_{doc_id}", help="Delete message"):
                        ok = delete_community_message(doc_id, username)
                        if ok:
                            st.session_state.pop("_comm_msgs", None)
                            st.rerun()

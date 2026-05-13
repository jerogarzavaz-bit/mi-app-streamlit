import streamlit as st
import json
from utils.auth import is_admin, is_guest, hash_password
from utils.db import save_user_data, load_user_data, is_configured, get_connection_error

if is_guest():
    st.error("Settings are not available for guest accounts.")
    st.stop()

username = st.session_state.get("username", "")

def _autosave():
    ok = is_configured() and save_user_data(username)
    # Store result so it survives the st.rerun() that follows
    st.session_state["_last_save_ok"] = ok

st.markdown("""
<div class='page-header'>
  <div class='page-title'>⚙️ Settings</div>
  <div class='page-subtitle'>Configure your preferences</div>
</div>""", unsafe_allow_html=True)

# ── Show any lingering save errors from the previous run ──────────────────────
if st.session_state.pop("_last_save_ok", None) is False:
    err = st.session_state.pop("_db_save_error", "unknown error")
    st.error(f"☁️ Cloud save failed: {err}")
elif st.session_state.pop("_last_save_ok", None) is True:
    pass  # success — no banner needed, the button label is enough

# ── Firebase status banner ────────────────────────────────────────────────────
if is_configured():
    st.success("☁️ **Cloud Sync: Active** — your data is saved automatically.", icon="✅")
else:
    conn_err = get_connection_error()
    if conn_err:
        st.error(f"☁️ **Cloud Sync: Connection failed** — data will NOT persist across reloads.\n\n`{conn_err}`")
    else:
        st.warning("☁️ **Cloud Sync: Not configured** — data will NOT persist across reloads.")

api_keys = st.session_state.get("api_keys", {"anthropic":"","alpha_vantage":"","fred":"","fmp":""})

# ── API Keys ──────────────────────────────────────────────────────────────────
st.subheader("🔑 API Keys")
st.write("Each user configures their own keys. Your keys are private and only used for your account.")

def _key_status(val, label_ok, label_missing, color_ok="#2ca02c", color_miss="#FFA500"):
    if val:
        return f"<span style='background:{color_ok};color:white;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;'>{label_ok}</span>"
    return f"<span style='background:{color_miss};color:white;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;'>{label_missing}</span>"

# Anthropic
with st.container():
    c1, c2 = st.columns([3, 1])
    st.markdown(f"**Anthropic API Key** &nbsp; {_key_status(api_keys.get('anthropic'), '✓ Active — AI enabled', 'Not set — AI features disabled')}", unsafe_allow_html=True)
    st.caption("Required for AI analysis, memos, chat, recommendations. Get yours at console.anthropic.com")
    col_key, col_btn = st.columns([4, 1])
    new_anthropic = col_key.text_input("Anthropic key", type="password",
        value=api_keys.get("anthropic",""), label_visibility="collapsed",
        placeholder="sk-ant-api03-…")
    if col_btn.button("Save", key="save_anthropic"):
        api_keys["anthropic"] = new_anthropic.strip()
        st.session_state.api_keys = api_keys
        _autosave()
        st.success("Anthropic key saved!" if new_anthropic else "Key cleared.")
        st.rerun()

st.divider()

# Alpha Vantage
with st.container():
    st.markdown(f"**Alpha Vantage Key** (free) &nbsp; {_key_status(api_keys.get('alpha_vantage'), '✓ Set', 'Not set — using free sources', '#1f77b4', '#4da6ff')}", unsafe_allow_html=True)
    st.caption("Optional — better sentiment data. alphavantage.co")
    col_key, col_btn = st.columns([4, 1])
    new_av = col_key.text_input("AV key", type="password",
        value=api_keys.get("alpha_vantage",""), label_visibility="collapsed",
        placeholder="ABCDEFGHIJ…")
    if col_btn.button("Save", key="save_av"):
        api_keys["alpha_vantage"] = new_av.strip()
        st.session_state.api_keys = api_keys
        _autosave()
        st.success("Alpha Vantage key saved!")

st.divider()

# FRED
with st.container():
    st.markdown(f"**FRED API Key** (free) &nbsp; {_key_status(api_keys.get('fred'), '✓ Set', 'Not set — macro charts unavailable', '#1f77b4', '#4da6ff')}", unsafe_allow_html=True)
    st.caption("Optional — macro history charts. fred.stlouisfed.org")
    col_key, col_btn = st.columns([4, 1])
    new_fred = col_key.text_input("FRED key", type="password",
        value=api_keys.get("fred",""), label_visibility="collapsed",
        placeholder="abcdef1234…")
    if col_btn.button("Save", key="save_fred"):
        api_keys["fred"] = new_fred.strip()
        st.session_state.api_keys = api_keys
        _autosave()
        st.success("FRED key saved!")

st.divider()

# FMP
st.subheader("📊 Financial Modeling Prep (FMP)")
st.write("FMP provides institutional-grade financial data. When enabled, it replaces yfinance for fundamentals, price history, earnings, and analyst estimates.")
st.markdown(f"**FMP Key** &nbsp; {_key_status(api_keys.get('fmp'), '✓ Set', 'Not set — FMP features unavailable', '#1f77b4', '#4da6ff')}", unsafe_allow_html=True)
col_key, col_btn = st.columns([4, 1])
new_fmp = col_key.text_input("FMP key", type="password",
    value=api_keys.get("fmp",""), label_visibility="collapsed",
    placeholder="your_fmp_api_key_here")
if col_btn.button("Save", key="save_fmp"):
    api_keys["fmp"] = new_fmp.strip()
    st.session_state.api_keys = api_keys
    _autosave()
    st.success("FMP key saved!")

provider = st.radio("Data Provider", ["yfinance (default, free)", "Financial Modeling Prep (FMP)"],
    index=0 if st.session_state.get("data_provider","yfinance") == "yfinance" else 1)
if st.button("Save provider"):
    st.session_state.data_provider = "yfinance" if "yfinance" in provider else "fmp"
    _autosave()
    st.success(f"Provider set to: {'yfinance' if 'yfinance' in provider else 'FMP'}")
st.info(f"**{st.session_state.get('data_provider','yfinance')}** is active as the primary data source.")

st.divider()

# ── Morning Brief ─────────────────────────────────────────────────────────────
st.subheader("☀️ Morning Brief")
st.write("Configure your personalized AI market briefing delivered by email before the open.")
from utils.morning_brief import is_email_configured
if is_email_configured():
    cfg_e = st.session_state.get("api_keys", {})
    st.success(f"✅ Email configured → {cfg_e.get('brief_email','')}  ·  Send time: {cfg_e.get('brief_send_time','07:00')}  ·  Auto-send: {'ON' if cfg_e.get('brief_enabled') else 'OFF'}")
else:
    st.warning("Morning Brief email not configured. Go to **Morning Brief → Schedule & Email** to set it up.")
if st.button("⚙️ Go to Morning Brief Settings"):
    st.switch_page("pages/21_Morning_Brief.py")
st.divider()

# ── Features Roadmap ───────────────────────────────────────────────────────────
st.subheader("🚀 Features Roadmap")
from utils.ai import has_key
has_ai = has_key()
status = "✅" if has_ai else "🔴"
status_label = "ACTIVE" if has_ai else "REQUIRES ANTHROPIC API KEY"

st.markdown(f"""
<div class='card' style='border-color:{"#2ca02c" if has_ai else "#d62728"};'>
  <div style='font-weight:700;color:{"#2ca02c" if has_ai else "#d62728"};margin-bottom:12px;'>
    {status} {status_label} — AI PIPELINE — MODEL: CLAUDE SONNET 4.6
  </div>""" + "\n".join(f"<div style='color:{'#ccc' if has_ai else '#555'};margin:4px 0;'>{'✅' if has_ai else '✗'} {feat}</div>"
  for feat in [
    "Deep Stock Analysis — 6-dimension scoring + Claude AI narrative (~$0.04/run)",
    "AI Chat — Portfolio advisor with full context (~$0.01/message)",
    "Daily Market Brief — Live data + Claude synthesis (~$0.05/run)",
    "Investment Memos — Professional PDF-quality memos (~$0.03/run)",
    "Recommendations — Daily AI-curated picks from your watchlist (~$0.04/run)",
    "Transcript Analyzer — Earnings call tone & guidance extraction (~$0.05/run)",
  ]) + "</div>", unsafe_allow_html=True)

st.divider()

# ── Cloud Sync ────────────────────────────────────────────────────────────────
st.subheader("☁️ Cloud Sync")
username = st.session_state.get("username", "")

if not is_configured():
    st.warning("Firebase not configured. See the setup guide below to enable cloud persistence.")
else:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save my data to cloud", type="primary", use_container_width=True):
            if save_user_data(username):
                st.success("Data saved to cloud!")
            else:
                st.error("Save failed.")
    with c2:
        if st.button("🔄 Load my data from cloud", use_container_width=True):
            if load_user_data(username):
                st.success("Data loaded!")
                st.rerun()
            else:
                st.info("No saved data found in cloud.")

st.divider()

# ── User Management (admin only) ──────────────────────────────────────────────
if is_admin():
    st.subheader("👥 User Management")
    st.info("Add new users by updating your Streamlit Cloud secrets. Use the tool below to generate the password hash.")

    with st.expander("🔐 Generate Password Hash"):
        st.write("Enter a plain password to get the bcrypt hash to put in your secrets.")
        new_pass = st.text_input("New password", type="password", key="gen_pass")
        if new_pass and st.button("Generate Hash"):
            hashed = hash_password(new_pass)
            st.code(hashed, language=None)
            st.caption("Copy this hash — you'll need it in the secrets TOML below.")

    with st.expander("📋 How to add a new user"):
        st.markdown("""
**1.** Generate the password hash above.

**2.** Go to your app in [Streamlit Cloud](https://share.streamlit.io) → **Settings** → **Secrets**.

**3.** Add this block for each new user (replace values):

```toml
[credentials.usernames.NEW_USERNAME]
name     = "Display Name"
email    = "user@email.com"
password = "$2b$12$PASTE_THE_HASH_HERE"
role     = "user"
```

For admin users, set `role = "admin"`.

**4.** Click **Save** — the app reloads automatically with the new user.
        """)

    with st.expander("📋 Full secrets.toml template"):
        st.code("""
# ── Authentication ────────────────────────
[credentials.usernames.admin]
name     = "Admin"
email    = "admin@yourapp.com"
password = "$2b$12$HASH_OF_YOUR_PASSWORD"
role     = "admin"

[credentials.usernames.jero]
name     = "Jero"
email    = "jero@email.com"
password = "$2b$12$HASH_OF_JERO_PASSWORD"
role     = "user"

[cookie]
name        = "sap_cookie"
key         = "replace_with_a_long_random_string_123456"
expiry_days = 30

# ── Firebase ──────────────────────────────
[firebase]
type                        = "service_account"
project_id                  = "your-project-id"
private_key_id              = "abc123..."
private_key                 = "-----BEGIN PRIVATE KEY-----\\nYOUR_KEY\\n-----END PRIVATE KEY-----\\n"
client_email                = "firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com"
client_id                   = "123456789"
auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
token_uri                   = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url        = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain             = "googleapis.com"
        """, language="toml")

    st.divider()

# ── Cache ─────────────────────────────────────────────────────────────────────
st.subheader("🗂️ Cache Management")
st.write("Clear cached market data if charts look stale or prices are not updating.")
if st.button("🔄 Clear Price & Chart Cache"):
    st.cache_data.clear()
    st.success("Cache cleared — data will reload on next request.")

st.divider()

# ── Data Backup ───────────────────────────────────────────────────────────────
st.subheader("💾 My Data Backup")
st.write("Download a backup of your portfolio and analysis history.")

col1, col2 = st.columns(2)
with col1:
    incl_keys = st.checkbox("Include my API keys in backup")
    backup_data = {
        "portfolio":      st.session_state.get("portfolio", []),
        "watchlists":     st.session_state.get("watchlists", {}),
        "analyses":       [{k: v for k, v in a.items() if k != "text"} for a in st.session_state.get("analyses", [])],
        "profile":        st.session_state.get("profile", {}),
        "alerts":         st.session_state.get("alerts", []),
        "screen_history": st.session_state.get("screen_history", []),
    }
    if incl_keys:
        backup_data["api_keys"] = api_keys
    st.download_button("⬇️ Download My Backup",
        json.dumps(backup_data, indent=2, default=str),
        file_name="stock_analyzer_backup.json",
        mime="application/json")

with col2:
    uploaded = st.file_uploader("Restore backup (.json)", type=["json"])
    if uploaded and st.button("🔄 Restore Data"):
        try:
            data = json.loads(uploaded.read())
            for key in ("portfolio","watchlists","analyses","profile","alerts","screen_history"):
                if key in data:
                    st.session_state[key] = data[key]
            if "api_keys" in data:
                st.session_state.api_keys = data["api_keys"]
            st.success("Data restored successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Could not restore backup: {e}")

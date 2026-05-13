import streamlit as st
import streamlit_authenticator as stauth


# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    import bcrypt
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(12)).decode()


def _secrets_credentials() -> dict | None:
    """Load credentials from st.secrets (fallback when Firestore is unavailable)."""
    try:
        raw = st.secrets["credentials"]
        def _to_dict(obj):
            if hasattr(obj, "items"):
                return {k: _to_dict(v) for k, v in obj.items()}
            return obj
        return _to_dict(raw)
    except Exception:
        return None


def _get_credentials() -> dict:
    """
    Credential priority:
      1. Firestore app_config/credentials  (always in sync, works on all devices)
      2. st.secrets["credentials"]         (local secrets.toml / Streamlit Cloud)
      3. Hardcoded demo fallback            (so the app never crashes)
    On first load with Firestore available, seeds Firestore from secrets if empty.
    """
    from utils.db import get_auth_credentials, seed_auth_credentials

    # Try Firestore
    fs_creds = get_auth_credentials()
    if fs_creds and fs_creds.get("usernames"):
        return fs_creds

    # Firestore empty or unavailable — try secrets
    sec_creds = _secrets_credentials()
    if sec_creds and sec_creds.get("usernames"):
        # Seed Firestore so future logins use it (only writes if doc missing)
        seed_auth_credentials(sec_creds)
        return sec_creds

    # Last-resort demo account
    return {
        "usernames": {
            "admin": {
                "name": "Admin",
                "email": "admin@thebullmonkey.com",
                "password": hash_password("Admin12345"),
                "role": "admin",
            }
        }
    }


def get_authenticator() -> stauth.Authenticate:
    creds = _get_credentials()
    try:
        cookie = st.secrets["cookie"]
        c_name   = cookie["name"]
        c_key    = cookie["key"]
        c_expiry = int(cookie.get("expiry_days", 30))
    except Exception:
        c_name, c_key, c_expiry = "bullmonkey_cookie", "bullmonkey_secret_key_change_me_2025", 30

    return stauth.Authenticate(creds, c_name, c_key, cookie_expiry_days=c_expiry, auto_hash=False)


def get_role() -> str:
    username = st.session_state.get("username", "")
    try:
        creds = _get_credentials()
        return creds.get("usernames", {}).get(username, {}).get("role", "user")
    except Exception:
        return "user"


def is_admin() -> bool:
    return get_role() == "admin"


def is_guest() -> bool:
    return get_role() == "guest"


def get_user_display_name() -> str:
    return st.session_state.get("name", st.session_state.get("username", "User"))

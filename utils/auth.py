import streamlit as st
import streamlit_authenticator as stauth


# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    import bcrypt
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _get_credentials() -> dict:
    """Load credentials from st.secrets (set in Streamlit Cloud dashboard)."""
    try:
        raw = st.secrets["credentials"]
        # Convert from AttrDict to plain dict recursively
        def _to_dict(obj):
            if hasattr(obj, "items"):
                return {k: _to_dict(v) for k, v in obj.items()}
            return obj
        return _to_dict(raw)
    except Exception:
        # Fallback: demo account so the app doesn't crash before secrets are set
        demo_hash = hash_password("demo1234")
        return {
            "usernames": {
                "admin": {
                    "name": "Admin",
                    "email": "admin@stockanalyzer.com",
                    "password": demo_hash,
                    "role": "admin",
                }
            }
        }


def get_authenticator() -> stauth.Authenticate:
    creds = _get_credentials()
    try:
        cookie = st.secrets["cookie"]
        c_name    = cookie["name"]
        c_key     = cookie["key"]
        c_expiry  = int(cookie.get("expiry_days", 30))
    except Exception:
        c_name, c_key, c_expiry = "sap_cookie", "change_this_secret_key_123!", 30

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

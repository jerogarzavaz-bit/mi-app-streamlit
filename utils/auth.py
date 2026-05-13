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
      1. Firestore app_config/credentials  (source of truth — all devices in sync)
      2. Hardcoded hashes                  (bootstrap fallback, seeds Firestore)
    secrets.toml credentials are intentionally skipped to avoid stale hashes.
    """
    from utils.db import get_auth_credentials, seed_auth_credentials

    # Try Firestore
    fs_creds = get_auth_credentials()
    if fs_creds and fs_creds.get("usernames"):
        return fs_creds

    # Last-resort fallback — hardcoded hashes (safe: bcrypt can't be reversed)
    # admin → Admin12345 | guest01-10 → Bull01Guest … Bull10Guest
    fallback = {
        "usernames": {
            "admin":   {"name": "Admin",    "email": "admin@thebullmonkey.com",   "password": "$2b$12$btb10qFHBD2bRIyKhkZ4SuVB7H8Lpmaly.z6Ojk5icbsGYFhiWwyO", "role": "admin"},
            "guest01": {"name": "Guest 01", "email": "guest01@thebullmonkey.com", "password": "$2b$12$ezybItuhJfYaWBLm4JBbmOSO2Pis142OwASHqy8Ba4OZI2xFRb1.u", "role": "guest"},
            "guest02": {"name": "Guest 02", "email": "guest02@thebullmonkey.com", "password": "$2b$12$1Kj.eHijxmsZe6mDlHb4pOK0b4uqZiF3/xDa.p72YvdEE6qn4VlyO", "role": "guest"},
            "guest03": {"name": "Guest 03", "email": "guest03@thebullmonkey.com", "password": "$2b$12$loPehOwKfINVpq.rhfQYFePHYz/vXDqpfgYiD0lptuhZgkdK/G0I6", "role": "guest"},
            "guest04": {"name": "Guest 04", "email": "guest04@thebullmonkey.com", "password": "$2b$12$FAPU8NlTGIxf0CxIq4ZHwuEXl8S1uCVapHXmgxaVXEJm.0jnLfrG2", "role": "guest"},
            "guest05": {"name": "Guest 05", "email": "guest05@thebullmonkey.com", "password": "$2b$12$UVU14yBp60BMz7uExg17GukF.S4EDRS.OhefBFneXpE9KVO7ACKzu",  "role": "guest"},
            "guest06": {"name": "Guest 06", "email": "guest06@thebullmonkey.com", "password": "$2b$12$fJDkDOYpqinmOlGPFJ5d4u5lJYYjb5EF6CLlJRe1fpd9xxG0fq28G", "role": "guest"},
            "guest07": {"name": "Guest 07", "email": "guest07@thebullmonkey.com", "password": "$2b$12$b8jAziWn11oAfJUlHlAsF.1TNLTjKMumKvUvNjUWgjXl.M8anhIhu",  "role": "guest"},
            "guest08": {"name": "Guest 08", "email": "guest08@thebullmonkey.com", "password": "$2b$12$KWN4eLqJICvi/hoHtf/.LO3aKpmD1BprxJc5hRswdmm7afRPZM2Fm",  "role": "guest"},
            "guest09": {"name": "Guest 09", "email": "guest09@thebullmonkey.com", "password": "$2b$12$V5mAgnxm7MfqwkXjOj5sReb5EEz8mqS0We6tKggh9UkRfiJ2zTJKu",  "role": "guest"},
            "guest10": {"name": "Guest 10", "email": "guest10@thebullmonkey.com", "password": "$2b$12$qhxR./ZBUIKLDoywrqCQEu.72XSMe7R8AG9NB9fMjGVgoVun5ZylW",  "role": "guest"},
        }
    }
    # Seed Firestore with fallback so next load uses Firestore
    seed_auth_credentials(fallback)
    return fallback


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

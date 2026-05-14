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


_BUILTIN_USERS = {
    "admin":   {"name": "Admin",   "email": "admin@thebullmonkey.com",   "password": "$2b$12$btb10qFHBD2bRIyKhkZ4SuVB7H8Lpmaly.z6Ojk5icbsGYFhiWwyO", "role": "admin"},
    "pipo":    {"name": "Pipo",    "email": "pipo@thebullmonkey.com",    "password": "$2b$12$UXiuFqWHAOOWQ3yCzvIKueShdcEczM1xA/.TLgV9jFze/4TbbZNpm",  "role": "guest"},
    "roro":    {"name": "Roro",    "email": "roro@thebullmonkey.com",    "password": "$2b$12$DQ1JSGKtp7A.KatpVareKONPJvYZOw.7HFuK12TzV9X2wkERuOEIG",  "role": "guest"},
    "berni":   {"name": "Berni",   "email": "berni@thebullmonkey.com",   "password": "$2b$12$2G/bLSfX3ZQhZXmgDGXbZesqyc5bx/Z8Rcq9eygCixcY09J/fV842",  "role": "guest"},
    "juan":    {"name": "Juan",    "email": "juan@thebullmonkey.com",    "password": "$2b$12$q5UJUNhpsV8uv1qKS7c2VOepFJpkLEcsihoISRSwMICD8xyxVmvu.",   "role": "guest"},
    "bonji":   {"name": "Bonji",   "email": "bonji@thebullmonkey.com",   "password": "$2b$12$SDzcNTIFJO5lEDi1HHcD.OCyiJfMih31m3iESrpgpv6zyC0MI99c2",  "role": "guest"},
    "insky":   {"name": "Insky",   "email": "insky@thebullmonkey.com",   "password": "$2b$12$HDyiLTDJlbbrkwZMtev3meCap0ID4ps2FqEpcaYaPTMvQe2PO/pd6",  "role": "guest"},
    "marito":  {"name": "Marito",  "email": "marito@thebullmonkey.com",  "password": "$2b$12$WmFNfIgWL4zG.JGMZ/zegu4qQJgzV72kLHfae0h9y4jxVJSB3Bdj.", "role": "guest"},
    "corve":   {"name": "Corve",   "email": "corve@thebullmonkey.com",   "password": "$2b$12$rMEo/X6aTN4/V70/P5GEYOpxHBGC.xPbp2zG1BdDBUAz6cIlfXScu", "role": "guest"},
    "borre":   {"name": "Borre",   "email": "borre@thebullmonkey.com",   "password": "$2b$12$2m.F9vKEwgWvpVKQy7SOCe4bIWnygYJopWV5CaqzXBJloBYfxQ10G",  "role": "guest"},
    "zata":    {"name": "Zata",    "email": "zata@thebullmonkey.com",    "password": "$2b$12$dR4pj25finzbseMGzv3dFuIU958aSWAi.tEuVWFkdp9B8XjAdNiEu",  "role": "guest"},
    "luis":    {"name": "Luis",    "email": "luis@thebullmonkey.com",    "password": "$2b$12$B0JvwajIk4gth7hfrRjF7uJHoM0mXLfXHfkL2Yb/mk4Ew4XkXRhu2",  "role": "guest"},
    "santino": {"name": "Santino", "email": "santino@thebullmonkey.com", "password": "$2b$12$o6R5F7nXhFsvhpQlymAtyOXekh7eda8TuRq3KqCgl7n5.aVGARzRC",  "role": "guest"},
}


def _get_credentials() -> dict:
    """
    Credential priority:
      1. Firestore app_config/credentials  (source of truth — all devices in sync)
         Missing built-in users are merged in automatically on every load.
      2. Hardcoded fallback                (when Firestore is unavailable)
    """
    from utils.db import get_auth_credentials, save_auth_credentials

    fs_creds = get_auth_credentials()
    if fs_creds and fs_creds.get("usernames"):
        existing = fs_creds["usernames"]
        # Merge any built-in users that are not yet in Firestore
        missing = {u: d for u, d in _BUILTIN_USERS.items() if u not in existing}
        if missing:
            existing.update(missing)
            fs_creds["usernames"] = existing
            try:
                save_auth_credentials(fs_creds)
            except Exception:
                pass
        return fs_creds

    # Firestore unavailable — use hardcoded fallback and try to seed
    fallback = {"usernames": dict(_BUILTIN_USERS)}
    try:
        save_auth_credentials(fallback)
    except Exception:
        pass
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

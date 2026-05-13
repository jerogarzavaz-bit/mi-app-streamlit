"""
Firebase Firestore persistence layer.
Falls back gracefully if Firebase is not configured.
"""
import json
import streamlit as st

SAVE_KEYS = [
    "portfolio", "watchlists", "profile",
    "alerts", "api_keys", "screen_history", "analyses",
]

_CONNECT_ERROR = None  # stores connection error for display in Settings


@st.cache_resource
def _get_db():
    global _CONNECT_ERROR
    try:
        from google.cloud import firestore
        from google.oauth2 import service_account
        fb = dict(st.secrets["firebase"])
        creds = service_account.Credentials.from_service_account_info(
            fb,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore",
            ],
        )
        client = firestore.Client(credentials=creds, project=fb["project_id"])
        _CONNECT_ERROR = None
        return client
    except Exception as e:
        _CONNECT_ERROR = str(e)
        return None


def get_connection_error() -> str | None:
    _get_db()  # ensure it has been attempted
    return _CONNECT_ERROR


def _clean(data: dict) -> dict:
    return json.loads(json.dumps(data, default=str))


def save_user_data(username: str) -> bool:
    db = _get_db()
    if db is None or not username:
        return False
    try:
        data = {}
        for key in SAVE_KEYS:
            val = st.session_state.get(key)
            if val is not None:
                if key == "analyses":
                    val = [{k: v for k, v in a.items()
                            if k not in ("text", "hist", "info")} for a in val]
                data[key] = val
        db.collection("users").document(username).set(_clean(data))
        return True
    except Exception as e:
        # Store error in session_state so it survives st.rerun()
        st.session_state["_db_save_error"] = str(e)
        return False


def load_user_data(username: str) -> bool:
    db = _get_db()
    if db is None or not username:
        return False
    try:
        doc = db.collection("users").document(username).get()
        if not doc.exists:
            return False
        data = doc.to_dict() or {}
        for key in SAVE_KEYS:
            if key in data:
                st.session_state[key] = data[key]
        return True
    except Exception as e:
        st.session_state["_db_load_error"] = str(e)
        return False


def is_configured() -> bool:
    return _get_db() is not None


# ── Auth credentials (stored in Firestore so secrets.toml is not needed) ──────

def get_auth_credentials() -> dict | None:
    """Return credentials dict from Firestore, or None if unavailable."""
    db = _get_db()
    if db is None:
        return None
    try:
        doc = db.collection("app_config").document("credentials").get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception:
        return None


def save_auth_credentials(creds: dict) -> bool:
    """Persist the full credentials dict to Firestore."""
    db = _get_db()
    if db is None:
        return False
    try:
        db.collection("app_config").document("credentials").set(_clean(creds))
        return True
    except Exception:
        return False


def seed_auth_credentials(creds: dict) -> bool:
    """Write credentials only if the Firestore doc doesn't exist yet."""
    db = _get_db()
    if db is None:
        return False
    try:
        ref = db.collection("app_config").document("credentials")
        if not ref.get().exists:
            ref.set(_clean(creds))
        return True
    except Exception:
        return False

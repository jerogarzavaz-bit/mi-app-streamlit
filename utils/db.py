"""
Firebase Firestore persistence layer.
Falls back gracefully (no error) if Firebase is not configured.
"""
import json
import streamlit as st

# Keys saved per user (excludes large/ephemeral data)
SAVE_KEYS = [
    "portfolio", "watchlists", "profile",
    "alerts", "api_keys", "screen_history",
    "analyses",
]


@st.cache_resource
def _get_db():
    try:
        from google.cloud import firestore
        from google.oauth2 import service_account
        fb = dict(st.secrets["firebase"])
        creds = service_account.Credentials.from_service_account_info(fb)
        return firestore.Client(credentials=creds, project=fb["project_id"])
    except Exception:
        return None


def _clean(data: dict) -> dict:
    """Make data JSON-serializable (handles pandas Timestamps, etc.)."""
    return json.loads(json.dumps(data, default=str))


def save_user_data(username: str) -> bool:
    """Save current session_state for this user to Firestore."""
    db = _get_db()
    if db is None:
        return False
    try:
        data = {}
        for key in SAVE_KEYS:
            val = st.session_state.get(key)
            if val is not None:
                # Strip huge text blobs from analyses to stay within Firestore limits
                if key == "analyses":
                    val = [{k: v for k, v in a.items()
                            if k not in ("text", "hist", "info")} for a in val]
                data[key] = val
        db.collection("users").document(username).set(_clean(data))
        return True
    except Exception as e:
        st.warning(f"Cloud save failed: {e}")
        return False


def load_user_data(username: str) -> bool:
    """Load user data from Firestore into session_state. Returns True on success."""
    db = _get_db()
    if db is None:
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
        st.warning(f"Cloud load failed: {e}")
        return False


def is_configured() -> bool:
    return _get_db() is not None

"""
Firebase Firestore persistence layer.
Falls back gracefully if Firebase is not configured.

Row Level Security (RLS):
  - _assert_own_user() enforces that every read/write targets the requesting user's doc.
  - All save/load functions check session username == passed username before touching Firestore.
"""
import json
import streamlit as st

SAVE_KEYS = [
    "portfolio", "watchlists", "profile",
    "alerts", "api_keys", "screen_history", "analyses",
]

_CONNECT_ERROR = None


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
    _get_db()
    return _CONNECT_ERROR


def _clean(data: dict) -> dict:
    return json.loads(json.dumps(data, default=str))


# ── Row Level Security enforcement ────────────────────────────────────────────

def _assert_own_user(username: str) -> None:
    """
    RLS gate: raises PermissionError if `username` does not match the
    currently authenticated session user. Prevents any code path from
    reading or writing another user's Firestore document.
    """
    session_user = st.session_state.get("username", "")
    if not session_user:
        raise PermissionError("RLS: no authenticated user in session.")
    if username != session_user:
        raise PermissionError(
            f"RLS violation: session user '{session_user}' "
            f"attempted to access '{username}' data."
        )


def clear_user_session_data() -> None:
    """
    Wipe all user-owned keys from session_state.
    Called when a different user logs in on the same browser session
    to prevent data bleed between accounts.
    """
    for key in SAVE_KEYS:
        st.session_state.pop(key, None)
    # Clear any derived/cached user flags
    for key in list(st.session_state.keys()):
        if key.startswith("_loaded_"):
            del st.session_state[key]


# ── User data ─────────────────────────────────────────────────────────────────

def save_user_data(username: str) -> bool:
    _assert_own_user(username)        # RLS check
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
    except PermissionError:
        raise
    except Exception as e:
        st.session_state["_db_save_error"] = str(e)
        return False


def load_user_data(username: str) -> bool:
    _assert_own_user(username)        # RLS check
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
    except PermissionError:
        raise
    except Exception as e:
        st.session_state["_db_load_error"] = str(e)
        return False


def is_configured() -> bool:
    return _get_db() is not None


# ── Auth credentials ──────────────────────────────────────────────────────────
# Stored in app_config/credentials — separate collection from user data.
# No RLS needed here: only hashed passwords are stored (not reversible),
# and the admin UI already enforces role checks before mutating this doc.

def get_auth_credentials() -> dict | None:
    db = _get_db()
    if db is None:
        return None
    try:
        doc = db.collection("app_config").document("credentials").get()
        return doc.to_dict() if doc.exists else None
    except Exception:
        return None


def save_auth_credentials(creds: dict) -> bool:
    db = _get_db()
    if db is None:
        return False
    try:
        db.collection("app_config").document("credentials").set(_clean(creds))
        return True
    except Exception:
        return False


def seed_auth_credentials(creds: dict) -> bool:
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


# ── Community chat ─────────────────────────────────────────────────────────────
# Messages are stored in the top-level `community_messages` collection.
# No RLS — all authenticated users can read and write. Users can only
# delete their own messages (enforced at app layer).

def post_community_message(username: str, display_name: str, text: str, tickers: list) -> bool:
    db = _get_db()
    if db is None or not username or not text.strip():
        return False
    try:
        from google.cloud import firestore as _fs
        db.collection("community_messages").add(_clean({
            "username":     username,
            "display_name": display_name,
            "text":         text.strip(),
            "tickers":      tickers,
            "timestamp":    _fs.SERVER_TIMESTAMP,
        }))
        return True
    except Exception:
        return False


def get_community_messages(limit: int = 100) -> list[dict]:
    db = _get_db()
    if db is None:
        return []
    try:
        docs = (db.collection("community_messages")
                  .order_by("timestamp", direction="DESCENDING")
                  .limit(limit)
                  .stream())
        msgs = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            msgs.append(d)
        return list(reversed(msgs))  # oldest first for chat display
    except Exception:
        return []


def delete_community_message(doc_id: str, requesting_user: str) -> bool:
    db = _get_db()
    if db is None:
        return False
    try:
        ref = db.collection("community_messages").document(doc_id)
        doc = ref.get()
        if not doc.exists:
            return False
        # Only owner or admin can delete
        owner = doc.to_dict().get("username", "")
        from utils.auth import is_admin
        if requesting_user != owner and not is_admin():
            return False
        ref.delete()
        return True
    except Exception:
        return False

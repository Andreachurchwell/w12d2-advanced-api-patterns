import requests
import streamlit as st
import os
import json
import time

# API_BASE_DEFAULT = "http://127.0.0.1:8000/v1"
# API_BASE_DEFAULT = os.getenv("API_BASE_URL") or os.getenv("API_BASE_URL") or "http://api:8000/v1"
API_BASE_DEFAULT = os.getenv("API_BASE_URL") or "http://localhost:8000/v1"

st.set_page_config(
    page_title="Watchlist Dashboard",
    page_icon="🎬",
    layout="wide",
)

# ---------- CSS (Cinematic red/black, softened + sharper) ----------
DASH_CSS = """
<style>
/* ===================== STREAMLIT CHROME (KEEP MENU) ===================== */
/* IMPORTANT: Do NOT hide header / toolbar — menu lives up here */
header[data-testid="stHeader"]{
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  pointer-events: auto !important;
  background: transparent !important;
  box-shadow: none !important;
}

/* Older + newer containers Streamlit uses for top-right menu/actions */
div[data-testid="stToolbar"],
div[data-testid="stHeaderActionElements"],
div[data-testid="stMainMenu"],
div[data-testid="stDecoration"]{
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  pointer-events: auto !important;
}

/* Make sure buttons inside are clickable/visible */
div[data-testid="stToolbar"] *,
div[data-testid="stHeaderActionElements"] *,
div[data-testid="stMainMenu"] *{
  visibility: visible !important;
  opacity: 1 !important;
  pointer-events: auto !important;
}

/* If you previously set a global "opacity" somewhere, this protects the menu */
#MainMenu { visibility: visible !important; }
button[title="Main menu"]{ visibility: visible !important; opacity: 1 !important; }

/* Keep footer hidden (safe) */
footer { visibility: hidden !important; }

/* ===================== LAYOUT ===================== */
.block-container{
  padding-top: 1.25rem !important;
  padding-bottom: 2rem !important;
  max-width: 1400px !important;
}

/* Background */
.stApp{
  background:
    radial-gradient(900px 520px at 12% 0%, rgba(195,7,16,0.18), transparent 62%),
    linear-gradient(180deg, #07070A, #0B0B10 40%, #07070A) !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: rgba(10,10,14,0.98) !important;
  border-right: 1px solid rgba(255,255,255,0.08) !important;
}
section[data-testid="stSidebar"] *{ color:#F5F5F1 !important; }

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"]{
  background: rgba(18,18,22,0.82) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 18px !important;
  padding: 16px !important;
  box-shadow: 0 14px 42px rgba(0,0,0,0.55) !important;
}

/* ===================== INPUTS (VISIBLE TYPING) ===================== */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input{
  background:#FFFFFF !important;
  color:#111111 !important;
  caret-color:#111111 !important;
  border-radius:12px !important;
  border:1px solid rgba(255,255,255,0.18) !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
.stNumberInput input::placeholder{
  color: rgba(17,17,17,0.55) !important;
  opacity:1 !important;
}

/* BaseWeb inputs */
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input{
  background:#FFFFFF !important;
  color:#111111 !important;
  caret-color:#111111 !important;
}

/* Autofill */
input:-webkit-autofill{
  -webkit-text-fill-color:#111111 !important;
  transition: background-color 9999s ease-in-out 0s;
}

/* Select dropdown text */
div[data-baseweb="select"] *{ color:#111111 !important; }

/* Buttons */
.stButton > button{ border-radius:12px !important; }

/* Tabs */
div[role="tablist"] button{ border-radius:999px !important; }

/* Metrics readable */
div[data-testid="stMetric"] *{ color:#F5F5F1 !important; }
</style>
"""
st.markdown(DASH_CSS, unsafe_allow_html=True)


def api_post(api_base: str, path: str, payload: dict, token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(f"{api_base}{path}", json=payload, headers=headers, timeout=12)


def api_get(api_base: str, path: str, token: str | None = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(f"{api_base}{path}", headers=headers, timeout=12)


def api_patch(api_base: str, path: str, payload: dict, token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.patch(f"{api_base}{path}", json=payload, headers=headers, timeout=12)


def api_delete(api_base: str, path: str, token: str | None = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.delete(f"{api_base}{path}", headers=headers, timeout=12)


# -----------------------------
# Helpers (UI)
# -----------------------------
def show_headers(resp: requests.Response):
    # proof headers (case-insensitive in requests, but we'll read via .get)
    keys = [
        "x-request-id",
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
        "x-ratelimit-reset",
        "retry-after",
    ]
    present = {}
    for k in keys:
        v = resp.headers.get(k)
        if v is not None:
            present[k] = v

    if present:
        st.caption("Response headers (proof)")
        st.json(present)


def nice_json(resp: requests.Response):
    st.caption(f"HTTP {resp.status_code}")
    show_headers(resp)
    try:
        st.json(resp.json())
    except Exception:
        st.code(resp.text)


def check_api_up(api_base: str) -> str:
    # your api_base includes /v1; health is at /health
    try:
        root = api_base.replace("/v1", "")
        r = requests.get(f"{root}/health", timeout=3)
        return "UP" if r.status_code == 200 else "DOWN"
    except Exception:
        return "DOWN"


def refresh_watchlist():
    """Pull latest watchlist and display it (with skip/limit/filter/sort)."""
    skip = st.session_state.skip
    limit = st.session_state.limit
    filter_type = st.session_state.filter_type
    sort = st.session_state.sort

    qs = f"skip={skip}&limit={limit}&sort={sort}"
    if filter_type != "(all)":
        qs += f"&type={filter_type}"

    resp = api_get(
        st.session_state.api_base,
        f"/watchlists/?{qs}",
        st.session_state.token,
    )
    nice_json(resp)


# -----------------------------
# Session State
# -----------------------------
if "api_base" not in st.session_state:
    st.session_state.api_base = API_BASE_DEFAULT
if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = ""
if "skip" not in st.session_state:
    st.session_state.skip = 0
if "limit" not in st.session_state:
    st.session_state.limit = 10
if "filter_type" not in st.session_state:
    st.session_state.filter_type = "(all)"
if "sort" not in st.session_state:
    st.session_state.sort = "created_at_desc"


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 🎬 Watchlist")
    st.caption("FastAPI + JWT + Protected routes")
    st.divider()

    st.session_state.api_base = st.text_input("API Base URL", value=st.session_state.api_base)

    # hard guard: if running in docker, prevent localhost/127.0.0.1 mistake
    if "localhost" in st.session_state.api_base or "127.0.0.1" in st.session_state.api_base:
        st.warning("In Docker, API base must be http://api:8000/v1 (not localhost).")

    st.divider()
    st.markdown("### Session")

    if st.session_state.token:
        st.success("Logged in")
        st.code(st.session_state.email or "user", language="text")
        if st.button("Log out", use_container_width=True):
            st.session_state.token = None
            st.session_state.email = ""
            st.rerun()
    else:
        st.info("Not logged in")

    st.divider()
    st.caption("Tip: If login fails, double-check email/password or re-register.")


# -----------------------------
# Header
# -----------------------------
st.markdown("# 🎬 Watchlist Dashboard")
st.caption("FastAPI + JWT + protected Watchlists (with rate-limit + request-id proof headers).")

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Auth", "ON" if st.session_state.token else "OFF")
with k2:
    st.metric("API", check_api_up(st.session_state.api_base))
with k3:
    st.metric("Mode", "Local Dev")

st.divider()

# -----------------------------
# Main Layout
# -----------------------------
col_auth, col_data = st.columns([0.50, 0.50], gap="large")

with col_auth:
    with st.container(border=True):
        st.subheader("🔐 Authentication")
        tabs = st.tabs(["Register", "Login", "Me"])

        with tabs[0]:
            st.caption("Create a user (stored in DB).")
            reg_email = st.text_input("Email", key="reg_email", placeholder="test@example.com")
            reg_pw = st.text_input("Password", type="password", key="reg_pw", placeholder="At least 8 chars")

            if st.button("Create account", use_container_width=True, type="primary"):
                resp = api_post(st.session_state.api_base, "/auth/register", {"email": reg_email, "password": reg_pw})
                nice_json(resp)

        with tabs[1]:
            st.caption("Login and store JWT in this dashboard session.")
            login_email = st.text_input("Email", key="login_email", placeholder="test@example.com")
            login_pw = st.text_input("Password", type="password", key="login_pw", placeholder="Same password")

            if st.button("Login", use_container_width=True, type="primary"):
                resp = api_post(st.session_state.api_base, "/auth/login", {"email": login_email, "password": login_pw})
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "ok":
                        st.session_state.token = data["access_token"]
                        st.session_state.email = login_email.lower().strip()
                        st.success("Logged in ✅")
                nice_json(resp)

        with tabs[2]:
            st.caption("Protected endpoint: returns the logged-in email.")
            if st.button("Call /me", use_container_width=True):
                if not st.session_state.token:
                    st.warning("Login first.")
                else:
                    resp = api_get(st.session_state.api_base, "/auth/me", st.session_state.token)
                    nice_json(resp)

with col_data:
    with st.container(border=True):
        st.subheader("📌 Watchlists")
        st.caption("Protected endpoint: `GET /v1/watchlists/` (supports filter + sort)")

        c1, c2 = st.columns(2)
        with c1:
            st.session_state.skip = st.number_input("Skip", min_value=0, step=1, value=st.session_state.skip)
        with c2:
            st.session_state.limit = st.number_input("Limit", min_value=1, step=1, value=st.session_state.limit)

        f1, f2 = st.columns(2)
        with f1:
            st.session_state.filter_type = st.selectbox("Filter type", ["(all)", "movie", "show"], index=["(all)", "movie", "show"].index(st.session_state.filter_type))
        with f2:
            st.session_state.sort = st.selectbox("Sort", ["created_at_desc", "created_at_asc"], index=["created_at_desc", "created_at_asc"].index(st.session_state.sort))

        if st.button("Load my watchlist", use_container_width=True, type="primary"):
            if not st.session_state.token:
                st.warning("Login first.")
            else:
                refresh_watchlist()

        st.divider()
        st.subheader("➕ Add item")

        new_title = st.text_input("Title", key="new_title", placeholder="The Matrix")
        new_type = st.selectbox("Type", ["movie", "show"], key="new_type")

        if st.button("Add to watchlist", use_container_width=True, key="btn_add"):
            if not st.session_state.token:
                st.warning("Login first.")
            else:
                resp = api_post(
                    st.session_state.api_base,
                    "/watchlists/items",
                    {"title": new_title, "type": new_type},
                    st.session_state.token,
                )
                nice_json(resp)
                refresh_watchlist()

        st.divider()
        st.subheader("🗑️ Remove item")

        del_id = st.number_input("Item ID to delete", min_value=1, step=1, key="del_id")

        if st.button("Delete item", use_container_width=True, key="btn_delete"):
            if not st.session_state.token:
                st.warning("Login first.")
            else:
                resp = api_delete(
                    st.session_state.api_base,
                    f"/watchlists/items/{int(del_id)}",
                    st.session_state.token,
                )
                nice_json(resp)
                refresh_watchlist()

        st.divider()
        st.subheader("✏️ Update item")

        upd_id = st.number_input("Item ID to update", min_value=1, step=1, key="upd_id")
        upd_title = st.text_input("New title (optional)", key="upd_title", placeholder="Leave blank to keep same")
        upd_type = st.selectbox("New type (optional)", ["(no change)", "movie", "show"], key="upd_type")

        if st.button("Update item", use_container_width=True, key="btn_update"):
            if not st.session_state.token:
                st.warning("Login first.")
            else:
                payload = {}
                if upd_title.strip():
                    payload["title"] = upd_title.strip()
                if upd_type != "(no change)":
                    payload["type"] = upd_type

                if not payload:
                    st.warning("Enter a title and/or choose a type to update.")
                else:
                    resp = api_patch(
                        st.session_state.api_base,
                        f"/watchlists/items/{int(upd_id)}",
                        payload,
                        st.session_state.token,
                    )
                    nice_json(resp)
                    refresh_watchlist()

        st.divider()
        st.subheader("🧪 Caching demo (call twice)")
        st.caption("Your API caches GET /watchlists for ~30 seconds. This calls twice to show speed difference.")
        if st.button("Cache demo (call twice)", use_container_width=True):
            if not st.session_state.token:
                st.warning("Login first.")
            else:
                # use current query settings too
                skip = st.session_state.skip
                limit = st.session_state.limit
                filter_type = st.session_state.filter_type
                sort = st.session_state.sort

                qs = f"skip={skip}&limit={limit}&sort={sort}"
                if filter_type != "(all)":
                    qs += f"&type={filter_type}"

                t0 = time.time()
                r1 = api_get(st.session_state.api_base, f"/watchlists/?{qs}", st.session_state.token)
                t1 = time.time()
                r2 = api_get(st.session_state.api_base, f"/watchlists/?{qs}", st.session_state.token)
                t2 = time.time()

                st.write(f"First call:  {(t1 - t0):.3f}s")
                st.write(f"Second call: {(t2 - t1):.3f}s (should be faster if cached)")
                nice_json(r2)

        st.divider()
        st.subheader("🩺 Health checks")
        if st.button("Call /health/detailed", use_container_width=True):
            resp = api_get(st.session_state.api_base, "/health/detailed", st.session_state.token)
            nice_json(resp)

        st.divider()
        st.subheader("🌐 External API demo (async)")
        if st.button("Call /external/github", use_container_width=True):
            resp = api_get(st.session_state.api_base, "/external/github", st.session_state.token)
            nice_json(resp)
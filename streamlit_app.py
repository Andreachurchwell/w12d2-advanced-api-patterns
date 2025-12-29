import requests
import streamlit as st

API_BASE_DEFAULT = "http://127.0.0.1:8000/v1"

st.set_page_config(
    page_title="Watchlist Dashboard",
    page_icon="🎬",
    layout="wide",
)

# ---------- CSS (Cinematic red/black, softened + sharper) ----------
DASH_CSS = """
<style>
/* Hide Streamlit chrome */

footer {visibility: hidden;}


/* Page width + spacing */
.block-container { padding-top: 1.25rem; padding-bottom: 2.25rem; max-width: 1400px; }

/* Cinematic background (softened red glow) */
.stApp {
  background:
    radial-gradient(900px 520px at 12% 0%, rgba(195,7,16,0.22), transparent 62%),
    radial-gradient(900px 520px at 88% 10%, rgba(255,255,255,0.06), transparent 58%),
    linear-gradient(180deg, #07070A, #0B0B10 40%, #07070A);
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: rgba(10, 10, 14, 0.98);
  border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] * { color: #F5F5F1; }

/* Headline font (safe: if not available, falls back cleanly) */
h1, h2, h3, .stMarkdown, .stTextInput label, .stSelectbox label, .stMetric label {
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, "Noto Sans", "Liberation Sans", sans-serif;
}

/* Title styling */
h1 {
  letter-spacing: 0.02em !important;
  text-transform: uppercase !important;
}

/* Card containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(18, 18, 22, 0.78);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 14px 42px rgba(0,0,0,0.55);
}

/* Make st.container(border=True) look more premium */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div[data-testid="stVerticalBlock"]) {
  border: 1px solid rgba(255,255,255,0.10);
}

/* Buttons */
.stButton > button {
  border-radius: 14px;
  padding: 0.70rem 1.0rem;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.04);
  color: #F5F5F1;
  transition: transform 120ms ease, box-shadow 160ms ease, border 160ms ease, background 160ms ease;
}
.stButton > button:hover {
  border: 1px solid rgba(195,7,16,0.55);
  box-shadow: 0 12px 34px rgba(195,7,16,0.14);
  transform: translateY(-1px);
}
.stButton > button:active {
  transform: translateY(0px);
}

/* Primary buttons (Streamlit "type=primary") */
.stButton > button[kind="primary"] {
  background: linear-gradient(180deg, #C30710, #8F050C) !important;
  border: 1px solid rgba(195,7,16,0.55) !important;
  color: #F5F5F1 !important;
  box-shadow: 0 10px 28px rgba(195,7,16,0.16);
}
.stButton > button[kind="primary"]:hover {
  border: 1px solid rgba(255,255,255,0.18) !important;
  box-shadow: 0 14px 38px rgba(195,7,16,0.20);
}

/* Text inputs */
.stTextInput input {
  border-radius: 14px !important;
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  color: #F5F5F1 !important;
}
.stTextInput input:focus {
  border: 1px solid rgba(195,7,16,0.60) !important;
  box-shadow: 0 0 0 3px rgba(195,7,16,0.16) !important;
}

/* Tabs — no harsh red ring */
div[role="tablist"] button {
  border-radius: 999px !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  background: rgba(255,255,255,0.03) !important;
  color: #F5F5F1 !important;
  margin-right: 6px !important;
}
div[role="tablist"] button[aria-selected="true"] {
  border: 1px solid rgba(195,7,16,0.50) !important;
  background: rgba(195,7,16,0.12) !important;
  box-shadow: 0 10px 26px rgba(195,7,16,0.08);
}

/* Metrics — make KPI tiles look like dashboard panels */
div[data-testid="stMetric"] {
  padding: 18px 18px;
  border-radius: 18px;
  border: 1px solid rgba(195,7,16,0.18);
  background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.03));
  box-shadow: 0 12px 34px rgba(0,0,0,0.35);
}
div[data-testid="stMetric"] * { color: #F5F5F1; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  font-size: 2.1rem !important;
  letter-spacing: 0.01em;
}

/* Alerts */
div[data-testid="stAlert"] {
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.04);
}
</style>
"""
st.markdown(DASH_CSS, unsafe_allow_html=True)

# ---------- Helpers ----------
def api_post(api_base: str, path: str, json: dict, token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(f"{api_base}{path}", json=json, headers=headers, timeout=12)

def api_get(api_base: str, path: str, token: str | None = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(f"{api_base}{path}", headers=headers, timeout=12)

def api_patch(api_base: str, path: str, json: dict, token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.patch(f"{api_base}{path}", json=json, headers=headers, timeout=12)


def nice_json(resp: requests.Response):
    st.caption(f"HTTP {resp.status_code}")
    try:
        st.json(resp.json())
    except Exception:
        st.code(resp.text)

def check_api_up(api_base: str) -> str:
    try:
        r = requests.get(api_base.replace("/v1", "") + "/health", timeout=3)
        return "UP" if r.status_code == 200 else "DOWN"
    except Exception:
        return "DOWN"
    
def api_delete(api_base: str, path: str, token: str | None = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.delete(f"{api_base}{path}", headers=headers, timeout=12)

def refresh_watchlist():
    """Pull latest watchlist and display it."""
    resp2 = api_get(st.session_state.api_base, "/watchlists/", st.session_state.token)
    nice_json(resp2)

# ---------- Session State ----------
if "api_base" not in st.session_state:
    st.session_state.api_base = API_BASE_DEFAULT
if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = ""

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🎬 Watchlist")
    st.caption("FastAPI + JWT + Protected routes")
    st.divider()

    st.session_state.api_base = st.text_input("API Base URL", value=st.session_state.api_base)

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


# ---------- Header ----------
st.markdown("# 🎬 Watchlist Dashboard")
st.caption("Flashy red + black cinematic test UI (FastAPI + JWT + protected Watchlists).")

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Auth", "ON" if st.session_state.token else "OFF")
with k2:
    st.metric("API", check_api_up(st.session_state.api_base))
with k3:
    st.metric("Mode", "Local Dev")

st.divider()

# ---------- Main Layout ----------
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
            login_email = st.text_input("Email ", key="login_email", placeholder="test@example.com")
            login_pw = st.text_input("Password ", type="password", key="login_pw", placeholder="Same password")

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
        st.caption("Protected endpoint: `GET /v1/watchlists/`")

        if st.button("Load my watchlist", use_container_width=True, type="primary"):
            if not st.session_state.token:
                st.warning("Login first.")
            else:
                resp = api_get(st.session_state.api_base, "/watchlists/", st.session_state.token)
                nice_json(resp)

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

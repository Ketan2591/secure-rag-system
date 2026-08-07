import html
import streamlit as st
from src.pages.styles import load_styles
from src.pages.login import show_login
from src.pages.register import show_register
from src.pages.dashboard import show_dashboard
from src.pages.documents import show_documents
from src.pages.history import show_history
from src.pages.profile import show_profile
from src.pages.settings import show_settings

# Page Configuration
st.set_page_config(
    page_title="SecureRAG v2 | Private Document Workspace",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "page" not in st.session_state:
    st.session_state.page = "login"

# Load Master CSS Styles
load_styles()

# Authentication Routing
if not st.session_state.logged_in:
    if st.session_state.page == "register":
        show_register()
    else:
        show_login()
    st.stop()

# Sidebar Navigation for Authenticated Users
user = st.session_state.current_user or {}
customer_id = user.get("customer_id", "CUS_GUEST")
full_name = user.get("full_name", "User")

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-title">🔐 SecureRAG</div>
            <div class="brand-subtitle">Private Workspace v2</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="sidebar-user-card">
            <div class="user-name">👤 {html.escape(full_name)}</div>
            <div class="user-id">Customer ID: {html.escape(customer_id)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    curr_page = st.session_state.get("page", "dashboard")

    if st.button("🏠 Dashboard", use_container_width=True, type="primary" if curr_page == "dashboard" else "secondary"):
        st.session_state.page = "dashboard"
        st.rerun()

    if st.button("📄 My Documents", use_container_width=True, type="primary" if curr_page == "documents" else "secondary"):
        st.session_state.page = "documents"
        st.rerun()

    if st.button("💬 Chat History", use_container_width=True, type="primary" if curr_page == "history" else "secondary"):
        st.session_state.page = "history"
        st.rerun()

    if st.button("👤 My Profile", use_container_width=True, type="primary" if curr_page == "profile" else "secondary"):
        st.session_state.page = "profile"
        st.rerun()

    if st.button("⚙️ Settings", use_container_width=True, type="primary" if curr_page == "settings" else "secondary"):
        st.session_state.page = "settings"
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.page = "login"
        st.rerun()

# Router Execution
page_map = {
    "dashboard": show_dashboard,
    "documents": show_documents,
    "history": show_history,
    "profile": show_profile,
    "settings": show_settings,
}

render_page = page_map.get(st.session_state.page, show_dashboard)
render_page()
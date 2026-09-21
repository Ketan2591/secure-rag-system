import html
import streamlit as st
from src.database import get_user_chat_history, get_user_documents
from src.pages.styles import load_styles
from src.pages.icons import icon
from src.pages.documents import show_documents
from src.pages.login import show_login
from src.pages.register import show_register
from src.pages.dashboard import show_dashboard
from src.pages.history import show_history
from src.pages.profile import show_profile
from src.pages.settings import show_settings

# Sets the browser tab title, favicon, and a wide, expanded-sidebar layout for the whole app. Must run before any other Streamlit call.
st.set_page_config(
    page_title="SecureRAG | Private Document Workspace",
    page_icon="src/assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sets default values for session state the first time the app loads, so the rest of the code can safely assume these keys already exist.
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "ui_theme" not in st.session_state:
    st.session_state.ui_theme = "dark"

if st.session_state.pop("clear_global_search", False):
    st.session_state.global_search = ""

# Loads the app's CSS for the currently selected theme (light or dark).
load_styles(st.session_state.ui_theme)

# If the user hasn't logged in yet, show only the login/register page and stop here, so no protected page code runs.
if not st.session_state.logged_in:
    if st.session_state.page == "register":
        show_register()
    else:
        show_login()
    st.stop()

# Pulls the logged-in user's basic info out of session state, used below in the top navbar and the sidebar.
user = st.session_state.current_user or {}
customer_id = user.get("customer_id", "CUS_GUEST")
full_name = user.get("full_name", "User")
initial = (full_name.strip()[:1] or "U").upper()

# Shared application command bar and functional appearance controls.
navbar = st.container(key="navbar_row")
top_search, top_space, top_status, top_theme = navbar.columns(
    [4.6, 1.6, 1.7, 1.3], vertical_alignment="center"
)
with top_search:
    search_query = st.text_input(
        "Search your documents or ask anything",
        key="global_search",
        placeholder="Search your documents or ask anything…",
        label_visibility="collapsed",
    )
with top_status:
    st.markdown(
        f'<div class="status-pill"><span class="dot"></span>{icon("lock", 13)}&nbsp;Workspace isolated</div>',
        unsafe_allow_html=True,
    )
with top_theme:
    active_theme = st.session_state.get("ui_theme", "dark")
    theme_choice = st.segmented_control(
        "Appearance",
        options=[":material/light_mode:", ":material/dark_mode:"],
        default=":material/light_mode:" if active_theme == "light" else ":material/dark_mode:",
        label_visibility="collapsed",
        key="theme_toggle",
    )
    wanted_theme = "light" if theme_choice == ":material/light_mode:" else "dark"
    if wanted_theme != active_theme:
        st.session_state.ui_theme = wanted_theme
        st.rerun()

# Global search: surfaces matching documents and past conversations from anywhere in the app.
if search_query and search_query.strip():
    needle = search_query.strip().lower()
    matched_docs = [d for d in get_user_documents(customer_id) if needle in str(d.get("filename", "")).lower()][:5]
    matched_chats = [
        h for h in get_user_chat_history(customer_id, include_deleted=False)
        if needle in str(h.get("user_message", "")).lower() or needle in str(h.get("assistant_response", "")).lower()
    ][:5]

    with st.container(border=True):
        if not matched_docs and not matched_chats:
            st.markdown(
                f'<div class="search-empty">{icon("search", 14)}No documents or conversations match "{html.escape(search_query.strip())}".</div>',
                unsafe_allow_html=True,
            )
        else:
            if matched_docs:
                st.markdown('<div class="search-group-label">Documents</div>', unsafe_allow_html=True)
                for doc in matched_docs:
                    if st.button(str(doc.get("filename", "Document")), icon=":material/description:", key=f"search_doc_{doc.get('id')}", use_container_width=True):
                        st.session_state.page = "documents"
                        st.session_state.clear_global_search = True
                        st.rerun()
            if matched_chats:
                st.markdown('<div class="search-group-label">Conversations</div>', unsafe_allow_html=True)
                for chat in matched_chats:
                    snippet = str(chat.get("user_message", "")).strip() or "Conversation"
                    if st.button(snippet[:80], icon=":material/forum:", key=f"search_chat_{chat.get('id')}", use_container_width=True):
                        st.session_state.page = "history"
                        st.session_state.clear_global_search = True
                        st.rerun()

# Sidebar: brand header, user card, page navigation buttons, logout, and a footer note about data privacy.
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="brand-icon">{icon("shield", 18)}</div>
            <div class="brand-text">
                <div class="brand-title">SecureRAG</div>
                <div class="brand-subtitle">Private knowledge workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="sidebar-user-card">
            <div class="avatar sm">{html.escape(initial)}</div>
            <div>
                <div class="user-name">{html.escape(full_name)}</div>
                <div class="user-id">Customer ID: {html.escape(customer_id)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    curr_page = st.session_state.get("page", "dashboard")

    nav_items = [
        ("dashboard", "Dashboard", ":material/space_dashboard:"),
        ("documents", "My Documents", ":material/folder:"),
        ("history", "Chat History", ":material/forum:"),
        ("profile", "My Profile", ":material/person:"),
        ("settings", "Settings", ":material/settings:"),
    ]
    for key, label, mat_icon in nav_items:
        if st.button(label, icon=mat_icon, use_container_width=True, type="primary" if curr_page == key else "secondary"):
            st.session_state.page = key
            st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.button("Logout", icon=":material/logout:", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.page = "login"
        st.rerun()

    st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="sidebar-footer-card">
            {icon("shield-check", 18)}
            <div>
                <div class="footer-title">Your data is private and secure</div>
                <div class="footer-text">Documents and conversations stay within your workspace.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Looks up which page function to run based on the current page in session state, and renders it (dashboard is the default).
page_map = {
    "dashboard": show_dashboard,
    "documents": show_documents,
    "history": show_history,
    "profile": show_profile,
    "settings": show_settings,
}

render_page = page_map.get(st.session_state.page, show_dashboard)
render_page()

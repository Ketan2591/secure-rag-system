import re
import streamlit as st
from src.auth import login_user
from src.pages.icons import icon


# Checks that a string looks like "name@domain.tld" using a simple regex. Does not verify the email actually exists or is reachable.
def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None


# Renders the login page: a centered card with the app branding, an email/password form, and a link to the register page.
def show_login():
    # Center the login card on the page using empty side columns.
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown(
            f"""
            <div class="auth-brand">
                <div class="auth-brand-icon">{icon("shield", 26)}</div>
                <h1>SecureRAG</h1>
                <p>Sign in to your private document workspace</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.subheader("Login")

            # Login form fields.
            email = st.text_input("Email Address", placeholder="example@gmail.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

            remember = st.checkbox("Remember me", key="login_remember")

            login = st.button("Sign In", type="primary", icon=":material/login:", use_container_width=True, key="login_submit_btn")

            # On submit: validate the input first, then check the credentials, and only log the user in if both pass.
            if login:
                email = email.strip()
                if not email:
                    st.warning("Please enter your email.")
                    return
                if not is_valid_email(email):
                    st.error("Please enter a valid email address.")
                    return
                if not password:
                    st.warning("Please enter your password.")
                    return

                success, result = login_user(email=email, password=password)
                if not success:
                    st.error(result)
                    return

                # Credentials are valid: store the logged-in user in session state and send them to the dashboard.
                st.session_state.logged_in = True
                st.session_state.current_user = result
                st.session_state.page = "dashboard"
                if remember:
                    st.session_state.remember_me = True

                st.success("Login successful!")
                st.rerun()

        # Link to switch over to the registration page.
        st.write("")
        st.markdown("<div class='auth-footnote'>Don't have an account?</div>", unsafe_allow_html=True)
        if st.button("Create New Account", icon=":material/person_add:", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

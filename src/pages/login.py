import re
import streamlit as st
from src.auth import login_user

def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None

def show_login():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center; padding: 20px 0 10px 0;">
                <h1 style="font-size: 32px; font-weight: 800; color: #ffffff; margin-bottom: 5px;">🔐 SecureRAG</h1>
                <p style="color: #94a3b8; font-size: 13px;">
                    Sign in to your private document workspace
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.subheader("Login")

            email = st.text_input("Email Address", placeholder="example@gmail.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            remember = st.checkbox("Remember me")

            login = st.button("Sign In", type="primary", use_container_width=True)

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

                st.session_state.logged_in = True
                st.session_state.current_user = result
                st.session_state.page = "dashboard"
                if remember:
                    st.session_state.remember_me = True

                st.success("Login successful!")
                st.rerun()

        st.write("")
        st.markdown("<div style='text-align:center; color:#94a3b8; font-size:12px;'>Don't have an account?</div>", unsafe_allow_html=True)
        if st.button("Create New Account", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
import re
import streamlit as st
from src.auth import register_user

def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None

def is_strong_password(password: str) -> bool:
    return len(password) >= 8

def show_register():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center; padding: 20px 0 10px 0;">
                <h1 style="font-size: 32px; font-weight: 800; color: #ffffff; margin-bottom: 5px;">📝 Create Account</h1>
                <p style="color: #94a3b8; font-size: 13px;">
                    Register to access your SecureRAG workspace
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email Address", placeholder="example@gmail.com")
            password = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

            register = st.button("Create Account", type="primary", use_container_width=True)

            if register:
                full_name = full_name.strip()
                email = email.strip().lower()

                if not full_name:
                    st.warning("Please enter your full name.")
                    return
                if not email:
                    st.warning("Please enter your email.")
                    return
                if not is_valid_email(email):
                    st.error("Please enter a valid email address.")
                    return
                if not password:
                    st.warning("Please enter a password.")
                    return
                if not is_strong_password(password):
                    st.error("Password must contain at least 8 characters.")
                    return
                if password != confirm_password:
                    st.error("Passwords do not match.")
                    return

                success, result = register_user(
                    full_name=full_name,
                    email=email,
                    password=password,
                )

                if success:
                    st.success(f"✅ Registration Successful!\n\nYour Customer ID is **{result}**")
                    st.info("Please login using your registered email and password.")
                    if st.button("Go to Login", use_container_width=True):
                        st.session_state.page = "login"
                        st.rerun()
                else:
                    st.error(result)

        st.write("")
        st.markdown("<div style='text-align:center; color:#94a3b8; font-size:12px;'>Already have an account?</div>", unsafe_allow_html=True)
        if st.button("Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
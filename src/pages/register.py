import re
import streamlit as st
from src.auth import register_user
from src.pages.icons import icon


# Checks that a string looks like "name@domain.tld" using a simple regex. Does not verify the email actually exists.
def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None


# Minimum password rule for this app: at least 8 characters, nothing else required.
def is_strong_password(password: str) -> bool:
    return len(password) >= 8


# Renders the "Create Account" page: a registration form, a success message with the new Customer ID after signup,
# and a link back to the login page.
def show_register():
    # Center the registration card on the page using empty side columns.
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown(
            f"""
            <div class="auth-brand">
                <div class="auth-brand-icon">{icon("shield", 26)}</div>
                <h1>Create Account</h1>
                <p>Register to access your SecureRAG workspace</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            # Registration form fields.
            full_name = st.text_input("Full Name", placeholder="Enter your full name", key="register_full_name")
            email = st.text_input("Email Address", placeholder="example@gmail.com", key="register_email")
            password = st.text_input("Password", type="password", placeholder="Minimum 8 characters", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="register_confirm_password")

            register = st.button("Create Account", type="primary", icon=":material/person_add:", use_container_width=True, key="register_submit_btn")

            # On submit: validate every field first, then create the account only if all checks pass.
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
                    # Stash the new customer_id in session state and rerun so the success message below can show it.
                    st.session_state.just_registered_id = result
                    st.rerun()
                else:
                    st.error(result)

            # Shown right after a successful registration: displays the new Customer ID and a button to head to login.
            if st.session_state.get("just_registered_id"):
                st.success(f"✅ Registration Successful!\n\nYour Customer ID is **{st.session_state.just_registered_id}**")
                st.info("Please login using your registered email and password.")
                if st.button("Go to Login", use_container_width=True, key="register_goto_login_btn"):
                    st.session_state.pop("just_registered_id", None)
                    st.session_state.page = "login"
                    st.rerun()

        # Link to switch back to the login page.
        st.write("")
        st.markdown("<div class='auth-footnote'>Already have an account?</div>", unsafe_allow_html=True)
        if st.button("Back to Login", icon=":material/login:", use_container_width=True, key="register_back_to_login_btn"):
            st.session_state.pop("just_registered_id", None)
            st.session_state.page = "login"
            st.rerun()
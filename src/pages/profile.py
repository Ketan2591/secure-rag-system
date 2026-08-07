import html
import streamlit as st
from src.database import update_user_profile, update_user_password
from src.auth import hash_password, verify_password

def show_profile():
    user = st.session_state.get("current_user") or {}
    user_id = user.get("id")
    customer_id = user.get("customer_id", "CUS_GUEST")
    full_name = user.get("full_name", "User")
    email = user.get("email", "user@example.com")
    is_active = user.get("is_active", True)
    created_at = user.get("created_at", "N/A")
    last_login = user.get("last_login", "N/A")

    st.markdown("## 👤 User Profile")
    st.caption("Manage your account information, Customer ID details, and credentials.")

    st.write("")

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown("### 📋 Account Details")
        st.markdown(
            f"""
            <div class="stat-card" style="margin-bottom: 20px;">
                <div style="font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 12px;">
                    {html.escape(full_name)}
                </div>
                <div style="font-size: 13px; color: #94a3b8; margin-bottom: 6px;">
                    📧 Email: <strong style="color: #f8fafc;">{html.escape(email)}</strong>
                </div>
                <div style="font-size: 13px; color: #94a3b8; margin-bottom: 6px;">
                    🔑 Customer ID: <span class="header-badge">{html.escape(customer_id)}</span>
                </div>
                <div style="font-size: 13px; color: #94a3b8; margin-bottom: 6px;">
                    🟢 Account Status: <strong style="color: #4ade80;">Active</strong>
                </div>
                <div style="font-size: 13px; color: #94a3b8; margin-bottom: 6px;">
                    📅 Member Since: <strong style="color: #cbd5e1;">{html.escape(str(created_at))}</strong>
                </div>
                <div style="font-size: 13px; color: #94a3b8;">
                    🕒 Last Login: <strong style="color: #cbd5e1;">{html.escape(str(last_login))}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("edit_name_form"):
            st.markdown("#### Edit Display Name")
            new_name = st.text_input("Full Name", value=full_name)
            submit_name = st.form_submit_button("Update Name", type="primary")

            if submit_name:
                clean_n = new_name.strip()
                if not clean_n:
                    st.warning("Full name cannot be empty.")
                else:
                    update_user_profile(user_id, clean_n)
                    st.session_state.current_user["full_name"] = clean_n
                    st.success("Profile updated successfully!")
                    st.rerun()

    with col2:
        st.markdown("### 🔒 Security & Password")
        with st.form("change_password_form"):
            st.markdown("#### Change Password")
            old_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password (Min 8 chars)", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            submit_pass = st.form_submit_button("Update Password", type="primary")

            if submit_pass:
                if not old_pass or not new_pass or not confirm_pass:
                    st.warning("Please fill in all password fields.")
                elif not verify_password(old_pass, user.get("password_hash", "")):
                    st.error("Current password is incorrect.")
                elif len(new_pass) < 8:
                    st.error("New password must be at least 8 characters long.")
                elif new_pass != confirm_pass:
                    st.error("New passwords do not match.")
                else:
                    new_hash = hash_password(new_pass)
                    update_user_password(user_id, new_hash)
                    st.session_state.current_user["password_hash"] = new_hash
                    st.success("Password changed successfully!")
                    st.rerun()

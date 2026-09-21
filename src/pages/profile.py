import html
import streamlit as st
from src.database import update_user_profile, update_user_password
from src.auth import hash_password, verify_password
from src.pages.icons import icon


# Renders the "My Profile" page: an account details card with a display-name form on the left,
# and a change-password form on the right.
def show_profile():
    # Pull the logged-in user's details out of session state for display and as defaults in the forms below.
    user = st.session_state.get("current_user") or {}
    user_id = user.get("id")
    customer_id = user.get("customer_id", "CUS_GUEST")
    full_name = user.get("full_name", "User")
    email = user.get("email", "user@example.com")
    is_active = user.get("is_active", True)
    created_at = user.get("created_at", "N/A")
    last_login = user.get("last_login", "N/A")

    st.markdown(
        f'<div class="page-header"><div class="icon-badge">{icon("user", 19)}</div>'
        f'<div class="page-header-text"><div class="page-title">User Profile</div>'
        f'<div class="page-caption">Manage your account information, Customer ID details, and credentials.</div></div></div>',
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2 = st.columns([1.2, 1], gap="large")

    # Left column: a read-only card showing account details, plus a form to change the display name.
    with col1:
        st.markdown(f'<div class="section-heading">{icon("documents", 16)}Account Details</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="info-card" style="margin-bottom: 20px;">
                <div style="display:flex;align-items:center;gap:.65rem;margin-bottom:.9rem">
                    <div class="avatar">{html.escape((full_name.strip()[:1] or "U").upper())}</div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: var(--text);">{html.escape(full_name)}</div>
                </div>
                <div class="info-row">{icon("mail", 14)}Email:&nbsp;<strong>{html.escape(email)}</strong></div>
                <div class="info-row">{icon("key", 14)}Customer ID:&nbsp;<span class="header-badge">{html.escape(customer_id)}</span></div>
                <div class="info-row">{icon("check-circle", 14)}Account Status:&nbsp;<strong style="color:var(--success)">Active</strong></div>
                <div class="info-row">{icon("clock", 14)}Member Since:&nbsp;<strong>{html.escape(str(created_at))}</strong></div>
                <div class="info-row">{icon("clock", 14)}Last Login:&nbsp;<strong>{html.escape(str(last_login))}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # On submit: save the new name to the database and update session state so the new name shows up immediately.
        with st.form("edit_name_form"):
            st.markdown("#### Edit Display Name")
            new_name = st.text_input("Full Name", value=full_name)
            submit_name = st.form_submit_button("Update Name", type="primary", icon=":material/save:")

            if submit_name:
                clean_n = new_name.strip()
                if not clean_n:
                    st.warning("Full name cannot be empty.")
                else:
                    update_user_profile(user_id, clean_n)
                    st.session_state.current_user["full_name"] = clean_n
                    st.success("Profile updated successfully!")
                    st.rerun()

    # Right column: change-password form, checking the current password before accepting a new one.
    with col2:
        st.markdown(f'<div class="section-heading">{icon("lock", 16)}Security &amp; Password</div>', unsafe_allow_html=True)
        with st.form("change_password_form"):
            st.markdown("#### Change Password")
            old_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password (Min 8 chars)", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            submit_pass = st.form_submit_button("Update Password", type="primary", icon=":material/lock_reset:")

            # Validate in order: all fields filled, current password correct, new password long enough, and the two new entries match.
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
                    # All checks passed: hash the new password and save it, then update session state to match.
                    new_hash = hash_password(new_pass)
                    update_user_password(user_id, new_hash)
                    st.session_state.current_user["password_hash"] = new_hash
                    st.success("Password changed successfully!")
                    st.rerun()

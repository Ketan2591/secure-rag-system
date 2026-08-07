import streamlit as st

def load_styles():
    st.markdown(
        """
<style>
/* Modern Font Family */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* App Background */
.stApp {
    background: #090d16;
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.10) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(139, 92, 246, 0.08) 0px, transparent 50%);
    color: #f8fafc;
}

/* Fix Streamlit top header clipping */
header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 100 !important;
}

.block-container {
    max-width: 1400px;
    padding-top: 2.5rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
}

/* SIDEBAR STYLING */
[data-testid="stSidebar"] {
    background: #060911 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #94a3b8 !important;
}

.sidebar-brand {
    padding: 12px 6px;
    margin-bottom: 12px;
}

.brand-title {
    color: #ffffff !important;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.brand-subtitle {
    color: #6366f1 !important;
    font-size: 11px;
    font-weight: 700;
    margin-top: 1px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.sidebar-user-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 15px;
}

.user-name {
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 700;
}

.user-id {
    color: #818cf8 !important;
    font-size: 11px;
    font-weight: 600;
    margin-top: 2px;
    font-family: monospace;
}

.sidebar-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.07);
    margin: 16px 0;
}

/* HERO BANNER & DASHBOARD HEADER */
.dashboard-header {
    background: linear-gradient(135deg, #111827 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    position: relative;
    overflow: hidden;
}

.dashboard-header::after {
    content: "";
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, transparent 70%);
    pointer-events: none;
}

.header-welcome {
    color: #94a3b8 !important;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}

.header-name {
    color: #ffffff !important;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.header-meta {
    display: flex;
    gap: 16px;
    margin-top: 10px;
    font-size: 12px;
    color: #cbd5e1;
}

.header-badge {
    background: rgba(99, 102, 241, 0.2);
    border: 1px solid rgba(99, 102, 241, 0.4);
    color: #c7d2fe !important;
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 700;
    font-family: monospace;
}

/* STAT CARDS */
.stat-card {
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transition: all 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.4);
}

.stat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stat-label {
    color: #94a3b8 !important;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.stat-value {
    color: #ffffff !important;
    font-size: 26px;
    font-weight: 800;
    margin-top: 8px;
}

.stat-subtitle {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 4px;
}

/* BUTTON STYLING */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
}

button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.55) !important;
    transform: translateY(-1px);
}

/* CARDS & EXPANDERS */
[data-testid="stExpander"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
}

.document-row {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.doc-name {
    color: #f8fafc !important;
    font-weight: 700;
    font-size: 14px;
}

.doc-meta {
    color: #94a3b8 !important;
    font-size: 11px;
    margin-top: 3px;
}

/* CHAT STYLING */
[data-testid="stChatMessage"] {
    background: rgba(15, 23, 42, 0.65) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li {
    color: #f1f5f9 !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(79, 70, 229, 0.15) !important;
    border-color: rgba(99, 102, 241, 0.3) !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(16, 185, 129, 0.08) !important;
    border-color: rgba(16, 185, 129, 0.25) !important;
}

.history-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 14px;
}

.history-question {
    color: #818cf8 !important;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 8px;
}

.history-answer {
    color: #e2e8f0 !important;
    font-size: 13px;
    line-height: 1.6;
}

.history-time {
    color: #64748b !important;
    font-size: 10px;
    margin-top: 8px;
}

.source-card {
    background: rgba(99, 102, 241, 0.1);
    border-left: 3px solid #6366f1;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 6px 0;
    color: #cbd5e1 !important;
    font-size: 11px;
}

/* FOOTER */
.app-footer {
    text-align: center;
    color: #64748b !important;
    font-size: 11px;
    margin-top: 35px;
    padding-top: 15px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

footer, #MainMenu {
    visibility: hidden;
}
</style>
""",
        unsafe_allow_html=True,
    )
import html
import streamlit as st

from src.config import (
    ACTIVE_LLM_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    VECTOR_DB_PROVIDER,
)
from src.database import get_db_type
from src.pages.icons import icon


# Renders the read-only "Settings" page: static info cards about the PII masking engine and tenant isolation on the
# left, and the LLM provider picker plus live system/database status on the right.
def show_settings():
    st.markdown(
        f'<div class="page-header"><div class="icon-badge">{icon("settings", 19)}</div>'
        f'<div class="page-header-text"><div class="page-title">SecureRAG System Settings</div>'
        f'<div class="page-caption">View and configure PII security rules, vector store parameters, and AI models.</div></div></div>',
        unsafe_allow_html=True,
    )

    st.write("")

    active_db = get_db_type()

    col1, col2 = st.columns(2, gap="large")

    # Left column: static explainer cards about how PII masking and multi-tenant isolation work. Nothing here is interactive.
    with col1:
        st.markdown(f'<div class="section-heading">{icon("shield-check", 16)}PII Masking Engine</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="info-card" style="margin-bottom: 16px;">
                <div class="info-title">Microsoft Presidio + spaCy NLP + Custom Regex</div>
                <div class="info-body">
                    Scans all document uploads prior to vector embedding generation. Masked entities are replaced with protected placeholders:
                    <br><br>
                    <code>&lt;PERSON&gt;</code> &nbsp;<code>&lt;EMAIL_ADDRESS&gt;</code> &nbsp;<code>&lt;PHONE_NUMBER&gt;</code><br>
                    <code>&lt;PASSWORD&gt;</code> &nbsp;<code>&lt;CLIENT_ID&gt;</code> &nbsp;<code>&lt;CREDIT_CARD&gt;</code><br>
                    <code>&lt;API_KEY&gt;</code> &nbsp;<code>&lt;BANK_ACCOUNT&gt;</code> &nbsp;<code>&lt;AADHAAR&gt;</code> &nbsp;<code>&lt;PAN&gt;</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="section-heading">{icon("lock", 16)}Multi-Tenant Data Isolation</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Metadata Filter Isolation</div>
                <div class="info-body">
                    Every document chunk indexed carries an authenticated <code>customer_id</code> metadata tag. Queries are filtered strictly at the vector database engine to prevent cross-tenant data leakage.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Right column: the actual working controls, letting the user pick a preferred LLM provider, plus a live
    # readout of which APIs/database are currently connected.
    with col2:
        st.markdown(f'<div class="section-heading">{icon("shield", 16)}Dynamic AI Model &amp; LLM Provider Engine</div>', unsafe_allow_html=True)

        # Dropdown to choose which LLM provider strategy answer_question should prefer.
        # Options are built from the actual configured model names (src/config.py) so this
        # never drifts out of sync with what get_llm_candidates() really uses.
        llm_option = st.selectbox(
            "Select Preferred AI Provider Strategy:",
            [
                f"Auto Fallback Engine ({GROQ_MODEL} -> {GEMINI_MODEL} -> openai/gpt-oss-20b -> qwen/qwen3.8-27b)",
                f"Groq Primary ({GROQ_MODEL})",
                f"Google Gemini ({GEMINI_MODEL})",
            ],
            index=0,
        )

        # Store the chosen strategy in session state so answer_question() picks it up as preferred_provider.
        if "Auto" in llm_option:
            st.session_state.preferred_provider = "auto"
        elif "Groq" in llm_option:
            st.session_state.preferred_provider = "groq"
        else:
            st.session_state.preferred_provider = "gemini"

        # Live status card: shows which LLM/vector providers are actually configured right now, straight from config.py.
        groq_status = "Connected" if GROQ_API_KEY else "Missing API Key"
        gemini_status = "Connected" if GEMINI_API_KEY else "Missing API Key"
        pinecone_status = "Active" if PINECONE_API_KEY else "Using ChromaDB Fallback"

        st.markdown(
            f"""
            <div class="info-card" style="margin-bottom: 16px;">
                <div class="info-title">Active System Configuration</div>
                <div class="info-row"><strong>Groq API:</strong>&nbsp;{groq_status} ({html.escape(GROQ_MODEL)})</div>
                <div class="info-row"><strong>Gemini API:</strong>&nbsp;{gemini_status} ({html.escape(GEMINI_MODEL)})</div>
                <div class="info-row"><strong>Vector DB:</strong>&nbsp;Pinecone / ChromaDB ({pinecone_status})</div>
                <div class="info-row"><strong>Embeddings:</strong>&nbsp;sentence-transformers/all-MiniLM-L6-v2</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Shows which database engine (SQLite or Postgres) is actually active for this deployment.
        st.markdown(f'<div class="section-heading">{icon("documents", 16)}Relational Database Storage</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-title"><span>{html.escape(active_db)} Database</span>
                    <span class="badge-pill success">{icon("check-circle", 11)}&nbsp;Active</span>
                </div>
                <div class="info-body">
                    Stores user account credentials, bcrypt password hashes, Customer IDs, document upload metadata, and persistent Q&amp;A audit history.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

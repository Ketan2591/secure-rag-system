import streamlit as st
import html
from src.database import get_db_type

def show_settings():
    st.markdown("## ⚙️ SecureRAG System Settings")
    st.caption("View and configure security rules, vector store parameters, and model options.")

    st.write("")

    active_db = get_db_type()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### 🛡️ PII Masking Engine")
        st.markdown(
            """
            <div class="stat-card" style="margin-bottom: 16px;">
                <div style="font-weight: 700; color: #ffffff; font-size: 15px; margin-bottom: 8px;">
                    Microsoft Presidio + spaCy NLP
                </div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.6;">
                    All documents are scanned for sensitive personal data prior to vector embedding generation. Masked entities are replaced with protected placeholders:
                    <br><br>
                    • <code>&lt;PERSON&gt;</code> • <code>&lt;EMAIL_ADDRESS&gt;</code> • <code>&lt;PHONE_NUMBER&gt;</code><br>
                    • <code>&lt;CREDIT_CARD&gt;</code> • <code>&lt;SSN&gt;</code> • <code>&lt;IP_ADDRESS&gt;</code><br>
                    • <code>&lt;API_KEY&gt;</code> • <code>&lt;BANK_ACCOUNT&gt;</code> • <code>&lt;AADHAAR_NUMBER&gt;</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🔒 Multi-Tenant Isolation")
        st.markdown(
            """
            <div class="stat-card">
                <div style="font-weight: 700; color: #ffffff; font-size: 15px; margin-bottom: 8px;">
                    Metadata Filter Isolation
                </div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.6;">
                    Every ChromaDB chunk stored carries a <code>customer_id</code> metadata tag. Queries are filtered strictly at the vector database retrieval stage to guarantee data boundary enforcement.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("### 🧠 AI Engine & Vector Store")
        st.markdown(
            """
            <div class="stat-card" style="margin-bottom: 16px;">
                <div style="font-weight: 700; color: #ffffff; font-size: 15px; margin-bottom: 8px;">
                    Groq LLM + Local HuggingFace Embeddings
                </div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.6;">
                    <strong>LLM Model:</strong> llama-3.3-70b-versatile<br>
                    <strong>Provider:</strong> Groq API<br>
                    <strong>Vector DB:</strong> ChromaDB (Local Persistent Storage)<br>
                    <strong>Embeddings:</strong> sentence-transformers/all-MiniLM-L6-v2
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🗄️ Database Backend")
        st.markdown(
            f"""
            <div class="stat-card">
                <div style="font-weight: 700; color: #ffffff; font-size: 15px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <span>{html.escape(active_db)}</span>
                    <span style="background: rgba(74, 222, 128, 0.15); border: 1px solid rgba(74, 222, 128, 0.3); color: #4ade80; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">
                        🟢 Active
                    </span>
                </div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.6;">
                    Persists user accounts, bcrypt hashed passwords, uploaded document records, and Q&A chat history with strict relational integrity.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

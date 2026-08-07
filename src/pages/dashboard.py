import html
import streamlit as st
from src.database import (
    get_user_document_count,
    get_user_chat_count,
    get_user_documents,
    get_user_chat_history,
    soft_delete_chat_message,
    reset_customer_workspace,
)
from src.rag_pipeline import ingest_document, answer_question

def show_dashboard():
    user = st.session_state.get("current_user") or {}
    customer_id = user.get("customer_id", "CUS_GUEST")
    full_name = user.get("full_name", "Valued User")
    last_login = user.get("last_login") or "First Session"

    doc_count = get_user_document_count(customer_id)
    chat_count = get_user_chat_count(customer_id)

    # Top Welcome Banner
    st.markdown(
        f"""
        <div class="dashboard-header">
            <div class="header-welcome">👋 Welcome Back</div>
            <div class="header-name">{html.escape(full_name)}</div>
            <div class="header-meta">
                <span>Customer ID: <span class="header-badge">{html.escape(customer_id)}</span></span>
                <span>•</span>
                <span>Last Login: <strong>{html.escape(str(last_login))}</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Quick Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">📄 Documents</span>
                    <span>📂</span>
                </div>
                <div class="stat-value">{doc_count}</div>
                <div class="stat-subtitle">Indexed in Database</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">💬 Total Chats</span>
                    <span>🗨️</span>
                </div>
                <div class="stat-value">{chat_count}</div>
                <div class="stat-subtitle">Q&A Interactions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">🛡️ PII Security</span>
                    <span>🟢</span>
                </div>
                <div class="stat-value" style="color: #4ade80 !important;">Active</div>
                <div class="stat-subtitle">Presidio + spaCy Masking</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-label">🔒 Workspace</span>
                    <span>🔐</span>
                </div>
                <div class="stat-value" style="color: #818cf8 !important;">Isolated</div>
                <div class="stat-subtitle">Tenant Filter Enabled</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # Fetch active non-deleted user documents for selector
    db_docs = get_user_documents(customer_id)
    doc_options = ["🌐 All Workspace Documents"] + [d.get("filename") for d in db_docs if d.get("filename")]

    # Split: Document Workspace & Chat Workspace
    doc_col, chat_col = st.columns([1, 1.15], gap="large")

    with doc_col:
        st.markdown("### 📄 Document Workspace")
        st.caption("Upload PDF, DOCX or TXT documents to index into your secure workspace.")

        uploaded_files = st.file_uploader(
            "Upload files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="dash_uploader",
        )

        if uploaded_files:
            c_html = "".join([f'<span class="file-chip">📄 {html.escape(f.name)}</span>' for f in uploaded_files])
            st.markdown(c_html, unsafe_allow_html=True)

        if st.button("🔐 Process & Index Documents", type="primary", use_container_width=True, key="dash_process_btn"):
            if not uploaded_files:
                st.warning("Please select at least one file to upload.")
            else:
                progress = st.progress(0)
                status = st.empty()
                success_count = 0
                first_new_filename = uploaded_files[0].name

                for idx, file_obj in enumerate(uploaded_files):
                    status.info(f"Ingesting & anonymizing {file_obj.name}...")
                    file_obj.seek(0)
                    ingest_document(file=file_obj, filename=file_obj.name, user_id=customer_id)
                    success_count += 1
                    progress.progress((idx + 1) / len(uploaded_files))
                
                status.empty()
                progress.empty()

                # Automatically focus query target to newly uploaded document!
                st.session_state.selected_target_doc = first_new_filename
                st.success(f"✅ Indexed {success_count} document(s)! Focused chat target to '{first_new_filename}'.")
                st.rerun()

        st.write("")
        d_title_col, d_reset_col = st.columns([2.5, 1.5])
        with d_title_col:
            st.markdown("#### 📚 Your Indexed Documents")
        with d_reset_col:
            if db_docs or chat_count > 0:
                if st.button("🧹 Reset Data", key="dash_reset_data_btn", help="Soft-delete current test documents & chats for a fresh workspace"):
                    reset_customer_workspace(customer_id)
                    if "selected_target_doc" in st.session_state:
                        del st.session_state["selected_target_doc"]
                    st.success("Workspace reset! Ready for new documents.")
                    st.rerun()

        if db_docs:
            for d in db_docs[:5]:  # Show top 5
                fname = html.escape(str(d.get("filename", "Document")))
                pages = d.get("pages_processed", 0)
                chunks = d.get("chunks_stored", 0)
                st.markdown(
                    f"""
                    <div class="document-row">
                        <div>
                            <div class="doc-name">📄 {fname}</div>
                            <div class="doc-meta">Pages: {pages} • Chunks: {chunks} • Verified Masked</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if len(db_docs) > 5:
                if st.button("View All Documents ➔", key="dash_goto_docs"):
                    st.session_state.page = "documents"
                    st.rerun()
        else:
            st.info("No active documents in workspace.")

    with chat_col:
        st.markdown("### 💬 Secure Document Assistant")

        # Document Selection Dropdown (No need to re-upload!)
        st.markdown("<div style='font-size:12px; font-weight:700; color:#c7d2fe; margin-bottom:4px;'>📌 Select Active Document for Questions (No re-upload needed!):</div>", unsafe_allow_html=True)
        
        default_index = 0
        if "selected_target_doc" in st.session_state and st.session_state.selected_target_doc in doc_options:
            default_index = doc_options.index(st.session_state.selected_target_doc)

        selected_doc = st.selectbox(
            "Select Document for Chat",
            options=doc_options,
            index=default_index,
            key="active_target_doc_selector",
            label_visibility="collapsed",
        )
        st.session_state.selected_target_doc = selected_doc

        clean_doc_target = None if selected_doc == "🌐 All Workspace Documents" else selected_doc

        # Load non-deleted history for selected document from DB
        all_history = get_user_chat_history(customer_id, include_deleted=False)
        
        if clean_doc_target:
            target_history = [
                h for h in all_history
                if any(s.get("source") == clean_doc_target for s in h.get("sources", []))
            ]
        else:
            target_history = all_history

        # Display Live Q&A Chat Container with timestamps & delete button
        chat_container = st.container(height=380)
        with chat_container:
            if not target_history:
                st.info(f"👋 No previous questions found for '{selected_doc}'. Type a question below to start!")
            else:
                for item in target_history:
                    user_q = item.get("user_message", "")
                    assistant_a = item.get("assistant_response", "")
                    timestamp_str = item.get("created_at", "")
                    sources = item.get("sources") or []
                    chat_id = item.get("id")

                    with st.chat_message("user"):
                        q_col1, q_col2 = st.columns([8.8, 1.2])
                        with q_col1:
                            st.markdown(user_q)
                            if timestamp_str:
                                st.markdown(f"<div style='font-size:10px; color:#64748b; margin-top:2px;'>📅 {timestamp_str}</div>", unsafe_allow_html=True)
                        with q_col2:
                            if chat_id and st.button("🗑️", key=f"del_chat_dash_{chat_id}", help="Delete Question (Saved in DB for Audit)"):
                                soft_delete_chat_message(chat_id, customer_id)
                                st.rerun()

                    with st.chat_message("assistant"):
                        st.markdown(assistant_a)

                        # Extract page numbers for right-aligned badge
                        pages_list = sorted(list({str(s.get("page", "-")) for s in sources if s.get("page") is not None}))
                        pages_text = ", ".join(pages_list) if pages_list else "-"

                        meta_col1, meta_col2 = st.columns([1, 1])
                        with meta_col1:
                            if timestamp_str:
                                st.markdown(f"<div style='font-size:10px; color:#64748b; margin-top:4px;'>📅 {timestamp_str}</div>", unsafe_allow_html=True)
                        with meta_col2:
                            if sources:
                                st.markdown(
                                    f"""
                                    <div style="text-align: right; margin-top: 2px;">
                                        <span style="background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.45); color: #c7d2fe; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 8px; display: inline-block;">
                                            📌 Page Number: {pages_text}
                                        </span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                        if sources:
                            with st.expander("📎 View Document Sources"):
                                for src in sources:
                                    s_name = html.escape(str(src.get("source", "Unknown")))
                                    s_page = html.escape(str(src.get("page", "-")))
                                    st.markdown(f'<div class="source-card">📄 <strong>{s_name}</strong> • <strong>Page {s_page}</strong></div>', unsafe_allow_html=True)

        question = st.chat_input("Ask a question about selected document...", key="dash_chat_input")
        if question:
            q_clean = question.strip()
            if q_clean:
                with st.spinner(f"Searching context in '{selected_doc}' & querying Groq..."):
                    answer_question(
                        question=q_clean,
                        user_id=customer_id,
                        doc_name=clean_doc_target,
                    )
                st.rerun()
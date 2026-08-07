import html
import streamlit as st
from src.database import get_user_documents, delete_user_document
from src.rag_pipeline import ingest_document

def show_documents():
    user = st.session_state.get("current_user") or {}
    customer_id = user.get("customer_id", "CUS_GUEST")

    st.markdown("## 📄 My Documents Workspace")
    st.caption("Manage your uploaded files, process new documents, and review vector store indexing.")

    st.write("")

    # Upload Section
    with st.expander("➕ Upload & Index New Documents", expanded=True):
        uploaded_files = st.file_uploader(
            "Select PDF, DOCX or TXT files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="docs_page_uploader",
        )

        if uploaded_files:
            c_html = "".join([f'<span class="file-chip">📄 {html.escape(f.name)}</span>' for f in uploaded_files])
            st.markdown(c_html, unsafe_allow_html=True)

        if st.button("🔐 Process & Anonymize Documents", type="primary", use_container_width=True, key="docs_page_process"):
            if not uploaded_files:
                st.warning("Please select at least one file to upload.")
            else:
                progress = st.progress(0)
                status = st.empty()
                success_count = 0
                for idx, file_obj in enumerate(uploaded_files):
                    status.info(f"Ingesting & anonymizing {file_obj.name}...")
                    file_obj.seek(0)
                    ingest_document(file=file_obj, filename=file_obj.name, user_id=customer_id)
                    success_count += 1
                    progress.progress((idx + 1) / len(uploaded_files))
                status.empty()
                progress.empty()

                # REQUIREMENT 1: Reset active chat screen on new document upload!
                st.session_state.active_chat_messages = []

                st.success(f"✅ Successfully indexed {success_count} document(s)! Chat window has been reset for new questions.")
                st.rerun()

    st.write("")
    st.markdown("### 📚 Indexed Documents List")

    db_docs = get_user_documents(customer_id)
    if not db_docs:
        st.info("No documents found in your database workspace.")
    else:
        for doc in db_docs:
            doc_id = doc.get("id")
            fname = html.escape(str(doc.get("filename", "Document")))
            pages = doc.get("pages_processed", 0)
            chunks = doc.get("chunks_stored", 0)
            uploaded_at = doc.get("uploaded_at", "-")

            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f"""
                    <div class="document-row">
                        <div>
                            <div class="doc-name">📄 {fname}</div>
                            <div class="doc-meta">Pages: {pages} • Chunks: {chunks} • Uploaded: {uploaded_at} • Status: <span style="color:#4ade80;">✓ Masked & Indexed</span></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                st.write("")
                if st.button("🗑️ Delete", key=f"del_doc_{doc_id}", use_container_width=True):
                    raw_filename = doc.get("filename")
                    delete_user_document(doc_id, customer_id)
                    try:
                        from src.vector_store import delete_documents_by_filename
                        delete_documents_by_filename(raw_filename, customer_id)
                    except Exception:
                        pass
                    if "selected_target_doc" in st.session_state and st.session_state.selected_target_doc == raw_filename:
                        st.session_state.selected_target_doc = "🌐 All Workspace Documents"
                    st.success(f"Archived '{fname}' from active workspace. Document & chat history remain 100% preserved in Database for safety.")
                    st.rerun()

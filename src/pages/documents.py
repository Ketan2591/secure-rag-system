import html
import streamlit as st

from src.database import delete_user_document, get_user_documents
from src.pages.icons import icon
from src.rag_pipeline import ingest_document


# Guesses a document's type (pdf, docx, or txt) from its filename extension, used to pick the right icon/tag in the list below.
def _file_kind(name: str) -> str:
    lower = name.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".docx") or lower.endswith(".doc"):
        return "docx"
    return "txt"


# Renders the "My Documents" page: an upload/index section at the top and the full list of a customer's indexed documents below it,
# each with a delete button that removes it from both the database and the vector store.
def show_documents():
    user = st.session_state.get("current_user") or {}
    customer_id = user.get("customer_id", "CUS_GUEST")

    st.markdown(
        f'<div class="page-header"><div class="icon-badge">{icon("folder", 19)}</div>'
        f'<div class="page-header-text"><div class="page-title">My Documents Workspace</div>'
        f'<div class="page-caption">Manage your uploaded files, process new documents, and review vector store indexing.</div></div></div>',
        unsafe_allow_html=True,
    )

    st.write("")

    # Upload & Index panel: pick files, then process each one on button click, tracking successes and duplicates separately.
    with st.expander("Upload & Index New Documents", icon=":material/cloud_upload:", expanded=True):
        uploaded_files = st.file_uploader(
            "Select PDF, DOCX or TXT files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="docs_page_uploader",
        )

        if st.button("Process & Anonymize Documents", type="primary", icon=":material/bolt:", use_container_width=True, key="docs_page_process"):
            if not uploaded_files:
                st.warning("Please select at least one file to upload.")
            else:
                # Ingest each selected file one by one, updating a progress bar and collecting outcomes to summarize afterward.
                progress = st.progress(0)
                status = st.empty()
                success_count = 0
                already_exists_names = []

                for idx, file_obj in enumerate(uploaded_files):
                    status.info(f"Ingesting & anonymizing {file_obj.name}...")
                    file_obj.seek(0)
                    try:
                        res = ingest_document(file=file_obj, filename=file_obj.name, user_id=customer_id)
                        if res.get("status") == "already_exists":
                            already_exists_names.append(file_obj.name)
                        else:
                            success_count += 1
                    except Exception as e:
                        st.error(f"Error processing {file_obj.name}: {e}")

                    progress.progress((idx + 1) / len(uploaded_files))

                status.empty()
                progress.empty()

                # Show a summary: which files were duplicates and how many new ones were successfully indexed.
                if already_exists_names:
                    names_str = ", ".join([f"'{n}'" for n in already_exists_names])
                    st.warning(f"{names_str} is already processed and indexed in your workspace.")

                if success_count > 0:
                    st.success(f"Successfully indexed {success_count} new document(s)!")

                st.rerun()

    st.write("")
    st.markdown(f'<div class="section-heading">{icon("documents", 16)}Indexed Documents List</div>', unsafe_allow_html=True)

    # List every active document for this customer, each row showing its name, page/chunk counts, upload date, and a delete button.
    db_docs = get_user_documents(customer_id)
    if not db_docs:
        st.info("No documents found in your workspace database. Upload a file above to start!")
    else:
        for doc in db_docs:
            doc_id = doc.get("id")
            fname = html.escape(str(doc.get("filename", "Document")))
            pages = doc.get("pages_processed", 1)
            chunks = doc.get("chunks_stored", 1)
            uploaded_at = doc.get("uploaded_at", "-")
            file_kind = _file_kind(str(doc.get("filename", "")))

            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f"""
                    <div class="doc-row-flat">
                        <div class="doc-title">
                            <span class="doc-file {file_kind}">{icon("file", 16)}</span>
                            <span>
                                <strong>{fname}</strong>
                                <small><span class="doc-tag">{file_kind.upper()}</span>&nbsp;Pages: {pages} • Chunks: {chunks} • Uploaded: {uploaded_at}
                                &nbsp;•&nbsp;<span class="doc-status">{icon("check-circle", 11)}&nbsp;Masked &amp; Indexed</span></small>
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                st.write("")
                # On delete: soft-delete the document row in the database, then also try to purge its chunks from the vector store.
                if st.button("Delete", icon=":material/delete:", key=f"del_doc_{doc_id}", use_container_width=True):
                    raw_filename = doc.get("filename")
                    if doc_id is not None:
                        delete_user_document(doc_id, customer_id)
                    try:
                        from src.vector_store import delete_documents_by_filename
                        if raw_filename:
                            delete_documents_by_filename(raw_filename, customer_id)
                    except Exception:
                        pass
                    st.success(f"Deleted '{fname}' from active workspace.")
                    st.rerun()

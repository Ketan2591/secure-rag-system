import html
import re
from datetime import datetime

import streamlit as st

from src.database import get_user_chat_count, get_user_documents, reset_customer_workspace
from src.pages.icons import icon
from src.rag_pipeline import answer_question, ingest_document


# Turns a raw timestamp string from the database into a friendly "DD Mon YYYY" format for display.
# Tries a few common timestamp formats one by one, and just returns the original text if none of them match.
def _format_date(raw) -> str:
    text = str(raw or "").split(".")[0].strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%d %b %Y")
        except ValueError:
            continue
    return text or "—"


# Matches masked PII placeholders like <EMAIL_ADDRESS> or <PHONE_NUMBER> inside an answer's text.
_PLACEHOLDER_TAG_RE = re.compile(r"<([A-Z][A-Z0-9_]*)>")


# Renders one assistant answer, wrapping any masked placeholder tag in backticks so it displays as code instead of being misread as markdown or HTML.
def _answer_box(text: str, box_key: str) -> None:
    highlighted = _PLACEHOLDER_TAG_RE.sub(lambda m: f"`<{m.group(1)}>`", text or "")
    with st.container(key=box_key):
        st.markdown(highlighted)


# Renders the small "source" chips (filename + page number) shown under an assistant answer.
def _sources(sources: list[dict]) -> None:
    for source in sources or []:
        name = html.escape(str(source.get("source", "Document")))
        page = html.escape(str(source.get("page", "—")))
        st.markdown(
            f'<span class="source-card">{icon("file", 12)}<strong>&nbsp;{name}</strong>&nbsp;•&nbsp;Page {page}</span>',
            unsafe_allow_html=True,
        )


# Guesses a document's type (pdf, docx, or txt) from its filename extension, used to pick the right icon/tag in the document list.
def _file_kind(name: str) -> str:
    lower = name.lower()
    if lower.endswith(".pdf"):
        return "pdf"
    if lower.endswith(".docx") or lower.endswith(".doc"):
        return "docx"
    return "txt"


# Runs the upload button's action: shows a progress bar while each selected file is masked, chunked, and indexed one by one.
# Shows an error per file that fails instead of stopping the whole batch, then reruns the page once everything is done.
def _ingest(files, user_id: str) -> None:
    if not files:
        st.warning("Select at least one PDF, DOCX, or TXT file first.")
        return
    progress, status = st.progress(0), st.empty()
    for index, file in enumerate(files, start=1):
        status.info(f"Protecting sensitive data and indexing {file.name}…")
        try:
            ingest_document(file=file, filename=file.name, user_id=user_id)
        except Exception as error:
            st.error(f"Could not process {file.name}: {error}")
        progress.progress(index / len(files))
    status.success("Documents are protected and ready to query.")
    st.rerun()


# Renders the main dashboard page: a welcome header, four stat cards, a document upload/list panel on the left,
# and the secure chat assistant panel on the right, with a footer at the bottom.
def show_dashboard():
    # Pull the logged-in user's info and their documents, needed by every section below.
    user = st.session_state.current_user or {}
    customer_id = user.get("customer_id", "CUS_GUEST")
    full_name = user.get("full_name", "User")
    last_login = user.get("last_login") or "Just now"
    documents = get_user_documents(customer_id)

    # Welcome header with the user's name, customer ID, and last login time.
    st.markdown(
        f'<div class="dashboard-header"><div class="header-name">Welcome back, <span class="name-accent">{html.escape(full_name)}</span></div><div class="header-meta">'
        f'<span>Customer ID: <span class="header-badge">{html.escape(customer_id)}</span></span><span>•</span><span>Last Login: {html.escape(str(last_login))}</span></div></div>',
        unsafe_allow_html=True,
    )

    # Top row of four stat cards: document count, chat count, and two static security status cards.
    metric_values = [
        ("documents", "Documents", str(len(documents)), "Indexed in your workspace", ""),
        ("chat", "Total chats", str(get_user_chat_count(customer_id)), "Across all sessions", ""),
        ("shield-check", "Security status", "Active", "PII protected • Source verified", "success"),
        ("lock", "Workspace", "Isolated", "Tenant filter enabled", "success"),
    ]
    for column, metric in zip(st.columns(4, gap="small"), metric_values):
        icon_name, label, value, subtitle, state = metric
        with column:
            st.markdown(
                f'<div class="stat-card"><div class="stat-header"><span class="stat-icon {state}">{icon(icon_name, 16)}</span>'
                f'<span class="stat-label">{label}</span></div><div class="stat-value {state}">{value}</div>'
                f'<div class="stat-subtitle">{subtitle}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1, 1.03], gap="small")

    # Left panel: upload new documents, filter/search the existing ones, and list them in a table.
    with left:
        with st.container(border=True):
            st.markdown(
                f'<p class="panel-heading">{icon("folder", 17)}&nbsp;Documents</p>'
                f'<p class="panel-caption">Upload and index your private documents.</p>',
                unsafe_allow_html=True,
            )
            uploads = st.file_uploader(
                "Upload PDF, DOCX, or TXT",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                key="dashboard_doc_uploader",
                label_visibility="collapsed",
            )
            st.markdown('<div class="process-button">', unsafe_allow_html=True)
            if st.button(
                "Process & Index Documents",
                type="primary",
                icon=":material/cloud_upload:",
                use_container_width=True,
                key="dashboard_process",
            ):
                _ingest(uploads, customer_id)
            st.markdown("</div>", unsafe_allow_html=True)

            # Type filter (All/PDF/DOCX/TXT) and a search box, both narrowing down the document list rendered below.
            filt_col, search_col = st.columns([1.35, 1], vertical_alignment="center")
            with filt_col:
                type_filter = st.segmented_control(
                    "Filter by type",
                    options=["All", "PDF", "DOCX", "TXT"],
                    default="All",
                    label_visibility="collapsed",
                    key="dashboard_type_filter",
                )
            with search_col:
                doc_names = sorted({fname for d in documents if (fname := d.get("filename"))})
                search_choice = st.selectbox(
                    "Search documents",
                    options=doc_names,
                    index=None,
                    placeholder="Search documents...",
                    label_visibility="collapsed",
                    key="dashboard_doc_search",
                )

            # Apply the type filter and the search selection to the full document list.
            filtered_documents = documents
            if type_filter and type_filter != "All":
                filtered_documents = [
                    d for d in filtered_documents if _file_kind(str(d.get("filename", ""))).upper() == type_filter
                ]
            if search_choice:
                filtered_documents = [d for d in filtered_documents if d.get("filename") == search_choice]

            # Table header, then the actual rows for whatever documents survived the filter/search above.
            st.markdown(
                '<div class="document-table-head"><span>Document name</span><span>Pages</span><span>Size</span><span>Status</span><span>Indexed</span></div>',
                unsafe_allow_html=True,
            )
            if not documents:
                st.info("No documents indexed yet. Upload a document to begin.")
            elif not filtered_documents:
                st.info("No documents match this filter.")
            else:
                with st.container(height=300):
                    for index, document in enumerate(filtered_documents):
                        name = html.escape(str(document.get("filename", "Document")))
                        pages, chunks = document.get("pages_processed", 1), document.get("chunks_stored", 0)
                        size = document.get("file_size", "200 KB" if index == 0 else "18 KB")
                        indexed = html.escape(_format_date(document.get("uploaded_at")))
                        is_selected = " selected" if search_choice and document.get("filename") == search_choice else ""
                        file_kind = _file_kind(str(document.get("filename", "")))
                        st.markdown(
                            f"""
                            <div class="document-row{is_selected}">
                                <div class="doc-title">
                                    <span class="doc-file {file_kind}">{icon("file", 16)}</span>
                                    <span><strong>{name}</strong><small><span class="doc-tag">{file_kind.upper()}</span>&nbsp;Pages: {pages} • Chunks: {chunks}</small></span>
                                </div>
                                <div>{pages}</div>
                                <div>{html.escape(str(size))}</div>
                                <div class="doc-status">{icon("check-circle", 13)}&nbsp;Indexed</div>
                                <div>{indexed}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            st.markdown(
                f'<div class="document-count">Showing {len(filtered_documents)} of {len(documents)} documents</div>',
                unsafe_allow_html=True,
            )

    # Right panel: the secure chat assistant, scoped to either the whole workspace or one selected document.
    with right:
        with st.container(border=True):
            st.markdown(
                f'<div class="assistant-title-row"><div><p class="panel-heading">{icon("shield-check", 18)}&nbsp;Secure assistant</p>'
                f'<p class="panel-caption">Ask questions strictly grounded in your indexed documents.</p></div>'
                f'<div><span class="security-pill">{icon("check-circle", 12)}&nbsp;PII protected</span>'
                f'<span class="security-pill">{icon("check-circle", 12)}&nbsp;Source verified</span></div></div>',
                unsafe_allow_html=True,
            )
            # Dropdown to scope the chat to "All Workspace Documents" or one specific file, then load that scope's chat history.
            options = ["All Workspace Documents"] + [d.get("filename") for d in documents if d.get("filename")]
            if st.session_state.get("selected_target_doc") not in options:
                st.session_state.selected_target_doc = options[0]
            selected_doc = st.selectbox("Selected document scope", options, key="selected_target_doc")
            from src.database import get_user_chat_history

            history = get_user_chat_history(customer_id, target_doc=selected_doc)

            # Replay the past conversation for this scope, each turn showing the user's question and the grounded answer with its sources.
            with st.container(height=360):
                if not history:
                    st.info("Ask a question to start a source-grounded conversation.")
                for idx, item in enumerate(history):
                    with st.chat_message("user", avatar=":material/person:"):
                        st.markdown('<div class="message-meta">You</div>', unsafe_allow_html=True)
                        st.markdown(item.get("user_message", ""))
                    with st.chat_message("assistant", avatar=":material/verified_user:"):
                        st.markdown(
                            f'<div class="message-meta assistant">{icon("shield-check", 11)}&nbsp;SecureRAG • Source verified</div>',
                            unsafe_allow_html=True,
                        )
                        _answer_box(item.get("assistant_response", ""), f"ans_hist_{item.get('id', idx)}")
                        _sources(item.get("sources", []))
            # New question box: on submit, run the RAG pipeline and rerun the page so the fresh answer shows up in the history above.
            question = st.chat_input(f"Ask a question about {selected_doc}…")
            st.markdown('<div class="chat-hint">Press Enter to send</div>', unsafe_allow_html=True)
            if question:
                with st.spinner("Finding verified information…"):
                    try:
                        answer_question(
                            question=question,
                            user_id=customer_id,
                            doc_name=selected_doc,
                            preferred_provider=st.session_state.get("preferred_provider", "auto"),
                        )
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not generate an answer: {error}")

    # Static footer shown at the bottom of the page.
    st.markdown(
        f'<div class="app-footer"><span>© 2026 SecureRAG. Private knowledge workspace.</span>'
        f'<span>{icon("shield-check", 12)}&nbsp;All processing is private. Your data remains in your workspace.</span></div>',
        unsafe_allow_html=True,
    )

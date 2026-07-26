import html
import streamlit as st

from src.rag_pipeline import ingest_document, answer_question


# Page setup

st.set_page_config(
    page_title="SecureRAG | Private Document Intelligence",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Styling

st.markdown(
    """
<style>

/* GLOBAL */

.stApp {
    background:
        radial-gradient(circle at 88% 8%, rgba(99, 102, 241, 0.10), transparent 24%),
        radial-gradient(circle at 12% 92%, rgba(37, 99, 235, 0.07), transparent 26%),
        #f8fafc;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

[data-testid="stMain"] {
    color: #0f172a;
}

[data-testid="stMain"] p,
[data-testid="stMain"] label {
    color: #334155;
}


/* SIDEBAR */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #071426 0%,
        #0b1b32 52%,
        #0e1d35 100%
    );
    border-right: 1px solid #1e293b;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

[data-testid="stSidebar"] input {
    background: #0b1526 !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}

[data-testid="stSidebar"] input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 1px #6366f1 !important;
}

[data-testid="stSidebar"] input::placeholder {
    color: #64748b !important;
}

.sidebar-brand {
    margin-bottom: 22px;
}

.brand-title {
    color: #ffffff !important;
    font-size: 24px;
    line-height: 1.2;
    font-weight: 850;
    letter-spacing: -0.5px;
}

.brand-subtitle {
    color: #94a3b8 !important;
    font-size: 11px;
    margin-top: 5px;
}

.sidebar-heading {
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 750;
    margin-top: 20px;
    margin-bottom: 10px;
}

.sidebar-divider {
    height: 1px;
    background: #26364d;
    margin: 20px 0;
}

.workspace-active {
    background: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(34, 197, 94, 0.28);
    color: #bbf7d0 !important;
    border-radius: 10px;
    padding: 11px 12px;
    font-size: 12px;
    font-weight: 750;
    margin-top: 10px;
}

.workspace-id {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 500;
    margin-top: 4px;
}

.security-control {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.055);
    border-radius: 11px;
    padding: 11px 12px;
    margin-bottom: 8px;
}

.security-control-title {
    color: #f8fafc !important;
    font-size: 12px;
    font-weight: 750;
}

.security-control-text {
    color: #94a3b8 !important;
    font-size: 10px;
    line-height: 1.45;
    margin-top: 3px;
}

.sidebar-footer {
    color: #64748b !important;
    font-size: 9px;
    line-height: 1.6;
}


/* HERO */

.hero {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(
            125deg,
            #0f172a 0%,
            #172554 38%,
            #1d4ed8 72%,
            #6d28d9 100%
        );
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 22px;
    padding: 31px 34px;
    box-shadow: 0 18px 42px rgba(15, 23, 42, 0.16);
    margin-bottom: 18px;
}

.hero::before {
    content: "";
    position: absolute;
    width: 250px;
    height: 250px;
    right: -80px;
    top: -120px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
}

.hero::after {
    content: "";
    position: absolute;
    width: 150px;
    height: 150px;
    right: 80px;
    bottom: -100px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
}

.hero-badge {
    position: relative;
    z-index: 2;
    display: inline-block;
    padding: 6px 11px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    color: #dbeafe !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.09em;
    margin-bottom: 12px;
}

.hero-title {
    position: relative;
    z-index: 2;
    color: #ffffff !important;
    font-size: 34px;
    font-weight: 850;
    line-height: 1.15;
    letter-spacing: -0.8px;
}

.hero-text {
    position: relative;
    z-index: 2;
    color: #dbeafe !important;
    max-width: 820px;
    font-size: 13px;
    line-height: 1.65;
    margin-top: 9px;
}


/* STATUS CARDS */

.status-card {
    background: rgba(255, 255, 255, 0.97);
    border: 1px solid #e2e8f0;
    border-radius: 15px;
    padding: 16px 17px;
    min-height: 105px;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.055);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.status-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.09);
}

.status-label {
    color: #64748b !important;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

.status-value {
    color: #0f172a !important;
    font-size: 18px;
    font-weight: 850;
    margin-top: 7px;
}

.status-green {
    color: #16a34a !important;
}

.status-indigo {
    color: #4f46e5 !important;
}

.status-subtitle {
    color: #64748b !important;
    font-size: 10px;
    margin-top: 4px;
}


/* SECTION HEADERS */

.section-header {
    margin-top: 5px;
    margin-bottom: 14px;
}

.section-title {
    color: #0f172a !important;
    font-size: 20px;
    line-height: 1.3;
    font-weight: 850;
}

.section-description {
    color: #64748b !important;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 4px;
}


/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background: transparent !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border: 1.5px dashed #a5b4fc !important;
    border-radius: 14px !important;
    min-height: 130px;
    transition: 0.18s ease;
}

[data-testid="stFileUploaderDropzone"]:hover {
    background: #f8faff !important;
    border-color: #6366f1 !important;
}

[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    color: #475569 !important;
}

.file-chip {
    display: inline-block;
    background: #eef2ff;
    color: #3730a3 !important;
    border: 1px solid #c7d2fe;
    border-radius: 999px;
    padding: 6px 10px;
    margin: 4px 4px 4px 0;
    font-size: 10px;
    font-weight: 700;
}


/* BUTTONS */

.stButton > button {
    min-height: 42px;
    border-radius: 10px;
    font-weight: 700;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 7px 16px rgba(15, 23, 42, 0.10);
}

button[kind="primary"] {
    color: #ffffff !important;
    background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
    border: none !important;
}

button[kind="primary"] p {
    color: #ffffff !important;
}


/* SUCCESS / INFORMATION */

.processing-success {
    background: #f0fdf4;
    color: #166534 !important;
    border: 1px solid #bbf7d0;
    border-radius: 11px;
    padding: 11px 13px;
    font-size: 11px;
    line-height: 1.6;
    margin: 10px 0;
}

.empty-state {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1e40af !important;
    border-radius: 12px;
    padding: 13px 14px;
    font-size: 11px;
}


/* EXPANDERS */

[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    background: #ffffff !important;
    color: #0f172a !important;
}

[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #0f172a !important;
    font-weight: 700 !important;
}

[data-testid="stExpander"] summary:hover {
    background: #f8fafc !important;
}

[data-testid="stExpander"] summary:hover p,
[data-testid="stExpander"] summary:hover span {
    color: #4338ca !important;
}

[data-testid="stExpander"] details > div {
    background: #ffffff !important;
    color: #334155 !important;
}

[data-testid="stExpander"] details > div p {
    color: #334155 !important;
}


/* DOCUMENTS */

.document-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 11px 12px;
    margin: 6px 0;
}

.document-name {
    color: #0f172a !important;
    font-size: 12px;
    font-weight: 750;
}

.document-meta {
    color: #64748b !important;
    font-size: 10px;
    margin-top: 4px;
}


/* CHAT */

[data-testid="stChatMessage"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 10px 13px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 3px 12px rgba(15, 23, 42, 0.035);
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] code {
    color: #0f172a !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #eff6ff !important;
    border-color: #bfdbfe !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #f0fdf4 !important;
    border-color: #bbf7d0 !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p {
    color: #14532d !important;
}

[data-testid="stChatInput"] {
    background: #1e293b !important;
    border: 1px solid #6366f1 !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    caret-color: #a78bfa !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
    opacity: 1 !important;
}


/* SOURCE CARDS */

.source-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #6366f1;
    border-radius: 9px;
    padding: 9px 11px;
    margin: 6px 0;
    color: #334155 !important;
    font-size: 11px;
}

.source-card strong {
    color: #0f172a !important;
}


/* STREAMLIT ALERTS */

[data-testid="stAlert"] {
    border-radius: 11px !important;
}

[data-testid="stAlert"] p {
    color: inherit !important;
}


/* FOOTER */

.app-footer {
    text-align: center;
    color: #94a3b8 !important;
    font-size: 9px;
    padding-top: 20px;
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}


/* RESPONSIVE */

@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 25px;
    }

    .hero-title {
        font-size: 27px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# Session variables


if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_user" not in st.session_state:
    st.session_state.active_user = ""


# Sidebar

with st.sidebar:

    st.markdown(
        """<div class="sidebar-brand">
<div class="brand-title">🔐 SecureRAG</div>
<div class="brand-subtitle">Private Document Intelligence</div>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<div class="sidebar-heading">👤 Customer Workspace</div>""",
        unsafe_allow_html=True,
    )

    user_id = st.text_input(
        "Customer ID",
        placeholder="e.g. customer_001",
        help="Each customer receives an isolated retrieval workspace.",
    )

    clean_user_id = user_id.strip()

    if clean_user_id:
        safe_user_id = html.escape(clean_user_id)

        st.markdown(
            f"""<div class="workspace-active">✓ Secure workspace active
<div class="workspace-id">Workspace: {safe_user_id}</div>
</div>""",
            unsafe_allow_html=True,
        )
    else:
        st.warning("Enter a Customer ID")

    st.markdown(
        """<div class="sidebar-divider"></div>
            <div class="sidebar-heading">Security Controls</div>
            <div class="security-control">
            <div class="security-control-title">🛡️ PII Masking</div>
            <div class="security-control-text">Sensitive information is anonymized before embedding.</div>
            </div>
            <div class="security-control">
            <div class="security-control-title">🔒 Tenant Isolation</div>
            <div class="security-control-text">Retrieval is filtered by the active Customer ID.</div>
            </div>
            <div class="security-control">
            <div class="security-control-title">🧠 Local Embeddings</div>
            <div class="security-control-text">Document embeddings are generated locally.</div>
            </div>
            <div class="security-control">
            <div class="security-control-title">📚 Grounded Answers</div>
            <div class="security-control-text">Responses are generated from retrieved document context.</div>
            </div>
            <div class="sidebar-divider"></div>
            <div class="sidebar-footer">SecureRAG Prototype<br>Assessment Build • v1.0.0</div>""",
        unsafe_allow_html=True,
    )


# Reset chat when customer changes

if clean_user_id != st.session_state.active_user:
    st.session_state.messages = []
    st.session_state.active_user = clean_user_id


# Hero

st.markdown(
    """<div class="hero">
        <div class="hero-badge">SECURE DOCUMENT INTELLIGENCE</div>
        <div class="hero-title">Ask your documents. Keep your data private.</div>
        <div class="hero-text">A secure Retrieval-Augmented Generation workspace for querying customer documents with PII masking, tenant-isolated retrieval, local embeddings and source-grounded AI responses.</div>
        </div>""",
    unsafe_allow_html=True,
)


# Status Cards

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

workspace_status = "Active" if clean_user_id else "Not Set"
workspace_style = "status-green" if clean_user_id else ""

with status_col1:
    st.markdown(
        f"""<div class="status-card">
<div class="status-label">👤 Workspace</div>
<div class="status-value {workspace_style}">{workspace_status}</div>
<div class="status-subtitle">Tenant-isolated session</div>
</div>""",
        unsafe_allow_html=True,
    )

with status_col2:
    st.markdown(
        """<div class="status-card">
<div class="status-label">🛡️ PII Protection</div>
<div class="status-value status-green">Enabled</div>
<div class="status-subtitle">Sensitive fields masked</div>
</div>""",
        unsafe_allow_html=True,
    )

with status_col3:
    st.markdown(
        """<div class="status-card">
<div class="status-label">🗄️ Vector Store</div>
<div class="status-value status-indigo">ChromaDB</div>
<div class="status-subtitle">Persistent semantic retrieval</div>
</div>""",
        unsafe_allow_html=True,
    )

with status_col4:
    st.markdown(
        """<div class="status-card">
<div class="status-label">🧠 AI Pipeline</div>
<div class="status-value status-indigo">RAG</div>
<div class="status-subtitle">Grounded document answers</div>
</div>""",
        unsafe_allow_html=True,
    )

st.write("")


# Get current customer documents

current_user_files = []

if clean_user_id:
    current_user_files = [
        result
        for key, result in st.session_state.processed_files.items()
        if key.startswith(f"{clean_user_id}:")
    ]



document_column, assistant_column = st.columns(
    [1, 1.08],
    gap="large",
)


# Document section

with document_column:

    st.markdown(
        """<div class="section-header">
<div class="section-title">📄 Document Workspace</div>
<div class="section-description">Upload PDF, DOCX or TXT documents. Sensitive information is masked before content is embedded and stored.</div>
</div>""",
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        chips = ""

        for uploaded_file in uploaded_files:
            safe_filename = html.escape(uploaded_file.name)

            chips += (
                f'<span class="file-chip">'
                f'📄 {safe_filename}'
                f'</span>'
            )

        st.markdown(chips, unsafe_allow_html=True)

    process_column, clear_column = st.columns([2.2, 1])

    with process_column:
        process_clicked = st.button(
            "🔐 Process Documents Securely",
            type="primary",
            use_container_width=True,
        )

    with clear_column:
        clear_clicked = st.button(
            "🧹 Clear Chat",
            use_container_width=True,
        )

    if clear_clicked:
        st.session_state.messages = []
        st.rerun()

    if process_clicked:

        if not clean_user_id:
            st.error(
                "Enter a Customer ID before processing documents."
            )

        elif not uploaded_files:
            st.error(
                "Upload at least one PDF, DOCX or TXT document."
            )

        else:
            successful_files = 0
            total_chunks = 0

            progress_bar = st.progress(0)
            processing_status = st.empty()

            for index, uploaded_file in enumerate(uploaded_files):

                try:
                    processing_status.info(
                        f"Securing and indexing "
                        f"{uploaded_file.name}..."
                    )

                    uploaded_file.seek(0)

                    result = ingest_document(
                        file=uploaded_file,
                        filename=uploaded_file.name,
                        user_id=clean_user_id,
                    )

                    file_key = (
                        f"{clean_user_id}:"
                        f"{uploaded_file.name}"
                    )

                    st.session_state.processed_files[
                        file_key
                    ] = result

                    successful_files += 1

                    total_chunks += result.get(
                        "chunks_stored",
                        0,
                    )

                except Exception as error:
                    st.error(
                        f"Could not process "
                        f"{uploaded_file.name}: {error}"
                    )

                progress_bar.progress(
                    (index + 1) / len(uploaded_files)
                )

            processing_status.empty()
            progress_bar.empty()

            if successful_files > 0:
                st.markdown(
                    f"""<div class="processing-success">✅ <strong>Secure indexing complete</strong><br>{successful_files} document(s) processed • {total_chunks} chunk(s) stored</div>""",
                    unsafe_allow_html=True,
                )

            # Refresh tenant file list immediately after processing.
            current_user_files = [
                result
                for key, result
                in st.session_state.processed_files.items()
                if key.startswith(
                    f"{clean_user_id}:"
                )
            ]

    if clean_user_id and current_user_files:

        st.write("")

        with st.expander(
            f"📚 Indexed Documents "
            f"({len(current_user_files)})",
            expanded=True,
        ):

            for result in current_user_files:

                filename = html.escape(
                    str(
                        result.get(
                            "filename",
                            "Document",
                        )
                    )
                )

                pages = result.get(
                    "pages_processed",
                    "-"
                )

                chunks = result.get(
                    "chunks_stored",
                    "-"
                )

                st.markdown(
                    f"""<div class="document-card">
                        <div class="document-name">📄 {filename}</div>
                        <div class="document-meta">Pages: {pages} &nbsp;•&nbsp; Chunks: {chunks} &nbsp;•&nbsp; ✓ Securely indexed</div>
                        </div>""",
                    unsafe_allow_html=True,
                )

    elif clean_user_id:
        st.markdown(
            """<div class="empty-state">📂 No documents are indexed in this workspace yet. Upload a document and process it securely to begin.</div>""",
            unsafe_allow_html=True,
        )


# Assistant section

with assistant_column:

    st.markdown(
        """<div class="section-header">
            <div class="section-title">💬 Secure Document Assistant</div>
            <div class="section-description">Ask questions and receive source-grounded answers from documents belonging only to the active customer workspace.</div>
            </div>""",
        unsafe_allow_html=True,
    )

    if not clean_user_id:
        st.info(
            "Enter a Customer ID in the sidebar "
            "to activate the secure assistant."
        )

    elif not current_user_files:
        st.info(
            "Process at least one document before "
            "asking questions."
        )

    # Previous chat messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if (
                message["role"] == "assistant"
                and message.get("sources")
            ):

                with st.expander(
                    "📎 View answer sources"
                ):

                    for source in message["sources"]:

                        source_name = html.escape(
                            str(
                                source.get(
                                    "source",
                                    "Unknown source",
                                )
                            )
                        )

                        source_page = html.escape(
                            str(
                                source.get(
                                    "page",
                                    "-",
                            )
                        )

                                )
                        st.markdown(
                            f"""<div class="source-card">📄 <strong>{source_name}</strong> &nbsp;•&nbsp; Page {source_page}</div>""",
                            unsafe_allow_html=True,
                        )

    # Disable chat until documents are available
    chat_disabled = (
        not clean_user_id
        or not bool(current_user_files)
    )

    question = st.chat_input(
        "Ask a question about your documents...",
        disabled=chat_disabled,
    )

    if question:

        clean_question = question.strip()

        if clean_question:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": clean_question,
                }
            )

            with st.chat_message("user"):
                st.markdown(clean_question)

            with st.chat_message("assistant"):

                try:
                    with st.spinner(
                        "Searching secure document context..."
                    ):
                        result = answer_question(
                            question=clean_question,
                            user_id=clean_user_id,
                        )

                    answer = result.get(
                        "answer",
                        "The requested information "
                        "was not found in the "
                        "uploaded documents.",
                    )

                    sources = result.get(
                        "sources",
                        [],
                    )

                    st.markdown(answer)

                    if sources:

                        with st.expander(
                            "📎 View answer sources"
                        ):

                            for source in sources:

                                source_name = html.escape(
                                    str(
                                        source.get(
                                            "source",
                                            "Unknown source",
                                        )
                                    )
                                )

                                source_page = html.escape(
                                    str(
                                        source.get(
                                            "page",
                                            "-",
                                        )
                                    )
                                )

                                st.markdown(
                                    f"""<div class="source-card">📄 <strong>{source_name}</strong> &nbsp;•&nbsp; Page {source_page}</div>""",
                                    unsafe_allow_html=True,
                                )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )

                except Exception as error:
                    st.error(
                        "Unable to complete the request. "
                        f"Details: {error}"
                    )


# Footer

st.markdown(
    """<div class="app-footer">🔐 SecureRAG &nbsp;•&nbsp; 🛡️ PII Protected &nbsp;•&nbsp; 🔒 Tenant Isolated &nbsp;•&nbsp; 📚 Source Grounded</div>""",
    unsafe_allow_html=True,
)
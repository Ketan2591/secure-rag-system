import html
import re
import streamlit as st
from src.database import (
    clear_user_chat_history,
    get_user_chat_history,
    get_user_documents,
    soft_delete_chat_message,
)
from src.pages.icons import icon


# Matches a masked PII placeholder like <EMAIL_ADDRESS> after it has already been HTML-escaped (so "<" became "&lt;").
_PLACEHOLDER_TAG_ESCAPED_RE = re.compile(r"&lt;([A-Z][A-Z0-9_]*)&gt;")


# Escapes an answer so it is safe to drop into HTML, then wraps any masked placeholder token in a highlighted span.
# Without this, a placeholder like <EMAIL_ADDRESS> would either get escaped into plain text or be mistaken for a real HTML tag.
def _render_answer_html(raw_answer: str) -> str:
    escaped = html.escape(raw_answer or "")
    return _PLACEHOLDER_TAG_ESCAPED_RE.sub(
        lambda m: f'<span class="pii-highlight">&lt;{m.group(1)}&gt;</span>',
        escaped,
    )


# Renders the "Chat History" page: a header with a clear-all button, a document-scope filter, and every past
# question/answer pair (newest first) with its cited sources and a per-message delete button.
def show_history():
    user = st.session_state.get("current_user") or {}
    customer_id = user.get("customer_id", "CUS_GUEST")

    # Page header on the left, "Clear History" button on the right.
    col_title, col_btn = st.columns([3.5, 1])
    with col_title:
        st.markdown(
            f'<div class="page-header"><div class="icon-badge">{icon("chat", 19)}</div>'
            f'<div class="page-header-text"><div class="page-title">Document-Wise Chat History</div>'
            f'<div class="page-caption">Review previous questions, grounded answers, and filter history by specific documents.</div></div></div>',
            unsafe_allow_html=True,
        )
    with col_btn:
        st.write("")
        if st.button("Clear History", icon=":material/delete_sweep:", type="secondary", use_container_width=True):
            clear_user_chat_history(customer_id)
            st.success("Chat history cleared.")
            st.rerun()

    st.write("")
    # Load the customer's chat history and their document list, used below to build the document filter dropdown.
    history = get_user_chat_history(customer_id, include_deleted=False)
    user_docs = get_user_documents(customer_id)

    db_doc_names = [d.get("filename") for d in user_docs if d.get("filename")]

    if not history:
        st.info("No chat history available. Upload a document and start asking questions!")
        return

    # Reshape each raw chat row into a display-friendly form, working out which document(s) it should be
    # grouped under (its cited sources, or "General" if it has none) so the filter dropdown below can use it.
    formatted_history = []
    all_referenced_docs = set()

    for item in history:
        sources = item.get("sources") or []
        doc_names = list(
            dict.fromkeys(
                [s.get("source") for s in sources if s.get("source") and s.get("source") != "Unknown"]
            )
        )
        if not doc_names:
            doc_label = "General / Workspace Documents"
        else:
            doc_label = ", ".join(doc_names)
            for d in doc_names:
                all_referenced_docs.add(d)

        formatted_history.append(
            {
                "id": item.get("id"),
                "user_message": item.get("user_message", ""),
                "assistant_response": item.get("assistant_response", ""),
                "created_at": item.get("created_at", ""),
                "sources": sources,
                "doc_label": doc_label,
                "doc_names": doc_names,
            }
        )

    # Build the filter dropdown from every document the customer owns plus every document ever cited in a chat,
    # so a deleted or unindexed document that still appears in old chat history can still be filtered on.
    available_doc_filters = ["All Documents"] + sorted(list(set(db_doc_names).union(all_referenced_docs)))

    st.markdown(f'<div class="section-heading">{icon("filter", 15)}Filter Questions by Document Scope</div>', unsafe_allow_html=True)
    selected_filter = st.selectbox(
        "Select Document Scope",
        options=available_doc_filters,
        index=0,
        label_visibility="collapsed",
    )

    # Narrow the history down to the selected document scope, or keep everything if "All Documents" is picked.
    if selected_filter == "All Documents":
        filtered_items = formatted_history
    else:
        filtered_items = [
            item
            for item in formatted_history
            if selected_filter in item["doc_names"] or item["doc_label"] == selected_filter
        ]

    st.caption(f"Showing **{len(filtered_items)}** interaction(s) for **{selected_filter}**")
    st.write("")

    if not filtered_items:
        st.info(f"No questions found for document '{selected_filter}'.")
    else:
        # Show newest questions first, each as a card with the question, the answer, cited pages, and a delete button.
        for item in reversed(filtered_items):
            q = html.escape(str(item.get("user_message", "")))
            ans = _render_answer_html(str(item.get("assistant_response", "")))
            created_at = item.get("created_at", "")
            sources = item.get("sources") or []
            doc_label = html.escape(item.get("doc_label", "General"))
            chat_id = item.get("id")

            pages_list = sorted(
                list({str(s.get("page", "-")) for s in sources if s.get("page") is not None})
            )
            pages_text = ", ".join(pages_list) if pages_list else "-"

            with st.container():
                h_col1, h_col2 = st.columns([9, 1])
                with h_col1:
                    st.markdown(
                        f"""
                        <div class="history-card">
                            <div style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: .4rem;">
                                <span class="header-badge">{icon("documents", 12)}&nbsp;{doc_label}</span>
                                <span class="badge-pill success">{icon("check-circle", 11)}&nbsp;Page {pages_text}</span>
                            </div>
                            <div class="history-question">{q}</div>
                            <div class="history-answer">{ans}</div>
                            <div class="history-time">{icon("clock", 11)}&nbsp;{created_at}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with h_col2:
                    if chat_id and st.button("", icon=":material/delete:", key=f"del_chat_hist_{chat_id}", help="Delete Question"):
                        soft_delete_chat_message(chat_id, customer_id)
                        st.rerun()

                # Collapsible list of the exact source chunks (filename + page) that were used to ground this answer.
                if sources:
                    with st.expander(f"Referenced Source Chunks ({len(sources)})", icon=":material/attachment:", expanded=False):
                        for src in sources:
                            s_name = html.escape(str(src.get("source", "Unknown")))
                            s_page = html.escape(str(src.get("page", "-")))
                            st.markdown(
                                f'<span class="source-card">{icon("file", 12)}<strong>&nbsp;{s_name}</strong>&nbsp;•&nbsp;Page {s_page}</span>',
                                unsafe_allow_html=True,
                            )
                st.write("")

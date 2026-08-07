import html
import streamlit as st
from src.database import get_user_chat_history, clear_user_chat_history, get_user_documents, soft_delete_chat_message

def show_history():
    user = st.session_state.get("current_user") or {}
    customer_id = user.get("customer_id", "CUS_GUEST")

    col_title, col_btn = st.columns([3.5, 1])
    with col_title:
        st.markdown("## 💬 Document-Wise Chat History")
        st.caption("Review previous questions, grounded answers, and filter history by specific documents.")
    with col_btn:
        st.write("")
        if st.button("🧹 Clear History", type="secondary", use_container_width=True):
            clear_user_chat_history(customer_id)
            st.success("Chat history cleared (soft-deleted in DB for audit).")
            st.rerun()

    st.write("")

    history = get_user_chat_history(customer_id, include_deleted=False)
    user_docs = get_user_documents(customer_id)
    db_doc_names = [d.get("filename") for d in user_docs if d.get("filename")]

    if not history:
        st.info("No chat history available. Upload a document and start asking questions!")
        return

    # Extract all document sources per chat item
    formatted_history = []
    all_referenced_docs = set()

    for item in history:
        sources = item.get("sources") or []
        doc_names = list(dict.fromkeys([s.get("source") for s in sources if s.get("source") and s.get("source") != "Unknown"]))
        if not doc_names:
            doc_label = "General / No Specific Source"
        else:
            doc_label = ", ".join(doc_names)
            for d in doc_names:
                all_referenced_docs.add(d)

        formatted_history.append({
            "id": item.get("id"),
            "user_message": item.get("user_message", ""),
            "assistant_response": item.get("assistant_response", ""),
            "created_at": item.get("created_at", ""),
            "sources": sources,
            "doc_label": doc_label,
            "doc_names": doc_names,
        })

    # Combine known DB doc names and referenced docs
    available_doc_filters = ["All Documents"] + sorted(list(set(db_doc_names).union(all_referenced_docs)))
    if any(item["doc_label"] == "General / No Specific Source" for item in formatted_history):
        available_doc_filters.append("General / No Specific Source")

    # Document Selector Filter
    st.markdown("#### 🔍 Filter Questions by Document")
    selected_filter = st.selectbox(
        "Select Document",
        options=available_doc_filters,
        index=0,
        label_visibility="collapsed",
    )

    # Filter items based on selection
    if selected_filter == "All Documents":
        filtered_items = formatted_history
    else:
        filtered_items = [
            item for item in formatted_history
            if selected_filter in item["doc_names"] or item["doc_label"] == selected_filter
        ]

    st.caption(f"Showing **{len(filtered_items)}** question(s) for **{selected_filter}**")

    st.write("")

    if not filtered_items:
        st.info(f"No questions asked for document '{selected_filter}'.")
    else:
        for idx, item in enumerate(reversed(filtered_items)):
            q = html.escape(str(item.get("user_message", "")))
            ans = item.get("assistant_response", "")
            created_at = item.get("created_at", "")
            sources = item.get("sources") or []
            doc_label = html.escape(item.get("doc_label", "General"))
            chat_id = item.get("id")

            pages_list = sorted(list({str(s.get("page", "-")) for s in sources if s.get("page") is not None}))
            pages_text = ", ".join(pages_list) if pages_list else "-"

            with st.container():
                h_col1, h_col2 = st.columns([9, 1])
                with h_col1:
                    st.markdown(
                        f"""
                        <div class="history-card">
                            <div style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                                <span class="header-badge" style="background: rgba(99, 102, 241, 0.15); border-color: rgba(99, 102, 241, 0.4); color: #c7d2fe; font-size: 11px;">
                                    📄 Document Source: {doc_label}
                                </span>
                                <span style="background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.45); color: #c7d2fe; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 8px;">
                                    📌 Page Number: {pages_text}
                                </span>
                            </div>
                            <div class="history-question">❓ {q}</div>
                            <div class="history-answer">{ans}</div>
                            <div class="history-time">🕒 {created_at}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with h_col2:
                    if chat_id and st.button("🗑️ Delete", key=f"del_chat_hist_{chat_id}", help="Delete Question (Soft Delete in DB)"):
                        soft_delete_chat_message(chat_id, customer_id)
                        st.rerun()

                if sources:
                    with st.expander(f"📎 Referenced Source Chunks ({len(sources)})", expanded=False):
                        for src in sources:
                            s_name = html.escape(str(src.get("source", "Unknown")))
                            s_page = html.escape(str(src.get("page", "-")))
                            st.markdown(
                                f'<div class="source-card">📄 <strong>{s_name}</strong> • Page {s_page}</div>',
                                unsafe_allow_html=True,
                            )
                st.write("")

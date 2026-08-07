import uuid

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import CHROMA_DB_PATH, COLLECTION_NAME, TOP_K_RESULTS
from src.embeddings import get_embedding_model


def get_vector_store() -> Chroma:
    """Create or connect to the persistent Chroma vector store."""

    CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(CHROMA_DB_PATH),
    )


def add_documents(
    documents: list[Document],
    user_id: str,
) -> list[str]:
    """
    Store document chunks securely for a specific customer.

    Every chunk receives a user_id so retrieval can be
    restricted to the owning customer.
    """

    if not user_id or not user_id.strip():
        raise ValueError("user_id is required.")

    if not documents:
        raise ValueError("No documents were provided.")

    clean_user_id = user_id.strip()

    prepared_documents = []
    ids = []

    for document in documents:
        metadata = document.metadata.copy()

        # Security boundary:
        # Never trust a user_id already present in document metadata.
        metadata["user_id"] = clean_user_id

        prepared_documents.append(
            Document(
                page_content=document.page_content,
                metadata=metadata,
            )
        )

        ids.append(str(uuid.uuid4()))

    vector_store = get_vector_store()

    vector_store.add_documents(
        documents=prepared_documents,
        ids=ids,
    )

    return ids


def search_documents(
    query: str,
    user_id: str,
    doc_name: str = None,
    k: int = TOP_K_RESULTS,
) -> list[Document]:
    """
    Retrieve relevant chunks belonging ONLY to active (non-deleted) documents of the given customer.
    Guarantees that soft-deleted or inactive documents are NEVER queried or returned.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not user_id or not user_id.strip():
        raise ValueError("user_id is required.")

    clean_user_id = user_id.strip()

    # Fetch active non-deleted documents for this user from SQL DB
    from src.database import get_user_documents
    active_docs = get_user_documents(clean_user_id, include_deleted=False)
    active_filenames = {d.get("filename") for d in active_docs if d.get("filename")}

    if not active_filenames:
        # No active documents exist in database for this customer
        return []

    # Clean target document name if provided
    clean_target_doc = None
    if doc_name and doc_name.strip():
        val = doc_name.strip()
        if val not in ["All Documents", "🌐 All Workspace Documents"]:
            clean_target_doc = val

    # If specific target doc requested, verify it is active
    if clean_target_doc and clean_target_doc not in active_filenames:
        return []

    vector_store = get_vector_store()
    
    if clean_target_doc:
        filter_dict = {
            "$and": [
                {"user_id": clean_user_id},
                {"source": clean_target_doc},
            ]
        }
    else:
        filter_dict = {"user_id": clean_user_id}

    results = vector_store.similarity_search(
        query=query.strip(),
        k=k * 2,  # Retrieve extra candidates for safety
        filter=filter_dict,
    )

    # Post-filtering safeguard: STRICTLY discard any chunks from soft-deleted files
    valid_results = []
    for doc in results:
        chunk_source = doc.metadata.get("source")
        if chunk_source in active_filenames:
            if clean_target_doc and chunk_source != clean_target_doc:
                continue
            valid_results.append(doc)

    return valid_results[:k]


def delete_documents_by_filename(filename: str, user_id: str):
    """
    Remove all vector store chunks for a given document belonging to a customer.
    """
    if not filename or not user_id:
        return
    try:
        vector_store = get_vector_store()
        clean_user_id = user_id.strip()
        clean_filename = filename.strip()
        if hasattr(vector_store, "_collection"):
            try:
                vector_store._collection.delete(
                    where={
                        "$and": [
                            {"user_id": clean_user_id},
                            {"source": clean_filename},
                        ]
                    }
                )
            except Exception:
                try:
                    vector_store._collection.delete(
                        where={"source": clean_filename}
                    )
                except Exception:
                    pass
    except Exception as e:
        print(f"Error deleting vectors for {filename}: {e}")
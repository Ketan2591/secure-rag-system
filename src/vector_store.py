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
    k: int = TOP_K_RESULTS,
) -> list[Document]:
    """
    Retrieve relevant chunks belonging ONLY to the given customer.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not user_id or not user_id.strip():
        raise ValueError("user_id is required.")

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query=query.strip(),
        k=k,
        filter={
            "user_id": user_id.strip(),
        },
    )

    return results
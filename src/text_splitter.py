from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.pii_masker import mask_pii


def create_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create and configure the text splitter."""

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def mask_documents(documents: list[Document]) -> list[Document]:
    """
    Mask sensitive information before documents are chunked
    and stored in the vector database.
    """

    masked_documents = []

    for document in documents:
        masked_text = mask_pii(document.page_content)

        masked_documents.append(
            Document(
                page_content=masked_text,
                metadata=document.metadata.copy(),
            )
        )

    return masked_documents


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Mask sensitive information and split documents into
    smaller chunks while preserving metadata.
    """

    if not documents:
        return []

    # IMPORTANT:
    # Sensitive information is removed BEFORE chunking/embedding.
    masked_documents = mask_documents(documents)

    text_splitter = create_text_splitter()

    chunks = text_splitter.split_documents(masked_documents)

    # Add a chunk number for traceability.
    for index, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk_id"] = index

    return chunks
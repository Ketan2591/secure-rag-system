"""
Prepares documents for the vector store: mask out PII first, then split
into overlapping chunks. The order matters -- masking runs before chunking
(not after) because it's the chunks themselves that get embedded and written
to ChromaDB/Pinecone, and a raw sensitive value must never end up sitting in
storage. Same reasoning as in pii_masker.py, just applied on the chunking side.
"""

from langchain_core.documents import Document
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.pii_masker import mask_pii


# Builds a RecursiveCharacterTextSplitter using the chunk size and overlap set in config, with sensible separators to split on paragraphs first, then lines, then words.
def create_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


# Runs mask_pii over every document's text and returns new Document objects with the masked text, keeping the original metadata intact.
def mask_documents(documents: list[Document]) -> list[Document]:
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


# Masks sensitive info in every document first, then splits the masked text into smaller overlapping chunks and tags each chunk with a chunk_id.
# Masking has to happen before splitting so a sensitive value never ends up sitting unmasked in the vector store.
def split_documents(documents: list[Document]) -> list[Document]:
    if not documents:
        return []

    masked_documents = mask_documents(documents)

    text_splitter = create_text_splitter()

    chunks = text_splitter.split_documents(masked_documents)

    # chunk_id only makes sense once splitting has actually happened (a
    # document doesn't have "chunks" before this point), so it gets stamped
    # on afterward -- lets us trace an answer back to the exact chunk it
    # came from later on.
    for index, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk_id"] = index

    return chunks
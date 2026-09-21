"""
Thin wrapper around whichever vector database backend we're actually using.

We support two backends behind one interface: ChromaDB (local, file-backed,
zero setup) and Pinecone (cloud, used when an API key is configured). Every
chunk gets a `user_id` tag in its metadata so one tenant's documents never
leak into another tenant's search results. Chroma and Pinecone don't behave
identically when it comes to metadata filtering, so a fair amount of this
file is fallback logic to paper over those differences rather than "real"
retrieval logic.
"""

import uuid

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import (
    CHROMA_DB_PATH,
    COLLECTION_NAME,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    TOP_K_RESULTS,
    VECTOR_DB_PROVIDER,
)
from src.embeddings import get_embedding_model


# Picking / building a backend

# Tries to connect to Pinecone and create the index if it doesn't exist yet, returning the connected vector store.
# Returns None instead of raising on any failure, so the caller can quietly fall back to local Chroma.
def _get_pinecone_vector_store():
    if not PINECONE_API_KEY:
        return None

    try:
        from langchain_pinecone import PineconeVectorStore
        from pinecone import Pinecone, ServerlessSpec

        pc = Pinecone(api_key=PINECONE_API_KEY)

        existing_indices = [idx.name for idx in pc.list_indexes()]
        if PINECONE_INDEX_NAME not in existing_indices:
            try:
                pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=384,
                    metric='cosine',
                    spec=ServerlessSpec(cloud='aws', region='us-east-1'),
                )
            except Exception as e:
                print(f'Pinecone index creation note: {e}')

        vector_store = PineconeVectorStore(
            index_name=PINECONE_INDEX_NAME,
            embedding=get_embedding_model(),
            pinecone_api_key=PINECONE_API_KEY,
        )
        return vector_store
    except Exception as e:
        print(f'Pinecone init note (using ChromaDB fallback): {e}')
        return None


# Returns the Pinecone vector store if it is configured and working, otherwise falls back to a local Chroma store on disk.
def get_vector_store():
    if VECTOR_DB_PROVIDER.lower() == 'pinecone' and PINECONE_API_KEY:
        pinecone_vs = _get_pinecone_vector_store()
        if pinecone_vs is not None:
            return pinecone_vs

    CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(CHROMA_DB_PATH),
    )


# Writing to the store

# Tags every document with the user_id (so tenants stay isolated) and writes them to the vector store, generating a unique id for each one.
# If the main backend rejects the write, it retries against local Chroma so the upload isn't lost.
def add_documents(
    documents: list[Document],
    user_id: str,
) -> list[str]:
    if not user_id or not user_id.strip():
        raise ValueError('user_id is required.')

    if not documents:
        raise ValueError('No documents were provided.')

    clean_user_id = user_id.strip()

    prepared_documents = []
    ids = []

    for document in documents:
        metadata = document.metadata.copy()
        metadata['user_id'] = clean_user_id

        prepared_documents.append(
            Document(
                page_content=document.page_content,
                metadata=metadata,
            )
        )
        ids.append(str(uuid.uuid4()))

    vector_store = get_vector_store()

    try:
        vector_store.add_documents(
            documents=prepared_documents,
            ids=ids,
        )
    except Exception:
        # If the configured backend (e.g. Pinecone) rejects the write for any
        # reason, don't just lose the upload — write it to local Chroma
        # instead so the user's documents still end up searchable.
        CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
        fallback_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embedding_model(),
            persist_directory=str(CHROMA_DB_PATH),
        )
        fallback_store.add_documents(
            documents=prepared_documents,
            ids=ids,
        )

    return ids


# Searching/reading

# Runs a similarity search scoped to one user (and optionally one document), then double-checks every result against the database's active/deleted list.
# When searching the whole workspace it spreads results across documents instead of just returning the globally top-ranked chunks.
def search_documents(
    query: str,
    user_id: str,
    doc_name: str | None = None,
    k: int = TOP_K_RESULTS,
) -> list[Document]:
    if not query or not query.strip():
        raise ValueError('Query cannot be empty.')

    if not user_id or not user_id.strip():
        raise ValueError('user_id is required.')

    clean_user_id = user_id.strip()

    from src.database import get_user_documents
    all_user_docs = get_user_documents(clean_user_id, include_deleted=True)
    active_filenames = {d.get('filename') for d in all_user_docs if not d.get('is_deleted')}
    deleted_filenames = {d.get('filename') for d in all_user_docs if d.get('is_deleted')} - active_filenames

    clean_target_doc = None
    if doc_name and doc_name.strip():
        val = doc_name.strip()
        if val not in ['All Documents', 'dYO? All Workspace Documents', 'All Workspace Documents', '🌐 All Workspace Documents']:
            clean_target_doc = val

    if active_filenames and clean_target_doc and clean_target_doc not in active_filenames:
        return []

    if clean_target_doc and clean_target_doc in deleted_filenames:
        return []

    vector_store = get_vector_store()

    if clean_target_doc:
        filter_dict = {
            "$and": [
                {"user_id": {"$eq": clean_user_id}},
                {"source": {"$eq": clean_target_doc}},
            ]
        }
    else:
        filter_dict = {"user_id": {"$eq": clean_user_id}}

    # When searching the whole workspace, fetch enough candidates that every
    # active document gets a fair chance to surface at least one chunk —
    # otherwise a broad question ("what is X in all documents") only ever
    # sees the globally top-ranked chunks and silently drops documents whose
    # wording just ranks a bit lower for that query.
    fetch_k = k * 3 if clean_target_doc else max(k * 3, len(active_filenames) * 6, 60)

    try:
        results = vector_store.similarity_search(
            query=query.strip(),
            k=fetch_k,
            filter=filter_dict,  # type: ignore[arg-type]
        )
    except Exception as e:
        # Some vector-store backends differ in how they accept compound
        # metadata filters.  Keep the tenant filter in the database query,
        # then enforce the selected filename again below in Python.
        # Requesting more candidates here prevents a selected document from
        # being missed simply because other workspace documents ranked first.
        print(f'Similarity search filter note ({e}), using tenant-only fallback.')
        try:
            results = vector_store.similarity_search(
                query=query.strip(),
                k=max(fetch_k, 100) if clean_target_doc else fetch_k,
                filter={'user_id': clean_user_id},
            )
        except Exception:
            CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
            fallback_store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=get_embedding_model(),
                persist_directory=str(CHROMA_DB_PATH),
            )
            results = fallback_store.similarity_search(
                query=query.strip(),
                k=max(fetch_k, 100) if clean_target_doc else fetch_k,
                filter={'user_id': clean_user_id},
            )

    # Belt-and-suspenders: re-check every result against the database's view
    # of what's active/deleted, even though we already passed a filter into
    # the vector-store query above. The vector store's own filtering isn't
    # always fully reliable across backends (and a soft-deleted document can
    # briefly still have chunks sitting in the index), so we don't trust it
    # alone — we trust the database as the source of truth and use it here
    # to strip out anything that shouldn't be showing up anymore.
    valid_results = []
    for doc in results:
        chunk_source = doc.metadata.get('source')

        if chunk_source in deleted_filenames:
            continue

        if active_filenames and chunk_source not in active_filenames:
            continue

        if clean_target_doc and chunk_source != clean_target_doc:
            continue

        valid_results.append(doc)

    if clean_target_doc:
        return valid_results[:k]

    # All Workspace Documents: guarantee coverage of every matching document
    # instead of a flat top-k that can end up drawn from just a few files.
    per_document: dict = {}
    for doc in valid_results:
        per_document.setdefault(doc.metadata.get('source'), []).append(doc)

    chunks_per_doc = 2
    safety_cap = 30
    diversified = []
    for source_chunks in per_document.values():
        diversified.extend(source_chunks[:chunks_per_doc])

    return diversified[:safety_cap]


# Fetches every single chunk stored for one document, not just the top-ranked ones a similarity search would return for some query.
# Used to reliably check whether a masked field like <EMAIL_ADDRESS> exists anywhere in the document, regardless of how its chunks rank.
def get_full_document_text(user_id: str, filename: str) -> str:
    clean_user_id = (user_id or '').strip()
    clean_filename = (filename or '').strip()
    if not clean_user_id or not clean_filename:
        return ''

    vector_store = get_vector_store()
    where_filter = {
        '$and': [
            {'user_id': {'$eq': clean_user_id}},
            {'source': {'$eq': clean_filename}},
        ]
    }

    # `_collection` is a Chroma-specific attribute (the underlying chromadb
    # collection object), not something Pinecone's wrapper exposes. Since
    # get_vector_store() can hand back either backend, we check for it here
    # rather than assuming — if it's there, we can do a real metadata-only
    # "get everything matching this filter" instead of a similarity search.
    if hasattr(vector_store, '_collection'):
        try:
            result = vector_store._collection.get(where=where_filter, include=['documents'])  # type: ignore[attr-defined]
            return '\n'.join(result.get('documents') or [])
        except Exception as e:
            print(f'Full-document fetch note for {filename}: {e}')

    # Non-Chroma backends (e.g. Pinecone): best-effort broad fetch since
    # there is no plain metadata-only "get" available.
    try:
        docs = vector_store.similarity_search(query=clean_filename, k=200, filter=where_filter)  # type: ignore[arg-type]
        return '\n'.join(d.page_content for d in docs)
    except Exception as e:
        print(f'Full-document fallback fetch note for {filename}: {e}')
        return ''


# Deletion

# Removes all vector chunks belonging to one filename for one user from the Chroma collection.
# If the compound filter fails on some Chroma versions, it retries with a filename-only delete so the chunks don't linger forever.
def delete_documents_by_filename(filename: str, user_id: str):
    if not filename or not user_id:
        return

    clean_user_id = user_id.strip()
    clean_filename = filename.strip()

    try:
        vector_store = get_vector_store()
        # Same reasoning as in get_full_document_text: only Chroma gives us
        # direct access to the underlying collection, so we branch on that
        # first. Pinecone doesn't expose `_collection`, but its LangChain
        # wrapper has its own public `.delete(filter=...)` method, so it
        # gets a separate branch below instead of being silently skipped.
        if hasattr(vector_store, '_collection'):
            try:
                vector_store._collection.delete(  # type: ignore[attr-defined]
                    where={
                        '$and': [
                            {'user_id': clean_user_id},
                            {'source': clean_filename},
                        ]
                    }
                )
            except Exception:
                # Some Chroma versions choke on the compound $and filter above
                # (or a stale collection has entries missing user_id) — retry
                # with a filename-only delete so the document doesn't just
                # linger in the index forever.
                try:
                    vector_store._collection.delete(where={'source': clean_filename})  # type: ignore[attr-defined]
                except Exception:
                    pass
        elif hasattr(vector_store, 'delete'):
            try:
                vector_store.delete(
                    filter={
                        '$and': [
                            {'user_id': {'$eq': clean_user_id}},
                            {'source': {'$eq': clean_filename}},
                        ]
                    }
                )
            except Exception:
                # Same belt-and-suspenders fallback as the Chroma path above,
                # in case Pinecone rejects the compound filter for some reason.
                try:
                    vector_store.delete(filter={'source': {'$eq': clean_filename}})
                except Exception:
                    pass
    except Exception as e:
        print(f'Deletion note for {filename}: {e}')

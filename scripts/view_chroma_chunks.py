"""
Manually browse what's actually stored in the local ChromaDB folder (data/chroma_db).

This connects straight to the Chroma persist_directory, bypassing get_vector_store()'s
Pinecone/Chroma routing -- so it works even when Pinecone is the active backend and shows
you exactly what's sitting in the local fallback store.

Usage (run from the project root):
    .venv\\Scripts\\python.exe scripts\\view_chroma_chunks.py
    .venv\\Scripts\\python.exe scripts\\view_chroma_chunks.py --user CUS_D3B5BJ
    .venv\\Scripts\\python.exe scripts\\view_chroma_chunks.py --user CUS_D3B5BJ --file "1_Avenqora_AvenQ_Platform_Technical_Documentation.pdf"
    .venv\\Scripts\\python.exe scripts\\view_chroma_chunks.py --limit 20
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from langchain_chroma import Chroma
from src.embeddings import get_embedding_model
from src.config import CHROMA_DB_PATH, COLLECTION_NAME


def main():
    parser = argparse.ArgumentParser(description="Browse chunks stored locally in ChromaDB")
    parser.add_argument("--user", help="Only show chunks for this customer_id")
    parser.add_argument("--file", help="Only show chunks for this exact filename")
    parser.add_argument("--limit", type=int, default=15, help="Max chunks to print (default 15)")
    parser.add_argument("--full", action="store_true", help="Print each chunk's full text instead of a 150-char preview")
    args = parser.parse_args()

    print(f"ChromaDB folder: {CHROMA_DB_PATH}\n")

    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(CHROMA_DB_PATH),
    )
    collection = store._collection
    print(f"Total chunks in the collection (everyone, every document): {collection.count()}\n")

    where = None
    if args.user and args.file:
        where = {"$and": [{"user_id": args.user}, {"source": args.file}]}
    elif args.user:
        where = {"user_id": args.user}
    elif args.file:
        where = {"source": args.file}

    result = collection.get(
        where=where,  # type: ignore[arg-type]
        limit=1000,
        include=["documents", "metadatas"],
    )

    # Chroma types documents/metadatas as Optional (None if nothing came back),
    # even though passing include=[...] guarantees a list here in practice --
    # the "or []" keeps this safe either way and satisfies the type checker.
    ids = result["ids"] or []
    metadatas = result["metadatas"] or []
    documents = result["documents"] or []
    rows = list(zip(ids, metadatas, documents))
    rows.sort(key=lambda r: (r[1].get("source", ""), r[1].get("chunk_id", 0)))

    print(f"Matching chunks: {len(rows)} (showing first {args.limit})\n")

    for chunk_id, metadata, text in rows[: args.limit]:
        shown = (text or "") if args.full else (text or "").replace("\n", " ")[:150]
        print(f"chunk_id={metadata.get('chunk_id')}  page={metadata.get('page')}  "
              f"source={metadata.get('source')}  user_id={metadata.get('user_id')}")
        print(f"  text: {shown}")
        print()


if __name__ == "__main__":
    main()

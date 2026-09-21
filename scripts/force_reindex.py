import os
import sys
import argparse


# CLI script: takes a customer_id and a filename from reindex_files/, deletes that document's old vectors, and re-ingests
# the file from scratch. Useful when a document was indexed with old/buggy logic and needs to be redone.
def main():
    parser = argparse.ArgumentParser(description="Force re-index a document for a user.")
    parser.add_argument("customer_id", help="Customer ID (e.g. CUS_XXXXX)")
    parser.add_argument("filename", help="Filename located in reindex_files/ to ingest")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(__file__))
    reindex_dir = os.path.join(repo_root, "reindex_files")
    os.makedirs(reindex_dir, exist_ok=True)

    target_path = os.path.join(reindex_dir, args.filename)
    if not os.path.exists(target_path):
        print(f"ERROR: file not found: {target_path}")
        print("Place the file you want to re-index in the project's reindex_files/ folder.")
        sys.exit(2)

    # Import project functions
    try:
        from src.vector_store import delete_documents_by_filename
        from src.rag_pipeline import ingest_document
    except Exception as e:
        print("ERROR: could not import project modules. Make sure dependencies are installed.")
        print(e)
        sys.exit(3)

    customer_id = args.customer_id
    filename = args.filename

    print(f"Deleting existing vectors for {customer_id} / {filename} ...")
    try:
        delete_documents_by_filename(filename=filename, user_id=customer_id)
        print("Delete operation attempted (no exception).")
    except Exception as e:
        print(f"Warning: delete failed: {e}")

    # Re-ingest file
    print(f"Re-ingesting {target_path} for {customer_id} ...")
    try:
        with open(target_path, "rb") as f:
            res = ingest_document(file=f, filename=filename, user_id=customer_id)

        print("Ingest result:")
        print(res)
    except Exception as e:
        print("ERROR: ingest failed.")
        print(e)
        sys.exit(4)


if __name__ == "__main__":
    main()

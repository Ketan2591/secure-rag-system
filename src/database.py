"""
Data access layer for SecureRAG. Everything here talks to either Postgres or a local
SQLite file depending on what's configured/available — I wanted the app runnable on a
laptop with zero setup, so if Postgres isn't reachable it just falls back to SQLite
automatically. That's also why almost every function branches on `is_sqlite`: the two
drivers use different placeholder styles (`?` vs `%s`) and hand back rows in different
shapes, so a lot of this file is just quietly smoothing that over.
"""

import json
import os
import sqlite3
from pathlib import Path
from src.config import (
    BASE_DIR,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


# Connection helpers

def dict_factory(cursor, row):
    """
    Turns a plain SQLite row tuple into a dict by pairing each value with its column name.
    This makes SQLite rows look the same as psycopg rows, which already come back dict-like.
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_connection():
    """
    Tries to connect to Postgres first using the settings from config, and if that fails for any reason (not installed, not running, wrong credentials), it silently connects to a local SQLite file instead.
    This is what lets the app run on a laptop with zero setup.
    """
    try:
        import psycopg
        conn = psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            connect_timeout=3,
        )
        return conn
    except Exception:
        # Fallback to local SQLite database
        db_dir = BASE_DIR / "data"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "secure_rag.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = dict_factory
        return conn


def get_db_type() -> str:
    """
    Opens a connection just to check whether it landed on SQLite or Postgres, then closes it.
    Used by the settings/dashboard UI to show which database is actually active right now.
    """
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            return "SQLite (Local Storage)"
        else:
            return f"PostgreSQL ({POSTGRES_DB})"
    finally:
        conn.close()


# Table setup / schema migrations

def create_tables():
    """
    Creates the users, documents and chat_history tables the first time the app runs, and does nothing if they already exist.
    Also checks for newer columns like is_deleted and target_doc and adds them if an older database is missing them.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)

        pk_type = "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"

        # Users table
        # pyrefly: ignore [no-matching-overload]
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {pk_type},
            customer_id VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(150) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()

        # Documents table
        # pyrefly: ignore [no-matching-overload]
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS documents (
            id {pk_type},
            customer_id VARCHAR(255) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            pages_processed INTEGER DEFAULT 0,
            chunks_stored INTEGER DEFAULT 0,
            file_size_bytes INTEGER DEFAULT 0,
            is_deleted BOOLEAN DEFAULT FALSE,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()

        # Chat History table
        # pyrefly: ignore [no-matching-overload]
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS chat_history (
            id {pk_type},
            customer_id VARCHAR(255) NOT NULL,
            user_message TEXT NOT NULL,
            assistant_response TEXT NOT NULL,
            sources_json TEXT,
            is_deleted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()

        # Check and add 'is_deleted' column to documents table if missing
        try:
            if is_sqlite:
                cur.execute("PRAGMA table_info(documents);")
                cols = [row["name"] if isinstance(row, dict) else row[1] for row in cur.fetchall()]
                if "is_deleted" not in cols:
                    cur.execute("ALTER TABLE documents ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;")
                    conn.commit()
            else:
                cur.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'documents' AND column_name = 'is_deleted';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE documents ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;")
                    conn.commit()
        except Exception:
            # Best-effort column patch — if this fails the table probably
            # already has the column (or we can't alter it), either way it's
            # not worth crashing startup over.
            pass

        # Check and add 'is_deleted' column to chat_history table if missing
        try:
            if is_sqlite:
                cur.execute("PRAGMA table_info(chat_history);")
                cols = [row["name"] if isinstance(row, dict) else row[1] for row in cur.fetchall()]
                if "is_deleted" not in cols:
                    cur.execute("ALTER TABLE chat_history ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;")
                    conn.commit()
            else:
                cur.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'chat_history' AND column_name = 'is_deleted';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE chat_history ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;")
                    conn.commit()
        except Exception:
            pass

        # Check and add 'target_doc' column to chat_history table if missing
        try:
            if is_sqlite:
                cur.execute("PRAGMA table_info(chat_history);")
                cols = [row["name"] if isinstance(row, dict) else row[1] for row in cur.fetchall()]
                if "target_doc" not in cols:
                    cur.execute("ALTER TABLE chat_history ADD COLUMN target_doc VARCHAR(255) DEFAULT '🌐 All Workspace Documents';")
                    conn.commit()
            else:
                cur.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'chat_history' AND column_name = 'target_doc';
                """)
                if not cur.fetchone():
                    cur.execute("ALTER TABLE chat_history ADD COLUMN target_doc VARCHAR(255) DEFAULT '🌐 All Workspace Documents';")
                    conn.commit()
        except Exception:
            pass

    finally:
        conn.close()


# Document tracking

def save_document_metadata(customer_id: str, filename: str, pages_processed: int, chunks_stored: int, file_size_bytes: int = 0):
    """
    Inserts one new row into the documents table with the filename, page count, chunk count and file size for a customer's upload.
    Called right after a document has been processed and stored in the vector database.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"""
            INSERT INTO documents (customer_id, filename, pages_processed, chunks_stored, file_size_bytes, is_deleted)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, FALSE)
            """,
            (customer_id, filename, pages_processed, chunks_stored, file_size_bytes),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_documents(customer_id: str, include_deleted: bool = False) -> list[dict]:
    """
    Fetches all documents that belong to a customer, newest upload first, skipping soft-deleted ones unless include_deleted is True.
    Also normalizes each row into a plain dict since SQLite and Postgres hand back rows in different shapes.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"

        if include_deleted:
            query = f"SELECT * FROM documents WHERE customer_id = {ph} ORDER BY uploaded_at DESC"
            params = (customer_id,)
        else:
            query = f"SELECT * FROM documents WHERE customer_id = {ph} AND (is_deleted = FALSE OR is_deleted IS NULL) ORDER BY uploaded_at DESC"
            params = (customer_id,)

        # pyrefly: ignore [bad-argument-type]
        cur.execute(query, params)
        rows = cur.fetchall()
        result = []
        for r in rows:
            # Rows show up differently depending on the driver/row_factory in
            # play: SQLite (with dict_factory above) hands back dicts, but
            # psycopg's default cursor gives plain tuples. Rather than forcing
            # a row factory everywhere, we just check the shape here and build
            # the dict ourselves from cur.description when needed. This same
            # dict-or-zip fallback shows up a few more times below.
            if isinstance(r, dict):
                result.append(r)
            else:
                # pyrefly: ignore [not-iterable]
                cols = [col[0] for col in cur.description] # type: ignore
                result.append(dict(zip(cols, r)))
        return result
    finally:
        conn.close()


def is_document_already_indexed(customer_id: str, filename: str) -> bool:
    """
    Looks through the customer's active (non-deleted) documents to see if one with this exact filename already exists.
    Used to stop the same file from being uploaded and indexed twice.
    """
    if not customer_id or not filename:
        return False
    active_docs = get_user_documents(customer_id, include_deleted=False)
    active_filenames = {d.get("filename") for d in active_docs if d.get("filename")}
    return filename.strip() in active_filenames


def delete_user_document(doc_id: int, customer_id: str):
    """
    Marks one document as is_deleted = TRUE so it disappears from the active UI, without ever deleting the actual row.
    The record stays in the database permanently for audit and safety reasons.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"

        # Mark document as soft deleted in DB (DO NOT HARD DELETE!)
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"UPDATE documents SET is_deleted = TRUE WHERE id = {ph} AND customer_id = {ph}",
            (doc_id, customer_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_document_count(customer_id: str) -> int:
    """
    Counts how many active (non-deleted) documents a customer currently has uploaded.
    Used mainly for showing stats on the dashboard.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"SELECT COUNT(*) FROM documents WHERE customer_id = {ph} AND (is_deleted = FALSE OR is_deleted IS NULL)",
            (customer_id,),
        )
        row = cur.fetchone()
        # COUNT(*) comes back as a dict under SQLite (dict_factory) and a
        # tuple under psycopg — same row-shape story as above, just handled
        # inline since it's a single value rather than a list of records.
        if isinstance(row, dict):
            return list(row.values())[0]
        return row[0] if row else 0
    finally:
        conn.close()


# Chat history

def save_chat_message(
    customer_id: str,
    user_message: str,
    assistant_response: str,
    sources: list = None, # type: ignore
    target_doc: str = "🌐 All Workspace Documents",
):
    """
    Saves one question and answer pair into chat_history, along with the sources used and which document/workspace it belongs to.
    The sources list is stored as a JSON string since the columns are plain text.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        sources_str = json.dumps(sources or [])
        clean_target = (target_doc or "🌐 All Workspace Documents").strip()
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"""
            INSERT INTO chat_history (customer_id, user_message, assistant_response, sources_json, target_doc, is_deleted)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, FALSE)
            """,
            (customer_id, user_message, assistant_response, sources_str, clean_target),
        )
        conn.commit()
    finally:
        conn.close()


def soft_delete_chat_message(chat_id: int, customer_id: str):
    """
    Marks one chat message as is_deleted = TRUE so it is hidden from the UI, without actually removing it.
    The message stays in the database permanently for audit and safety reasons.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"UPDATE chat_history SET is_deleted = TRUE WHERE id = {ph} AND customer_id = {ph}",
            (chat_id, customer_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_chat_history(customer_id: str, target_doc: str | None = None, include_deleted: bool = False) -> list[dict]:
    """
    Fetches a customer's chat history, hiding messages tied to deleted documents and filtering to one document/workspace if target_doc is given.
    Also loads the sources JSON back into a list for each message.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"

        # Fetch soft-deleted filenames for this user to exclude chats of deleted files
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"SELECT filename FROM documents WHERE customer_id = {ph} AND is_deleted = TRUE",
            (customer_id,),
        )
        deleted_doc_rows = cur.fetchall()
        deleted_filenames = set()
        for r in deleted_doc_rows:
            if isinstance(r, dict):
                deleted_filenames.add(r.get("filename"))
            else:
                deleted_filenames.add(r[0])

        # A filename can be soft-deleted and later re-uploaded under the same
        # name, producing both a deleted row and a current active row. Only
        # exclude filenames that have NO active (non-deleted) document left —
        # otherwise a fresh re-upload's chat history stays hidden forever.
        if deleted_filenames:
            cur.execute(
                # pyrefly: ignore [bad-argument-type]
                f"SELECT filename FROM documents WHERE customer_id = {ph} AND (is_deleted = FALSE OR is_deleted IS NULL)",
                (customer_id,),
            )
            active_doc_rows = cur.fetchall()
            active_filenames = set()
            for r in active_doc_rows:
                if isinstance(r, dict):
                    active_filenames.add(r.get("filename"))
                else:
                    active_filenames.add(r[0])
            deleted_filenames -= active_filenames

        if include_deleted:
            query = f"SELECT * FROM chat_history WHERE customer_id = {ph} ORDER BY created_at ASC"
        else:
            query = f"SELECT * FROM chat_history WHERE customer_id = {ph} AND (is_deleted = FALSE OR is_deleted IS NULL) ORDER BY created_at ASC"

        # pyrefly: ignore [bad-argument-type]
        cur.execute(query, (customer_id,))
        rows = cur.fetchall()
        result = []
        for r in rows:
            if isinstance(r, dict):
                d = dict(r)
            else:
                # pyrefly: ignore [not-iterable]
                cols = [col[0] for col in cur.description] # type: ignore
                d = dict(zip(cols, r))

            try:
                d["sources"] = json.loads(d.get("sources_json") or "[]")
            except Exception:
                # Malformed/empty JSON shouldn't blow up the whole history
                # fetch — just treat it as "no sources" and move on.
                d["sources"] = []

            # Exclude chats belonging strictly to soft-deleted files
            if not include_deleted and deleted_filenames:
                if d.get("sources"):
                    non_deleted_sources = [s for s in d["sources"] if s.get("source") and s.get("source") not in deleted_filenames]
                    has_deleted_sources = any(s.get("source") in deleted_filenames for s in d["sources"])
                    if not non_deleted_sources and has_deleted_sources:
                        continue
                if d.get("target_doc") and d.get("target_doc") in deleted_filenames:
                    continue

            # Per-Document Chat Workspace Filtering
            if target_doc:
                clean_target = target_doc.strip()
                item_target = (d.get("target_doc") or "🌐 All Workspace Documents").strip()

                is_all_workspace = clean_target in ["🌐 All Workspace Documents", "All Workspace Documents", "All Documents"]
                item_is_all_workspace = item_target in ["🌐 All Workspace Documents", "All Workspace Documents", "All Documents", ""]

                if is_all_workspace:
                    if not item_is_all_workspace and d.get("target_doc"):
                        # If filtering for All Workspace Documents, exclude specific doc chats
                        continue
                else:
                    # Specific document target match: only show chats that were asked
                    # while this exact document was selected. Do NOT fall back to
                    # matching on cited sources, otherwise an "All Workspace
                    # Documents" answer that happens to cite this file would leak
                    # into this document's isolated conversation.
                    target_matches = (item_target == clean_target)

                    if not target_matches:
                        continue

            result.append(d)
        return result
    finally:
        conn.close()


def clear_user_chat_history(customer_id: str):
    """
    Marks every chat message belonging to a customer as is_deleted = TRUE in one go, used for the "clear chat" button.
    The rows stay in the database permanently for audit and compliance.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"UPDATE chat_history SET is_deleted = TRUE WHERE customer_id = {ph}",
            (customer_id,),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_chat_count(customer_id: str) -> int:
    """
    Simply calls get_user_chat_history and returns how many active messages came back.
    Kept as its own function so callers who just need a number don't have to deal with the filtering logic.
    """
    active_chats = get_user_chat_history(customer_id, include_deleted=False)
    return len(active_chats)


# Workspace reset

def reset_customer_workspace(customer_id: str):
    """
    Soft-deletes all of a customer's documents and chat history, then also removes their vectors from the vector store.
    Used by the "start over" button in the UI to give the user a clean, fresh workspace. Any vector cleanup failure is ignored.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        # pyrefly: ignore [bad-argument-type]
        cur.execute(f"UPDATE documents SET is_deleted = TRUE WHERE customer_id = {ph}", (customer_id,))
        # pyrefly: ignore [bad-argument-type]
        cur.execute(f"UPDATE chat_history SET is_deleted = TRUE WHERE customer_id = {ph}", (customer_id,))
        conn.commit()
    finally:
        conn.close()

    try:
        from src.vector_store import get_vector_store
        vs = get_vector_store()
        if hasattr(vs, "_collection"):
            try:
                vs._collection.delete(where={"user_id": customer_id}) # type: ignore
            except Exception:
                pass
    except Exception:
        pass


# User profile / account management

def update_user_profile(user_id: int, full_name: str):
    """
    Updates the full_name column for a user, used when someone edits their name in the profile settings page.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"UPDATE users SET full_name = {ph} WHERE id = {ph}",
            (full_name, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_user_password(user_id: int, password_hash: str):
    """
    Updates the stored password_hash for a user, used when someone changes their password from the settings page.
    The caller is expected to hash the new password before calling this.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"UPDATE users SET password_hash = {ph} WHERE id = {ph}",
            (password_hash, user_id),
        )
        conn.commit()
    finally:
        conn.close()


# Auto-initialize database tables on import
try:
    create_tables()
except Exception:
    pass

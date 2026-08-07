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

# Helper row factory for SQLite dict-like access
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_connection():
    """
    Create and return a database connection.
    Attempts PostgreSQL first, falls back to SQLite.
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
    """Return the name of the currently active database engine."""
    conn = get_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            return "SQLite (Local Storage)"
        else:
            return f"PostgreSQL ({POSTGRES_DB})"
    finally:
        conn.close()


def create_tables():
    """
    Create users, documents, and chat_history tables if they do not already exist,
    and safely ensure all columns (like is_deleted) exist in both PostgreSQL & SQLite.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        
        pk_type = "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"

        # Users table
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {pk_type},
            customer_id VARCHAR(12) UNIQUE NOT NULL,
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
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS documents (
            id {pk_type},
            customer_id VARCHAR(12) NOT NULL,
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
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS chat_history (
            id {pk_type},
            customer_id VARCHAR(12) NOT NULL,
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

    finally:
        conn.close()


def save_document_metadata(customer_id: str, filename: str, pages_processed: int, chunks_stored: int, file_size_bytes: int = 0):
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
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

        cur.execute(query, params)
        rows = cur.fetchall()
        result = []
        for r in rows:
            if isinstance(r, dict):
                result.append(r)
            else:
                cols = [col[0] for col in cur.description]
                result.append(dict(zip(cols, r)))
        return result
    finally:
        conn.close()


def delete_user_document(doc_id: int, customer_id: str):
    """
    Soft-delete document: Marks is_deleted = TRUE so it is hidden from active UI,
    while PERMANENTLY PRESERVING document records and chat history in Database for future audit & safety.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"

        # Mark document as soft deleted in DB (DO NOT HARD DELETE!)
        cur.execute(
            f"UPDATE documents SET is_deleted = TRUE WHERE id = {ph} AND customer_id = {ph}",
            (doc_id, customer_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_document_count(customer_id: str) -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            f"SELECT COUNT(*) FROM documents WHERE customer_id = {ph} AND (is_deleted = FALSE OR is_deleted IS NULL)",
            (customer_id,),
        )
        row = cur.fetchone()
        if isinstance(row, dict):
            return list(row.values())[0]
        return row[0] if row else 0
    finally:
        conn.close()


def save_chat_message(customer_id: str, user_message: str, assistant_response: str, sources: list = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        sources_str = json.dumps(sources or [])
        cur.execute(
            f"""
            INSERT INTO chat_history (customer_id, user_message, assistant_response, sources_json, is_deleted)
            VALUES ({ph}, {ph}, {ph}, {ph}, FALSE)
            """,
            (customer_id, user_message, assistant_response, sources_str),
        )
        conn.commit()
    finally:
        conn.close()


def soft_delete_chat_message(chat_id: int, customer_id: str):
    """
    Soft-delete chat message: Marks is_deleted = TRUE so it is hidden from UI,
    while PERMANENTLY PRESERVING chat records in Database for future audit & safety.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            f"UPDATE chat_history SET is_deleted = TRUE WHERE id = {ph} AND customer_id = {ph}",
            (chat_id, customer_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_chat_history(customer_id: str, include_deleted: bool = False) -> list[dict]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"

        # Fetch soft-deleted filenames for this user to exclude chats of deleted files
        cur.execute(
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

        if include_deleted:
            query = f"SELECT * FROM chat_history WHERE customer_id = {ph} ORDER BY created_at ASC"
        else:
            query = f"SELECT * FROM chat_history WHERE customer_id = {ph} AND (is_deleted = FALSE OR is_deleted IS NULL) ORDER BY created_at ASC"

        cur.execute(query, (customer_id,))
        rows = cur.fetchall()
        result = []
        for r in rows:
            if isinstance(r, dict):
                d = dict(r)
            else:
                cols = [col[0] for col in cur.description]
                d = dict(zip(cols, r))
            
            try:
                d["sources"] = json.loads(d.get("sources_json") or "[]")
            except Exception:
                d["sources"] = []

            # If not including deleted, check if sources belong ONLY to soft-deleted documents
            if not include_deleted and d["sources"]:
                non_deleted_sources = [s for s in d["sources"] if s.get("source") and s.get("source") not in deleted_filenames]
                has_deleted_sources = any(s.get("source") in deleted_filenames for s in d["sources"])
                if not non_deleted_sources and has_deleted_sources:
                    # Skip chat item if all referenced sources belong to deleted documents
                    continue

            result.append(d)
        return result
    finally:
        conn.close()


def clear_user_chat_history(customer_id: str):
    """
    Soft-delete all chat history for a customer (sets is_deleted = TRUE).
    Data remains permanently saved in DB for audit & compliance.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            f"UPDATE chat_history SET is_deleted = TRUE WHERE customer_id = {ph}",
            (customer_id,),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_chat_count(customer_id: str) -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            f"SELECT COUNT(*) FROM chat_history WHERE customer_id = {ph} AND (is_deleted = FALSE OR is_deleted IS NULL)",
            (customer_id,),
        )
        row = cur.fetchone()
        if isinstance(row, dict):
            return list(row.values())[0]
        return row[0] if row else 0
    finally:
        conn.close()


def reset_customer_workspace(customer_id: str):
    """
    Clears active workspace data (soft-deletes documents & chat history)
    and purges vector store for a clean fresh workspace.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(f"UPDATE documents SET is_deleted = TRUE WHERE customer_id = {ph}", (customer_id,))
        cur.execute(f"UPDATE chat_history SET is_deleted = TRUE WHERE customer_id = {ph}", (customer_id,))
        conn.commit()
    finally:
        conn.close()

    try:
        from src.vector_store import get_vector_store
        vs = get_vector_store()
        if hasattr(vs, "_collection"):
            try:
                vs._collection.delete(where={"user_id": customer_id})
            except Exception:
                pass
    except Exception:
        pass


def update_user_profile(user_id: int, full_name: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
            f"UPDATE users SET full_name = {ph} WHERE id = {ph}",
            (full_name, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_user_password(user_id: int, password_hash: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur.execute(
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


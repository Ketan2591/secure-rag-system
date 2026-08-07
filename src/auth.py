import secrets
import string
import sqlite3
import bcrypt

from src.database import get_connection


def hash_password(password: str) -> str:
    """
    Convert a plain password into a secure hash.
    """
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )
    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Check whether the entered password matches
    the stored password hash.
    """
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def generate_customer_id() -> str:
    """
    Generate IDs like:
    CUS_A7F91C
    """
    characters = string.ascii_uppercase + string.digits
    random_part = "".join(
        secrets.choice(characters)
        for _ in range(6)
    )
    return f"CUS_{random_part}"


def register_user(
    full_name: str,
    email: str,
    password: str,
):
    """
    Register a new user.
    """
    email = email.strip().lower()
    conn = get_connection()
    try:
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur = conn.cursor()

        cur.execute(
            f"SELECT id FROM users WHERE email = {ph}",
            (email,),
        )

        row = cur.fetchone()
        if row:
            return False, "Email already registered."

        customer_id = generate_customer_id()
        password_hash = hash_password(password)

        cur.execute(
            f"""
            INSERT INTO users (customer_id, full_name, email, password_hash)
            VALUES ({ph}, {ph}, {ph}, {ph})
            """,
            (customer_id, full_name, email, password_hash),
        )
        conn.commit()
        return True, customer_id
    finally:
        conn.close()


def login_user(
    email: str,
    password: str,
):
    """
    Authenticate a user.
    """
    email = email.strip().lower()
    conn = get_connection()
    try:
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur = conn.cursor()

        cur.execute(
            f"SELECT * FROM users WHERE email = {ph} AND is_active = TRUE",
            (email,),
        )

        row = cur.fetchone()
        if not row:
            return False, "Invalid email or password."

        # Convert row to dict if sqlite tuple row
        if isinstance(row, dict):
            user = row
        elif hasattr(row, "_asdict"):
            user = row._asdict()
        else:
            # Fallback for tuple row
            cols = [col[0] for col in cur.description]
            user = dict(zip(cols, row))

        if not verify_password(password, user["password_hash"]):
            return False, "Invalid email or password."

        cur.execute(
            f"UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = {ph}",
            (user["id"],),
        )
        conn.commit()
        return True, user
    finally:
        conn.close()
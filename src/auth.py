"""
Everything related to accounts: registering a user, logging one in, and the
password hashing behind both. Also home to a small annoyance we have to deal
with because the app can run on either SQLite (local dev) or Postgres (prod)
-- the two drivers hand back query rows in different shapes, so login_user()
has to normalize a row into a plain dict before it can be used safely.
"""

import secrets
import string
import sqlite3
import bcrypt

from src.database import get_connection


# Takes the plain password, converts it to bytes, and hashes it with bcrypt using a random salt so the same password never produces the same hash twice.
# The final hash is converted back to a normal string so it can be stored in the database.
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )
    return hashed.decode("utf-8")


# Checks the password entered at login against the stored hash by re-hashing the entered password with the same salt embedded in the stored hash and comparing them.
# Returns True if they match, False otherwise.
def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


# Builds a unique customer ID like "CUS_A7F91C" by picking 6 random uppercase letters/digits using a secure random generator and adding the "CUS_" prefix.
def generate_customer_id() -> str:
    characters = string.ascii_uppercase + string.digits
    random_part = "".join(
        secrets.choice(characters)
        for _ in range(6)
    )
    return f"CUS_{random_part}"


# Cleans up the email, checks if it is already registered, and if not, generates a customer ID, hashes the password, and inserts the new user into the database.
# Returns (False, error message) if the email already exists, otherwise (True, customer_id). The database connection is always closed at the end.
def register_user(
    full_name: str,
    email: str,
    password: str,
):
    email = email.strip().lower()
    conn = get_connection()
    try:
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur = conn.cursor()

        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"SELECT id FROM users WHERE email = {ph}",
            (email,),
        )

        row = cur.fetchone()
        if row:
            return False, "Email already registered."

        customer_id = generate_customer_id()
        password_hash = hash_password(password)

        cur.execute(
            # pyrefly: ignore [bad-argument-type]
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


# Looks up the active user by email, normalizes the DB row into a dict (since SQLite/Postgres return different row shapes), and checks the password against the stored hash.
# On success it updates last_login and returns (True, user); on any failure it returns (False, "Invalid email or password").
def login_user(
    email: str,
    password: str,
):
    email = email.strip().lower()
    conn = get_connection()
    try:
        is_sqlite = isinstance(conn, sqlite3.Connection)
        ph = "?" if is_sqlite else "%s"
        cur = conn.cursor()

        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"SELECT * FROM users WHERE email = {ph} AND is_active = TRUE",
            (email,),
        )

        row = cur.fetchone()
        if not row:
            return False, "Invalid email or password."

        # sqlite3 (with a row_factory) can hand back a dict, psycopg's NamedTupleCursor gives us an object with _asdict(),
        # and a plain cursor just gives a bare tuple. This normalizes all three cases into one plain dict called "user".
        if isinstance(row, dict):
            user = row
        elif hasattr(row, "_asdict"):
            user = row._asdict()  # type: ignore[attr-defined]
        else:
            # Fallback for tuple row
            cols = [col[0] for col in cur.description] # type: ignore
            user = dict(zip(cols, row))

        if not verify_password(password, user["password_hash"]):
            return False, "Invalid email or password."

        cur.execute(
            # pyrefly: ignore [bad-argument-type]
            f"UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = {ph}",
            (user["id"],),
        )
        conn.commit()
        return True, user
    finally:
        conn.close()

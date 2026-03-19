"""
Authentication — simple username/password stored as salted hash in SQLite.
No external auth service required; works fully offline.
"""
import sqlite3
import hashlib
import secrets
import streamlit as st
from utils.database import DB_NAME


# ── DB SETUP ─────────────────────────────────────────────────────────────────
def init_auth_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    UNIQUE NOT NULL,
                salt     TEXT    NOT NULL,
                pw_hash  TEXT    NOT NULL,
                name     TEXT    DEFAULT '',
                dept     TEXT    DEFAULT '',
                current_sem INTEGER DEFAULT 1,
                theme    TEXT    DEFAULT 'dark'
            )
        """)
        conn.commit()


# ── HASHING ───────────────────────────────────────────────────────────────────
def _hash(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


# ── CRUD ─────────────────────────────────────────────────────────────────────
def register_user(username: str, password: str, name: str, dept: str, sem: int) -> bool:
    salt    = secrets.token_hex(16)
    pw_hash = _hash(password, salt)
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute(
                "INSERT INTO users (username,salt,pw_hash,name,dept,current_sem) VALUES (?,?,?,?,?,?)",
                (username.strip().lower(), salt, pw_hash, name, dept, sem),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def verify_user(username: str, password: str):
    """Returns user row dict if valid, else None."""
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username=?", (username.strip().lower(),)
        ).fetchone()
    if row is None:
        return None
    cols = ["id","username","salt","pw_hash","name","dept","current_sem","theme"]
    user = dict(zip(cols, row))
    if _hash(password, user["salt"]) == user["pw_hash"]:
        return user
    return None


def update_user(user_id: int, name: str, dept: str, sem: int):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE users SET name=?,dept=?,current_sem=? WHERE id=?",
            (name, dept, sem, user_id),
        )


def update_theme(user_id: int, theme: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE users SET theme=? WHERE id=?", (theme, user_id))


def change_password(user_id: int, old_pw: str, new_pw: str) -> bool:
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute("SELECT salt,pw_hash FROM users WHERE id=?", (user_id,)).fetchone()
    if row is None:
        return False
    salt, pw_hash = row
    if _hash(old_pw, salt) != pw_hash:
        return False
    new_salt = secrets.token_hex(16)
    new_hash = _hash(new_pw, new_salt)
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE users SET salt=?,pw_hash=? WHERE id=?", (new_salt, new_hash, user_id))
    return True


def get_all_usernames() -> list:
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute("SELECT username FROM users").fetchall()
    return [r[0] for r in rows]


# ── STREAMLIT SESSION HELPERS ────────────────────────────────────────────────
def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def current_user() -> dict | None:
    return st.session_state.get("user")


def login(user: dict):
    st.session_state.user    = user
    st.session_state.entered = True
    st.session_state.page    = "dashboard"


def logout():
    for key in ["user", "entered", "page", "sub_id"]:
        st.session_state.pop(key, None)

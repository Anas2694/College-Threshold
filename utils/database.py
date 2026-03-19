import sqlite3
import pandas as pd

DB_NAME = "vtu_predictor.db"

# ── NUMERIC HELPER ───────────────────────────────────────────────────────────
def _num(x):
    if isinstance(x, (bytes, bytearray)):
        try:
            x = x.decode()
        except Exception:
            pass
    try:
        return float(x)
    except Exception:
        return 0.0


# ── INIT ─────────────────────────────────────────────────────────────────────
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                credits INTEGER,
                cie1 REAL DEFAULT 0, cie2 REAL DEFAULT 0, cie3 REAL DEFAULT 0,
                quiz_score REAL DEFAULT 0, aat_score REAL DEFAULT 0, lab_score REAL DEFAULT 0,
                quiz_max REAL DEFAULT 10, aat_max REAL DEFAULT 10, lab_max REAL DEFAULT 25,
                cie_max REAL DEFAULT 40,
                cie_weight REAL DEFAULT 20, lab_weight REAL DEFAULT 20,
                quiz_weight REAL DEFAULT 5, aat_weight REAL DEFAULT 5,
                extra_weight REAL DEFAULT 0, extra_score REAL DEFAULT 0, extra_max REAL DEFAULT 0,
                attended_classes INTEGER DEFAULT 0,
                total_classes INTEGER DEFAULT 0,
                default_total_classes INTEGER DEFAULT 40,
                see_score REAL DEFAULT -1,
                semester INTEGER DEFAULT 1
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, dept TEXT,
                current_sem INTEGER DEFAULT 1,
                photo BLOB
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS past_semesters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semester INTEGER,
                subject_name TEXT,
                credits INTEGER,
                grade TEXT,
                grade_points REAL
            )
        """)

        # Migrations — add new columns safely
        migrations = [
            ("cie_max",    "REAL DEFAULT 40"),
            ("cie_weight", "REAL DEFAULT 20"),
            ("lab_weight", "REAL DEFAULT 20"),
            ("quiz_weight","REAL DEFAULT 5"),
            ("aat_weight", "REAL DEFAULT 5"),
            ("extra_weight","REAL DEFAULT 0"),
            ("extra_score","REAL DEFAULT 0"),
            ("extra_max",  "REAL DEFAULT 0"),
            ("see_score",  "REAL DEFAULT -1"),
            ("semester",   "INTEGER DEFAULT 1"),
        ]
        for col, spec in migrations:
            try:
                c.execute(f"ALTER TABLE subjects ADD COLUMN {col} {spec}")
            except Exception:
                pass
        try:
            c.execute("ALTER TABLE user_profile ADD COLUMN current_sem INTEGER DEFAULT 1")
        except Exception:
            pass
        conn.commit()


# ── SUBJECTS ─────────────────────────────────────────────────────────────────
def get_subjects(sem=None):
    with sqlite3.connect(DB_NAME) as conn:
        if sem:
            df = pd.read_sql_query(
                "SELECT * FROM subjects WHERE semester=?", conn, params=[sem]
            )
        else:
            df = pd.read_sql_query("SELECT * FROM subjects", conn)

    num_cols = [
        "credits","cie1","cie2","cie3","quiz_score","aat_score","lab_score",
        "quiz_max","aat_max","lab_max","cie_max","cie_weight","lab_weight",
        "quiz_weight","aat_weight","extra_weight","extra_score","extra_max",
        "attended_classes","total_classes","default_total_classes","see_score","semester",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str), errors="coerce").fillna(0)
    return df


def add_subject(name, credits, semester=1):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute(
                "INSERT INTO subjects (name,credits,total_classes,default_total_classes,semester) VALUES (?,?,?,?,?)",
                (name, credits, 0, 10 * int(credits), semester),
            )
            return True
        except Exception:
            return False


def save_marks(subject_id, data):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """UPDATE subjects
               SET cie1=?,cie2=?,cie3=?,quiz_score=?,aat_score=?,lab_score=?,
                   quiz_max=?,aat_max=?,lab_max=?,extra_score=?,extra_max=?
               WHERE id=?""",
            data,
        )


def save_see(subject_id, see):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE subjects SET see_score=? WHERE id=?", (see, subject_id)
        )


def save_weights(subject_id, cw, lw, qw, aw, ew, ex, ex_max):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """UPDATE subjects
               SET cie_weight=?,lab_weight=?,quiz_weight=?,aat_weight=?,
                   extra_weight=?,extra_score=?,extra_max=?
               WHERE id=?""",
            (cw, lw, qw, aw, ew, ex, ex_max, subject_id),
        )


def save_attendance(subject_id, attended, conducted):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE subjects SET attended_classes=?,total_classes=? WHERE id=?",
            (attended, conducted, subject_id),
        )


def update_planned_classes(subject_id, planned):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE subjects SET default_total_classes=? WHERE id=?",
            (planned, subject_id),
        )


def delete_subject(subject_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM subjects WHERE id=?", (subject_id,))


def get_subject_by_id(subject_id):
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM subjects WHERE id=?", conn, params=[subject_id]
        )
    row = df.iloc[0]
    for col in row.index:
        try:
            row[col] = _num(row[col])
        except Exception:
            pass
    return row


# ── PROFILE ──────────────────────────────────────────────────────────────────
def save_profile(name, dept, sem, photo):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM user_profile")
        c.execute(
            "INSERT INTO user_profile (name,dept,current_sem,photo) VALUES (?,?,?,?)",
            (name, dept, sem, photo),
        )
        conn.commit()


def get_profile():
    with sqlite3.connect(DB_NAME) as conn:
        try:
            df = pd.read_sql_query("SELECT * FROM user_profile LIMIT 1", conn)
            return df.iloc[0] if not df.empty else None
        except Exception:
            return None


# ── PAST SEMESTERS ───────────────────────────────────────────────────────────
GP_MAP = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}


def get_past():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(
            "SELECT * FROM past_semesters ORDER BY semester", conn
        )


def add_past_grade(sem, subject_name, credits, grade):
    gp = GP_MAP.get(grade, 0)
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO past_semesters (semester,subject_name,credits,grade,grade_points) VALUES (?,?,?,?,?)",
            (sem, subject_name, credits, grade, gp),
        )


def delete_past_grade(record_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM past_semesters WHERE id=?", (record_id,))

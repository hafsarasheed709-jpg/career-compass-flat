"""SQLite persistence layer. All queries are parameterised.

Set the CAREER_COMPASS_DB environment variable to store the database elsewhere
(for example on a mounted volume when deploying). No passwords or sensitive
identifiers are stored - only a display name and career-related answers.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from utils import from_json_list, to_json_list, utc_now

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "career_compass.db"


class DatabaseError(RuntimeError):
    """Raised for any database failure, with a readable message."""


def get_db_path(db_path=None) -> Path:
    return Path(db_path or os.environ.get("CAREER_COMPASS_DB") or DEFAULT_DB_PATH)


@contextmanager
def connect(db_path=None):
    path = get_db_path(db_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
    except (sqlite3.Error, OSError) as exc:
        raise DatabaseError(f"Cannot open database at {path}: {exc}") from exc
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise DatabaseError(f"Database error: {exc}") from exc
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL,
    education_level TEXT NOT NULL,
    field_of_study TEXT NOT NULL,
    technical_skills TEXT NOT NULL DEFAULT '[]',
    soft_skills TEXT NOT NULL DEFAULT '[]',
    career_interests TEXT NOT NULL DEFAULT '[]',
    career_goal TEXT NOT NULL DEFAULT '',
    learning_areas TEXT NOT NULL DEFAULT '[]',
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
    updated_at TEXT NOT NULL,
    UNIQUE (profile_id, skill)
);
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    career TEXT NOT NULL,
    match_score REAL NOT NULL,
    rank INTEGER NOT NULL,
    generated_at TEXT NOT NULL,
    UNIQUE (profile_id, career)
);
CREATE TABLE IF NOT EXISTS roadmap_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    career TEXT NOT NULL,
    task_key TEXT NOT NULL,
    module TEXT NOT NULL,
    task_type TEXT NOT NULL,
    title TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    completed_at TEXT,
    UNIQUE (profile_id, career, task_key)
);
CREATE INDEX IF NOT EXISTS idx_tasks_profile ON roadmap_tasks(profile_id, career);
"""


def init_db(db_path=None) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)


# ----------------------------------------------------------------- profiles
def _profile_from_row(row) -> dict:
    d = dict(row)
    for key in ("technical_skills", "soft_skills", "career_interests", "learning_areas"):
        d[key] = from_json_list(d[key])
    d["is_demo"] = bool(d["is_demo"])
    return d


def create_profile(data: dict, is_demo: bool = False, db_path=None) -> int:
    now = utc_now()
    with connect(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO profiles (display_name, education_level, field_of_study, technical_skills,
               soft_skills, career_interests, career_goal, learning_areas, is_demo, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data["display_name"].strip(), data["education_level"], data["field_of_study"].strip(),
             to_json_list(data.get("technical_skills")), to_json_list(data.get("soft_skills")),
             to_json_list(data.get("career_interests")), (data.get("career_goal") or "").strip(),
             to_json_list(data.get("learning_areas")), int(is_demo), now, now),
        )
        return int(cur.lastrowid)


def update_profile(profile_id: int, data: dict, db_path=None) -> None:
    with connect(db_path) as conn:
        cur = conn.execute(
            """UPDATE profiles SET display_name=?, education_level=?, field_of_study=?, technical_skills=?,
               soft_skills=?, career_interests=?, career_goal=?, learning_areas=?, updated_at=? WHERE id=?""",
            (data["display_name"].strip(), data["education_level"], data["field_of_study"].strip(),
             to_json_list(data.get("technical_skills")), to_json_list(data.get("soft_skills")),
             to_json_list(data.get("career_interests")), (data.get("career_goal") or "").strip(),
             to_json_list(data.get("learning_areas")), utc_now(), profile_id),
        )
        if cur.rowcount == 0:
            raise DatabaseError("Profile not found.")


def get_profile(profile_id: int, db_path=None) -> dict | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone()
    return _profile_from_row(row) if row else None


def list_profiles(db_path=None) -> list[dict]:
    with connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM profiles ORDER BY id").fetchall()
    return [_profile_from_row(r) for r in rows]


def delete_profile(profile_id: int, db_path=None) -> None:
    with connect(db_path) as conn:
        conn.execute("DELETE FROM profiles WHERE id=?", (profile_id,))


# -------------------------------------------------------------- assessments
def save_assessment(profile_id: int, scores: dict, db_path=None) -> None:
    now = utc_now()
    with connect(db_path) as conn:
        conn.executemany(
            """INSERT INTO assessments (profile_id, skill, score, updated_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(profile_id, skill) DO UPDATE SET score=excluded.score, updated_at=excluded.updated_at""",
            [(profile_id, skill, int(score), now) for skill, score in scores.items()],
        )


def get_assessment(profile_id: int, db_path=None) -> dict[str, int]:
    with connect(db_path) as conn:
        rows = conn.execute("SELECT skill, score FROM assessments WHERE profile_id=?", (profile_id,)).fetchall()
    return {r["skill"]: r["score"] for r in rows}


def get_assessment_updated_at(profile_id: int, db_path=None) -> str | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT MAX(updated_at) AS t FROM assessments WHERE profile_id=?", (profile_id,)).fetchone()
    return row["t"] if row else None


def reset_assessment(profile_id: int, db_path=None) -> None:
    with connect(db_path) as conn:
        conn.execute("DELETE FROM assessments WHERE profile_id=?", (profile_id,))
        conn.execute("DELETE FROM recommendations WHERE profile_id=?", (profile_id,))


# ---------------------------------------------------------- recommendations
def save_recommendations(profile_id: int, recs: list[dict], db_path=None) -> None:
    now = utc_now()
    with connect(db_path) as conn:
        conn.execute("DELETE FROM recommendations WHERE profile_id=?", (profile_id,))
        conn.executemany(
            "INSERT INTO recommendations (profile_id, career, match_score, rank, generated_at) VALUES (?, ?, ?, ?, ?)",
            [(profile_id, r["career"], float(r["match"]), i + 1, now) for i, r in enumerate(recs)],
        )


def get_recommendations(profile_id: int, db_path=None) -> list[dict]:
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT career, match_score, rank, generated_at FROM recommendations WHERE profile_id=? ORDER BY rank",
            (profile_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ------------------------------------------------------------ roadmap tasks
def ensure_roadmap_tasks(profile_id: int, career: str, tasks: list[dict], db_path=None) -> None:
    """Insert any tasks missing for this profile/career (existing progress is kept)."""
    with connect(db_path) as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO roadmap_tasks (profile_id, career, task_key, module, task_type, title)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [(profile_id, career, t["key"], t["module"], t["type"], t["title"]) for t in tasks],
        )


def get_roadmap_tasks(profile_id: int, career: str, db_path=None) -> list[dict]:
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM roadmap_tasks WHERE profile_id=? AND career=? ORDER BY id", (profile_id, career)
        ).fetchall()
    return [{**dict(r), "completed": bool(r["completed"])} for r in rows]


def set_task_completed(profile_id: int, task_id: int, completed: bool, db_path=None) -> None:
    with connect(db_path) as conn:
        conn.execute(
            "UPDATE roadmap_tasks SET completed=?, completed_at=? WHERE id=? AND profile_id=?",
            (int(completed), utc_now() if completed else None, task_id, profile_id),
        )


def roadmap_progress(profile_id: int, db_path=None) -> list[dict]:
    """Per-career totals for every roadmap the learner has opened."""
    with connect(db_path) as conn:
        rows = conn.execute(
            """SELECT career, COUNT(*) AS total, SUM(completed) AS done FROM roadmap_tasks
               WHERE profile_id=? GROUP BY career ORDER BY career""",
            (profile_id,),
        ).fetchall()
    return [{"career": r["career"], "total": r["total"], "done": int(r["done"] or 0)} for r in rows]


def recent_completed_tasks(profile_id: int, limit: int = 5, db_path=None) -> list[dict]:
    with connect(db_path) as conn:
        rows = conn.execute(
            """SELECT career, title, completed_at FROM roadmap_tasks
               WHERE profile_id=? AND completed=1 ORDER BY completed_at DESC, id DESC LIMIT ?""",
            (profile_id, int(limit)),
        ).fetchall()
    return [dict(r) for r in rows]

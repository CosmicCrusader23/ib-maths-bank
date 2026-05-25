"""SQLite schema + helpers."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "questions.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT    NOT NULL,
    source_id       TEXT    NOT NULL,
    source_url      TEXT,
    subject         TEXT    NOT NULL,                    -- 'maths_aa' | 'maths_ai' | 'physics' | ...
    course          TEXT,                                -- legacy: 'AA' | 'AI' | null for physics
    level           TEXT,                                -- 'SL' | 'HL' | 'BOTH'
    paper           TEXT,
    year            TEXT,
    session         TEXT,
    topic_id        TEXT    NOT NULL,                    -- subject-scoped
    subtopic        TEXT,
    title           TEXT,
    question_html   TEXT    NOT NULL,
    solution_html   TEXT,
    examiners_html  TEXT,
    extra_json      TEXT,
    UNIQUE(source, source_id)
);

CREATE INDEX IF NOT EXISTS idx_q_subject ON questions(subject);
CREATE INDEX IF NOT EXISTS idx_q_topic   ON questions(subject, topic_id);
CREATE INDEX IF NOT EXISTS idx_q_level   ON questions(level);
CREATE INDEX IF NOT EXISTS idx_q_source  ON questions(source);
"""


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert_questions(conn: sqlite3.Connection, rows: Iterable[dict[str, Any]]) -> int:
    cols = (
        "source", "source_id", "source_url", "subject", "course", "level",
        "paper", "year", "session", "topic_id", "subtopic", "title",
        "question_html", "solution_html", "examiners_html", "extra_json",
    )
    placeholders = ",".join("?" for _ in cols)
    update_clause = ",".join(f"{c}=excluded.{c}" for c in cols if c not in ("source", "source_id"))
    sql = (
        f"INSERT INTO questions ({','.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT(source, source_id) DO UPDATE SET {update_clause}"
    )
    n = 0
    for r in rows:
        extra = r.get("extra")
        values = [
            r.get("source"), r.get("source_id"), r.get("source_url"),
            r.get("subject"), r.get("course"), r.get("level"),
            r.get("paper"), r.get("year"), r.get("session"),
            r.get("topic_id"), r.get("subtopic"), r.get("title"),
            r.get("question_html") or "", r.get("solution_html"),
            r.get("examiners_html"),
            json.dumps(extra, ensure_ascii=False) if extra is not None else None,
        ]
        conn.execute(sql, values)
        n += 1
    conn.commit()
    return n


def stats(conn: sqlite3.Connection) -> dict[str, Any]:
    cur = conn.cursor()
    out = {"total": cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]}
    out["by_subject"] = dict(cur.execute(
        "SELECT subject, COUNT(*) FROM questions GROUP BY subject ORDER BY 2 DESC"
    ).fetchall())
    out["by_source"] = dict(cur.execute(
        "SELECT source, COUNT(*) FROM questions GROUP BY source ORDER BY 2 DESC"
    ).fetchall())
    out["by_topic"] = dict(cur.execute(
        "SELECT subject || ':' || topic_id, COUNT(*) FROM questions GROUP BY subject, topic_id ORDER BY 1"
    ).fetchall())
    return out

"""Export the SQLite DB to per-topic JSON files for the static site.

Layout written under ``site/public/data/``::

    index.json                     -- topics + counts + source list
    topic-{1..5}.json              -- list of question metadata for that topic
    questions/{id}.json            -- full HTML payload, lazy-loaded by the site

The per-topic file contains lightweight rows so the listing page is small;
the full question/solution HTML lives in ``questions/{id}.json`` and is fetched
when the user opens a question.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import db
from .topics import TOPICS


def _row_summary(r) -> dict:
    return {
        "id": r["id"],
        "source": r["source"],
        "course": r["course"],
        "level": r["level"],
        "paper": r["paper"],
        "year": r["year"],
        "session": r["session"],
        "subtopic": r["subtopic"],
        "title": r["title"],
        "topic_id": r["topic_id"],
    }


def _row_full(r) -> dict:
    out = _row_summary(r)
    out.update({
        "source_url": r["source_url"],
        "question_html": r["question_html"],
        "solution_html": r["solution_html"],
        "examiners_html": r["examiners_html"],
    })
    return out


def run(out_dir: Path) -> Path:
    conn = db.connect()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "questions").mkdir(exist_ok=True)

    cur = conn.cursor()
    counts = {}
    for tid in TOPICS:
        rows = cur.execute(
            "SELECT * FROM questions WHERE topic_id=? ORDER BY source, course, level, paper, session, title",
            (tid,),
        ).fetchall()
        summaries = [_row_summary(r) for r in rows]
        (out_dir / f"topic-{tid}.json").write_text(
            json.dumps(summaries, ensure_ascii=False),
            encoding="utf-8",
        )
        counts[tid] = len(summaries)
        for r in rows:
            (out_dir / "questions" / f"{r['id']}.json").write_text(
                json.dumps(_row_full(r), ensure_ascii=False),
                encoding="utf-8",
            )

    sources = dict(cur.execute(
        "SELECT source, COUNT(*) FROM questions GROUP BY source ORDER BY 2 DESC"
    ).fetchall())

    index = {
        "topics": [
            {"id": tid, "name": name, "count": counts.get(tid, 0)}
            for tid, name in TOPICS.items()
        ],
        "sources": sources,
        "total": sum(counts.values()),
    }
    (out_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    return out_dir

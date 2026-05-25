"""Export the SQLite DB to per-subject/per-topic JSON for the site.

Layout written under ``site/public/data/``::

    index.json                                          -- subjects + counts
    {subject}/index.json                                -- topics within subject
    {subject}/topic-{topic_id}.json                     -- list summary
    questions/{id}.json                                 -- full HTML payload
"""
from __future__ import annotations

import json
from pathlib import Path

from . import db
from .topics import SUBJECTS, SUBJECT_LABELS


def _summary(r) -> dict:
    return {
        "id": r["id"],
        "source": r["source"],
        "subject": r["subject"],
        "course": r["course"],
        "level": r["level"],
        "paper": r["paper"],
        "year": r["year"],
        "session": r["session"],
        "subtopic": r["subtopic"],
        "title": r["title"],
        "topic_id": r["topic_id"],
    }


def _full(r) -> dict:
    out = _summary(r)
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
    subjects_meta = []
    for subject_key, topics in SUBJECTS.items():
        subj_dir = out_dir / subject_key
        subj_dir.mkdir(parents=True, exist_ok=True)
        topic_meta = []
        subject_total = 0
        for tid, name in topics.items():
            rows = cur.execute(
                "SELECT * FROM questions WHERE subject=? AND topic_id=? "
                "ORDER BY source, course, level, paper, session, title",
                (subject_key, tid),
            ).fetchall()
            summaries = [_summary(r) for r in rows]
            (subj_dir / f"topic-{tid}.json").write_text(
                json.dumps(summaries, ensure_ascii=False), encoding="utf-8",
            )
            topic_meta.append({"id": tid, "name": name, "count": len(summaries)})
            subject_total += len(summaries)
            for r in rows:
                (out_dir / "questions" / f"{r['id']}.json").write_text(
                    json.dumps(_full(r), ensure_ascii=False), encoding="utf-8",
                )
        sources_in_subject = dict(cur.execute(
            "SELECT source, COUNT(*) FROM questions WHERE subject=? GROUP BY source ORDER BY 2 DESC",
            (subject_key,),
        ).fetchall())
        (subj_dir / "index.json").write_text(
            json.dumps({
                "subject": subject_key,
                "label": SUBJECT_LABELS.get(subject_key, subject_key),
                "topics": topic_meta,
                "sources": sources_in_subject,
                "total": subject_total,
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        subjects_meta.append({
            "key": subject_key,
            "label": SUBJECT_LABELS.get(subject_key, subject_key),
            "total": subject_total,
            "topic_count": len(topic_meta),
        })

    sources = dict(cur.execute(
        "SELECT source, COUNT(*) FROM questions GROUP BY source ORDER BY 2 DESC"
    ).fetchall())
    total = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]

    (out_dir / "index.json").write_text(
        json.dumps({
            "subjects": subjects_meta,
            "sources": sources,
            "total": total,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_dir

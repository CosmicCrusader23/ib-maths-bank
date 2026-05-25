"""Pestle (pirateIB) — IB QuestionBanks for Maths AA/AI and Physics.

Each per-subject JSON bank is a list of question objects with ``Question``,
``Markscheme``, ``Examiners report``, ``question_id``, ``topics`` and
``subtopics`` fields. The banks live as git-LFS objects on git.pirateib.sh,
fetched once via the LFS media URL.

Each row in the JSON has its topic slug already mapped onto the IB syllabus,
so we just route via PESTLE_TOPIC_MAP into our (subject, topic_id) pair.
"""
from __future__ import annotations

import json
import re
from typing import Iterator

from ..db import upsert_questions
from ..http import CACHE, fetch
from ..topics import PESTLE_TOPIC_MAP

BASE = "https://git.pirateib.sh/pirateIB/pestle/media/branch/master/assets/jsonqb"

# (bank_key, json filename, subject_resolver)
#   subject_resolver: ('maths', tid) -> 'maths_aa'/'maths_ai' | ('physics', tid) -> 'physics'
BANKS = [
    ("Math AA QB",  "Math%20AA%20QB.json",  "maths_aa"),
    ("Math AI QB",  "Math%20AI%20QB.json",  "maths_ai"),
    ("Physics QB",  "Physics%20QB.json",    "physics"),
]

# question_id formats (pestle): SPM.1.SL.TZ0.8 | 18M.2.AHL.TZ2.H_10 | 18N.2.HL.TZ0.2
ID_RE = re.compile(
    r"^(?P<session>SPM|EXM|EXN|\d{2}[MN])\."
    r"(?P<paper>\d)\."
    r"(?P<level>SL|AHL|HL)\."
    r"(?P<tz>TZ\d)\."
    r"(?P<qn>.+)$"
)


def _session_to_year(session: str) -> str | None:
    if not session or session in {"SPM", "EXM", "EXN"}:
        return None
    return str(2000 + int(session[:2]))


def _parse_id(qid: str) -> dict[str, str | None]:
    m = ID_RE.match(qid or "")
    if not m:
        return {"session": None, "paper": None, "level": None, "tz": None, "qn": qid}
    g = m.groupdict()
    return {
        "session": g["session"],
        "paper": g["paper"],
        "level": "HL" if g["level"] == "AHL" else g["level"],
        "tz": g["tz"],
        "qn": g["qn"],
    }


def _resolve_subject(course_subject: str, kind: str) -> str | None:
    """Resolve a (kind, topic_id) marker to a real subject key.

    For physics, the marker is already 'physics'. For maths, the marker is
    'maths' and we use the bank's `course_subject` ('maths_aa' or 'maths_ai').
    """
    if kind == "physics":
        return "physics"
    if kind == "maths":
        return course_subject if course_subject.startswith("maths_") else None
    return None


def _row_iter(bank_label: str, course_subject: str, raw: list[dict]) -> Iterator[dict]:
    course_legacy = {"maths_aa": "AA", "maths_ai": "AI"}.get(course_subject)
    for q in raw:
        topics = q.get("topics") or []
        routes = []
        for t in topics:
            if t in PESTLE_TOPIC_MAP:
                kind, tid = PESTLE_TOPIC_MAP[t]
                subj = _resolve_subject(course_subject, kind)
                if subj:
                    routes.append((subj, tid))
        if not routes:
            continue
        qid = q.get("question_id") or ""
        meta = _parse_id(qid)
        subtopics = q.get("subtopics") or []
        for subj, tid in routes:
            yield {
                "source": "pestle",
                "source_id": f"{bank_label}:{qid}:{subj}:{tid}",
                "source_url": "https://pestle.pages.dev/app/",
                "subject": subj,
                "course": course_legacy,
                "level": meta["level"],
                "paper": meta["paper"],
                "year": _session_to_year(meta["session"] or ""),
                "session": meta["session"],
                "topic_id": tid,
                "subtopic": ", ".join(subtopics) if subtopics else None,
                "title": qid,
                "question_html": q.get("Question") or "",
                "solution_html": q.get("Markscheme"),
                "examiners_html": q.get("Examiners report"),
                "extra": {
                    "tz": meta["tz"],
                    "qn": meta["qn"],
                    "subtopics": subtopics,
                },
            }


def ingest(conn) -> int:
    n = 0
    for bank_label, filename, course_subject in BANKS:
        url = f"{BASE}/{filename}"
        dest = CACHE / "pestle" / f"{bank_label}.json"
        print(f"  pestle: fetching {bank_label}…")
        data = fetch(url, dest=dest)
        raw = json.loads(data)
        rows = list(_row_iter(bank_label, course_subject, raw))
        n += upsert_questions(conn, rows)
        print(f"  pestle: {bank_label}: {len(raw)} questions → {len(rows)} rows")
    return n

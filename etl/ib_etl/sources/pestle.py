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

BANKS = [
    ("Math AA QB",  "Math%20AA%20QB.json",  "maths", "AA"),
    ("Math AI QB",  "Math%20AI%20QB.json",  "maths", "AI"),
    ("Physics QB",  "Physics%20QB.json",    "physics", None),
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


def _row_iter(bank_label: str, subject: str, course: str | None, raw: list[dict]) -> Iterator[dict]:
    for q in raw:
        topics = q.get("topics") or []
        routes = []
        seen: set[str] = set()
        for t in topics:
            if t in PESTLE_TOPIC_MAP:
                kind, tid = PESTLE_TOPIC_MAP[t]
                if kind != subject:
                    continue
                if tid in seen:
                    continue
                seen.add(tid)
                routes.append(tid)
        if not routes:
            continue
        qid = q.get("question_id") or ""
        meta = _parse_id(qid)
        subtopics = q.get("subtopics") or []
        for tid in routes:
            yield {
                "source": "pestle",
                "source_id": f"{bank_label}:{qid}:{tid}",
                "source_url": "https://pestle.pages.dev/app/",
                "subject": subject,
                "course": course,
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
    for bank_label, filename, subject, course in BANKS:
        url = f"{BASE}/{filename}"
        dest = CACHE / "pestle" / f"{bank_label}.json"
        print(f"  pestle: fetching {bank_label}…")
        data = fetch(url, dest=dest)
        raw = json.loads(data)
        rows = list(_row_iter(bank_label, subject, course, raw))
        n += upsert_questions(conn, rows)
        print(f"  pestle: {bank_label}: {len(raw)} questions → {len(rows)} rows")
    return n

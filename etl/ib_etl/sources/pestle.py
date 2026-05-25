"""Pestle (pirateIB) — IB QuestionBanks for Math AA / AI.

The full per-subject JSON banks are stored as git-LFS objects on
git.pirateib.sh. We pull them once via the LFS media URL and parse them
straight into our schema.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterator

from ..db import upsert_questions
from ..http import CACHE, fetch
from ..topics import PESTLE_TOPIC_TO_ID

BASE = "https://git.pirateib.sh/pirateIB/pestle/media/branch/master/assets/jsonqb"
BANKS = {
    "AA": f"{BASE}/Math%20AA%20QB.json",
    "AI": f"{BASE}/Math%20AI%20QB.json",
}

# question_id formats (pestle):
#   SPM.1.SL.TZ0.8                 — Specimen paper, paper 1, SL, qn 8
#   18M.2.AHL.TZ2.H_10             — 2018 May session, paper 2, AHL (HL extension), qn H_10
#   18N.1.SL.TZ0.T_5               — 2018 November, paper 1, SL, qn T_5
ID_RE = re.compile(
    r"^(?P<session>SPM|EXM|EXN|\d{2}[MN])\."
    r"(?P<paper>\d)\."
    r"(?P<level>SL|AHL|HL)\."
    r"(?P<tz>TZ\d)\."
    r"(?P<qn>.+)$"
)


def _session_to_year(session: str) -> str | None:
    if session in {"SPM", "EXM", "EXN"}:
        return None
    # '18M' -> 2018, '24N' -> 2024
    yr = int(session[:2])
    return str(2000 + yr)


def _parse_id(qid: str) -> dict[str, str | None]:
    m = ID_RE.match(qid)
    if not m:
        return {"session": None, "paper": None, "level": None, "tz": None, "qn": qid}
    g = m.groupdict()
    return {
        "session": g["session"],
        "paper": g["paper"],
        # AHL is pestle-speak for the HL extension content; treat as HL for browsing
        "level": "HL" if g["level"] == "AHL" else g["level"],
        "tz": g["tz"],
        "qn": g["qn"],
    }


def _row_iter(course: str, raw: list[dict]) -> Iterator[dict]:
    for q in raw:
        topics = q.get("topics") or []
        # pestle puts every entry under exactly one numeric topic in practice;
        # if multiple, we duplicate so each topic page has it.
        topic_ids = [PESTLE_TOPIC_TO_ID[t] for t in topics if t in PESTLE_TOPIC_TO_ID]
        if not topic_ids:
            continue
        qid = q.get("question_id") or ""
        meta = _parse_id(qid)
        subtopics = q.get("subtopics") or []
        # one row per (question, topic_id) so a question shows up under each
        # of its topics on the site
        for topic_id in topic_ids:
            yield {
                "source": "pestle",
                "source_id": f"{course}:{qid}:{topic_id}",
                "source_url": "https://pestle.pages.dev/app/",
                "course": course,
                "level": meta["level"],
                "paper": meta["paper"],
                "year": _session_to_year(meta["session"] or ""),
                "session": meta["session"],
                "topic_id": topic_id,
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
    """Pull both AA and AI banks, parse, upsert. Returns rows touched."""
    n = 0
    for course, url in BANKS.items():
        dest = CACHE / "pestle" / f"Math {course} QB.json"
        print(f"  pestle: fetching {course}…")
        data = fetch(url, dest=dest)
        raw = json.loads(data)
        rows = list(_row_iter(course, raw))
        n += upsert_questions(conn, rows)
        print(f"  pestle: {course}: {len(raw)} questions → {len(rows)} rows")
    return n

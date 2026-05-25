"""Christos Nikolaidis MAA exercises.

The site is HTML with links out to per-subtopic PDFs hosted on Dropbox. Each
PDF filename encodes the AA syllabus section, e.g.::

    Math-AA-1.1-NUMBERS-ROUNDING.pdf
    Math-AA-5.23-MACLAURIN-SERIES-EXTENSION-OF-BINOMIAL-THEOREM_solutions.pdf

We ingest one row per *PDF set* (main / eco / solutions all bundled together)
since the actual question text lives in the PDF — extracting it would mean
heavy OCR/PDF parsing and isn't worth it for v1. Each row carries the PDF
links so the site can offer them as downloads.
"""
from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path

from bs4 import BeautifulSoup

from ..db import upsert_questions
from ..http import CACHE, fetch

INDEX_URL = "https://www.christosnikolaidis.com/en/maa-exercise/"

# Math-AA-1.1-NUMBERS-ROUNDING.pdf
# Math-AA-1.2-1.3-ARITHMETIC-SEQUENCES.pdf
# Math-AA-5.23-MACLAURIN-SERIES-EXTENSION-OF-BINOMIAL-THEOREM_solutions.pdf
NAME_RE = re.compile(
    r"Math-AA-"
    r"(?P<sections>(?:\d+\.\d+)(?:-\d+\.\d+)*)"      # one or more dotted sections
    r"-(?P<title>[A-Z0-9-]+?)"
    r"(?P<variant>_eco|_solutions)?"
    r"\.pdf$",
    re.IGNORECASE,
)


def _parse_filename(url: str) -> dict | None:
    fname = url.rsplit("/", 1)[-1].split("?", 1)[0]
    fname = html.unescape(fname)
    m = NAME_RE.search(fname)
    if not m:
        return None
    sections = m.group("sections").split("-")
    title = m.group("title").replace("-", " ").title()
    variant = (m.group("variant") or "").lstrip("_") or "main"
    topic_id = sections[0].split(".", 1)[0]   # leading digit = MAA topic
    if topic_id not in {"1", "2", "3", "4", "5"}:
        return None
    return {
        "fname": fname,
        "sections": sections,
        "title": title,
        "variant": variant,
        "topic_id": topic_id,
    }


def ingest(conn) -> int:
    dest = CACHE / "christos" / "index.html"
    print("  christos: fetching index…")
    raw = fetch(INDEX_URL, dest=dest)
    soup = BeautifulSoup(raw, "lxml")

    # Group variants of the same exercise together
    groups: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"variants": {}, "sections": None, "title": None, "topic_id": None}
    )
    for a in soup.find_all("a", href=True):
        href = html.unescape(a["href"])
        if "dropbox.com" not in href or ".pdf" not in href:
            continue
        meta = _parse_filename(href)
        if not meta:
            continue
        key = (meta["topic_id"], "-".join(meta["sections"]) + "-" + meta["title"])
        g = groups[key]
        g["variants"][meta["variant"]] = href
        g["sections"] = meta["sections"]
        g["title"] = meta["title"]
        g["topic_id"] = meta["topic_id"]

    rows = []
    for (topic_id, ident), g in sorted(groups.items()):
        sections = g["sections"]
        title = g["title"]
        variants = g["variants"]
        # Synthetic 'question' content: link block. Site renders as HTML.
        section_label = " / ".join(sections)
        links_html = "".join(
            f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener">'
            f'{html.escape(label)}</a></li>'
            for label, url in (
                ("Worksheet", variants.get("main")),
                ("Worksheet (no working space)", variants.get("eco")),
                ("Solutions", variants.get("solutions")),
            )
            if url
        )
        question_html = (
            f'<div class="src-christos">'
            f'<p><strong>Christos Nikolaidis — AA §{section_label}: {html.escape(title)}</strong></p>'
            f'<p>PDF worksheet bundled by syllabus subtopic.</p>'
            f'<ul>{links_html}</ul>'
            f"</div>"
        )
        solution_html = None
        if "solutions" in variants:
            solution_html = (
                f'<p><a href="{html.escape(variants["solutions"])}" target="_blank" '
                f'rel="noopener">Open solutions PDF</a></p>'
            )

        rows.append({
            "source": "christos",
            "source_id": ident,
            "source_url": variants.get("main") or next(iter(variants.values())),
            "subject": "maths",
            "course": "AA",
            "level": "BOTH",                 # site notes white = SL+HL, blue = HL-only
            "paper": None,
            "year": None,
            "session": None,
            "topic_id": topic_id,
            "subtopic": section_label,
            "title": title,
            "question_html": question_html,
            "solution_html": solution_html,
            "examiners_html": None,
            "extra": {
                "sections": sections,
                "variants": variants,
            },
        })

    n = upsert_questions(conn, rows)
    print(f"  christos: {n} exercise sets")
    return n

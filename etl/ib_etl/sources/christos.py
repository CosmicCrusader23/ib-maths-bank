"""Christos Nikolaidis — IB MAA exercises, MAA tests, and MAI exercises.

The site has three live PDF index pages we can scrape today:

- /en/maa-exercise/   → ``Math-AA-1.1-NUMBERS-ROUNDING.pdf`` (topic in filename)
- /en/mai-exercise/   → ``MAI-1.1-NUMBERS-ROUNDING.pdf``      (topic in filename)
- /en/maa-tests/      → ``TEST-1.-Sequences-2014.pdf``        (topic via keywords)

We treat each PDF group (main + eco + solutions) as one row. The actual
question text lives in the PDF — extracting it would mean OCR/PDF parsing
and isn't worth it for v1, so each row carries the PDF links and the site
renders them as a download list.
"""
from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path

from bs4 import BeautifulSoup

from ..db import upsert_questions
from ..http import CACHE, fetch

# ---- exercise filenames ------------------------------------------------------
# Match either "Math-AA-..." or "MAI-...". Both share the same X.Y(-X.Y)*-TITLE.pdf
# tail; only the prefix and the variant suffix differ.
EXERCISE_RE = re.compile(
    r"(?:Math-AA|MAI)-"
    r"(?P<sections>(?:\d+\.\d+)(?:-\d+\.\d+)*)"
    r"-(?P<title>[A-Z0-9-]+?)"
    r"(?P<variant>_eco|_solutions)?"
    r"\.pdf$",
    re.IGNORECASE,
)

# ---- tests filenames ---------------------------------------------------------
# TEST-1.-Sequences-2014.pdf
# TEST-2.-Sequences-Binomial-Induction-2015.pdf
# TEST-1.-Sequences-SOLUTIONS.pdf
TEST_RE = re.compile(
    r"TEST-(?P<num>\d+)\.?-(?P<rest>[A-Za-z0-9-]+?)\.pdf$",
    re.IGNORECASE,
)

# Keyword → IB topic ID. First match wins; we walk from most-specific to most-general.
TEST_KEYWORDS: list[tuple[str, str]] = [
    ("sequences",     "1"),
    ("binomial",      "1"),
    ("induction",     "1"),
    ("complex",       "1"),
    ("exponents",     "1"),
    ("logarithms",    "1"),
    ("polynomial",    "2"),
    ("functions",     "2"),
    ("trigonometry",  "3"),
    ("vectors",       "3"),
    ("statistics",    "4"),
    ("probability",   "4"),
    ("derivatives",   "5"),
    ("integrals",     "5"),
    ("calculus",      "5"),
]


SOURCES: list[tuple[str, str, str, str]] = [
    # (source key suffix, URL, course, kind)
    ("maa-exercise", "https://www.christosnikolaidis.com/en/maa-exercise/", "AA", "exercise"),
    ("mai-exercise", "https://www.christosnikolaidis.com/en/mai-exercise/", "AI", "exercise"),
    ("maa-tests",    "https://www.christosnikolaidis.com/en/maa-tests/",    "AA", "test"),
]


def _parse_exercise(fname: str) -> dict | None:
    m = EXERCISE_RE.search(fname)
    if not m:
        return None
    sections = m.group("sections").split("-")
    title = m.group("title").replace("-", " ").title()
    variant = (m.group("variant") or "").lstrip("_") or "main"
    topic_id = sections[0].split(".", 1)[0]
    if topic_id not in {"1", "2", "3", "4", "5"}:
        return None
    return {
        "fname": fname, "sections": sections, "title": title,
        "variant": variant, "topic_id": topic_id,
    }


def _parse_test(fname: str) -> dict | None:
    m = TEST_RE.search(fname)
    if not m:
        return None
    rest = m.group("rest")
    is_solution = "SOLUTIONS" in rest.upper()
    rest_lower = rest.lower()
    topic_id = None
    for kw, tid in TEST_KEYWORDS:
        if kw in rest_lower:
            topic_id = tid
            break
    if topic_id is None:
        return None
    title_words = re.sub(r"-(\d{4}|SOLUTIONS|P1|P2)$", "", rest, flags=re.IGNORECASE)
    title_words = re.sub(r"-(\d{4}[A-Z])$", "", title_words)  # 2013A trailing
    title = title_words.replace("-", " ").strip().title()
    test_num = m.group("num")
    return {
        "fname": fname,
        "test_num": test_num,
        "title": title,
        "variant": "solutions" if is_solution else "main",
        "topic_id": topic_id,
    }


def _ingest_exercise(course: str, source_key: str, soup: BeautifulSoup) -> list[dict]:
    groups: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"variants": {}, "sections": None, "title": None, "topic_id": None}
    )
    for a in soup.find_all("a", href=True):
        href = html.unescape(a["href"])
        if "dropbox.com" not in href or ".pdf" not in href:
            continue
        fname = href.rsplit("/", 1)[-1].split("?", 1)[0]
        meta = _parse_exercise(html.unescape(fname))
        if not meta:
            continue
        key = (meta["topic_id"], "-".join(meta["sections"]) + "-" + meta["title"])
        g = groups[key]
        g["variants"][meta["variant"]] = href
        g["sections"] = meta["sections"]
        g["title"] = meta["title"]
        g["topic_id"] = meta["topic_id"]

    rows: list[dict] = []
    for (topic_id, ident), g in sorted(groups.items()):
        section_label = " / ".join(g["sections"])
        title = g["title"]
        variants = g["variants"]
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
            f'<p><strong>Christos Nikolaidis — {course} §{section_label}: '
            f'{html.escape(title)}</strong></p>'
            f'<p>PDF worksheet bundled by syllabus subtopic.</p>'
            f'<ul>{links_html}</ul>'
            f'</div>'
        )
        solution_html = None
        if "solutions" in variants:
            solution_html = (
                f'<p><a href="{html.escape(variants["solutions"])}" target="_blank" '
                f'rel="noopener">Open solutions PDF</a></p>'
            )
        rows.append({
            "source": source_key,
            "source_id": ident,
            "source_url": variants.get("main") or next(iter(variants.values())),
            "subject": "maths",
            "course": course,
            "level": "BOTH",
            "paper": None,
            "year": None,
            "session": None,
            "topic_id": topic_id,
            "subtopic": section_label,
            "title": title,
            "question_html": question_html,
            "solution_html": solution_html,
            "examiners_html": None,
            "extra": {"sections": g["sections"], "variants": variants},
        })
    return rows


def _ingest_test(course: str, source_key: str, soup: BeautifulSoup) -> list[dict]:
    groups: dict[tuple[str, str, str], dict] = defaultdict(
        lambda: {"variants": {}, "test_num": None, "title": None, "topic_id": None}
    )
    for a in soup.find_all("a", href=True):
        href = html.unescape(a["href"])
        if "dropbox.com" not in href or ".pdf" not in href:
            continue
        fname = href.rsplit("/", 1)[-1].split("?", 1)[0]
        meta = _parse_test(html.unescape(fname))
        if not meta:
            continue
        # Pair main+solutions of the same test_num + similar title.
        # Use (topic_id, test_num, title-without-year) as the group key.
        key = (meta["topic_id"], meta["test_num"], meta["title"])
        g = groups[key]
        g["variants"][meta["variant"]] = href
        g["test_num"] = meta["test_num"]
        g["title"] = meta["title"]
        g["topic_id"] = meta["topic_id"]

    rows: list[dict] = []
    for (topic_id, test_num, title), g in sorted(groups.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
        variants = g["variants"]
        links_html = "".join(
            f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener">'
            f'{html.escape(label)}</a></li>'
            for label, url in (
                ("Test paper", variants.get("main")),
                ("Solutions", variants.get("solutions")),
            )
            if url
        )
        question_html = (
            f'<div class="src-christos-test">'
            f'<p><strong>Christos Nikolaidis — {course} test {test_num}: '
            f'{html.escape(title)}</strong></p>'
            f'<p>Full timed test PDF; topic mapped from test title.</p>'
            f'<ul>{links_html}</ul>'
            f'</div>'
        )
        solution_html = None
        if "solutions" in variants:
            solution_html = (
                f'<p><a href="{html.escape(variants["solutions"])}" target="_blank" '
                f'rel="noopener">Open solutions PDF</a></p>'
            )
        rows.append({
            "source": source_key,
            "source_id": f"{test_num}:{title}",
            "source_url": variants.get("main") or next(iter(variants.values())),
            "subject": "maths",
            "course": course,
            "level": "BOTH",
            "paper": None,
            "year": None,
            "session": None,
            "topic_id": topic_id,
            "subtopic": title,
            "title": f"Test {test_num}: {title}",
            "question_html": question_html,
            "solution_html": solution_html,
            "examiners_html": None,
            "extra": {"test_num": test_num, "variants": variants},
        })
    return rows


def ingest(conn) -> int:
    total = 0
    for slug, url, course, kind in SOURCES:
        dest = CACHE / "christos" / f"{slug}.html"
        print(f"  christos: fetching {slug}…")
        raw = fetch(url, dest=dest)
        soup = BeautifulSoup(raw, "lxml")
        source_key = f"christos-{slug}"
        if kind == "exercise":
            rows = _ingest_exercise(course, source_key, soup)
        elif kind == "test":
            rows = _ingest_test(course, source_key, soup)
        else:
            continue
        n = upsert_questions(conn, rows)
        total += n
        print(f"  christos: {slug}: {n} rows ({course} {kind})")
    return total

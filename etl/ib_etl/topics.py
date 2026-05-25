"""Canonical IB Mathematics syllabus topics.

We key everything on the five MAA topics (which are the same as the five MAI
topics by number — the contents differ but the top-level groupings do not).
"""
from __future__ import annotations

TOPICS = {
    "1": "Number and algebra",
    "2": "Functions",
    "3": "Geometry and trigonometry",
    "4": "Statistics and probability",
    "5": "Calculus",
}

# pestle's topic slugs map directly onto our numeric IDs
PESTLE_TOPIC_TO_ID = {
    "topic-1-number-and-algebra": "1",
    "topic-2-functions": "2",
    "topic-3-geometry-and-trigonometry": "3",
    "topic-4-statistics-and-probability": "4",
    "topic-5-calculus": "5",
}


def topic_name(topic_id: str) -> str:
    return TOPICS[topic_id]


def all_topic_ids() -> list[str]:
    return list(TOPICS.keys())

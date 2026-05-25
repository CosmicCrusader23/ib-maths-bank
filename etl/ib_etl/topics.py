"""Per-subject taxonomy of IB syllabus topics.

Each subject has its own ordered list of topic IDs and human-readable names.
Topic IDs are strings — Physics options are 'a' through 'd', so we don't use
ints. The mapping from a source's topic slug → our (subject, topic_id) lives
alongside the taxonomy so a single ``classify(slug)`` call can route the
question to the right subject + topic.
"""
from __future__ import annotations

# subject_key -> ordered dict of topic_id -> name
SUBJECTS: dict[str, dict[str, str]] = {
    "maths": {
        "1": "Number and algebra",
        "2": "Functions",
        "3": "Geometry and trigonometry",
        "4": "Statistics and probability",
        "5": "Calculus",
    },
    "physics": {
        "1":  "Measurements and uncertainties",
        "2":  "Mechanics",
        "3":  "Thermal physics",
        "4":  "Waves",
        "5":  "Electricity and magnetism",
        "6":  "Circular motion and gravitation",
        "7":  "Atomic, nuclear and particle physics",
        "8":  "Energy production",
        "9":  "Wave phenomena (HL)",
        "10": "Fields (HL)",
        "11": "Electromagnetic induction (HL)",
        "12": "Quantum and nuclear physics (HL)",
        "a":  "Option A — Relativity",
        "b":  "Option B — Engineering physics",
        "c":  "Option C — Imaging",
        "d":  "Option D — Astrophysics",
    },
}

SUBJECT_LABELS = {
    "maths":   "Mathematics",
    "physics": "Physics",
}


# pestle topic slugs → (subject, topic_id)
PESTLE_TOPIC_MAP: dict[str, tuple[str, str]] = {
    "topic-1-number-and-algebra":          ("maths", "1"),
    "topic-2-functions":                    ("maths", "2"),
    "topic-3-geometry-and-trigonometry":    ("maths", "3"),
    "topic-4-statistics-and-probability":   ("maths", "4"),
    "topic-5-calculus":                     ("maths", "5"),
    "topic-1-measurements-and-uncertainties":     ("physics", "1"),
    "topic-2-mechanics":                          ("physics", "2"),
    "topic-3-thermal-physics":                    ("physics", "3"),
    "topic-4-waves":                              ("physics", "4"),
    "topic-5-electricity-and-magnetism":          ("physics", "5"),
    "topic-6-circular-motion-and-gravitation":    ("physics", "6"),
    "topic-7-atomic-nuclear-and-particle-physics":("physics", "7"),
    "topic-8-energy-production":                  ("physics", "8"),
    "topic-9-wave-phenomena":                     ("physics", "9"),
    "topic-10-fields":                            ("physics", "10"),
    "topic-11-electromagnetic-induction":         ("physics", "11"),
    "topic-12-quantum-and-nuclear-physics":       ("physics", "12"),
    "option-a-relativity":                        ("physics", "a"),
    "option-b-engineering-physics":               ("physics", "b"),
    "option-c-imaging":                           ("physics", "c"),
    "option-d-astrophysics":                      ("physics", "d"),
}


def topic_name(subject: str, topic_id: str) -> str:
    return SUBJECTS[subject][topic_id]


def subject_topics(subject: str) -> list[tuple[str, str]]:
    return list(SUBJECTS[subject].items())

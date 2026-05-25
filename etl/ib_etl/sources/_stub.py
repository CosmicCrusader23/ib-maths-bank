"""Stubs for sources that need auth or aren't yet implemented.

Each stub raises NotImplementedError with a hint about what's missing so the
CLI surfaces it cleanly. Drop a real loader in here when you have credentials
or a bypass.
"""
from __future__ import annotations


def ingest(conn):  # pragma: no cover
    raise NotImplementedError(
        "Source not yet implemented. See README → Sources for status."
    )

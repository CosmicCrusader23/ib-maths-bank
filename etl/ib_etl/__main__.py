"""CLI: ingest <source>+ | export | stats."""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from . import db

KNOWN_SOURCES = {
    "pestle":   "ib_etl.sources.pestle",
    "christos": "ib_etl.sources.christos",
    # placeholders — drop in modules as they get implemented
    "smearchive": "ib_etl.sources._stub",
    "thinkib":    "ib_etl.sources._stub",
    "studyib":    "ib_etl.sources._stub",
    "madas":      "ib_etl.sources._stub",
    "ibqb":       "ib_etl.sources._stub",
}


def cmd_ingest(args):
    conn = db.connect()
    targets = args.sources or ["pestle", "christos"]
    if "all" in targets:
        targets = list(KNOWN_SOURCES)
    total = 0
    for name in targets:
        modname = KNOWN_SOURCES.get(name)
        if not modname:
            print(f"unknown source: {name}", file=sys.stderr)
            continue
        print(f"== {name} ==")
        try:
            mod = importlib.import_module(modname)
            total += mod.ingest(conn)
        except NotImplementedError as e:
            print(f"  skipped: {e}")
        except Exception as e:
            print(f"  FAILED: {e!r}", file=sys.stderr)
    print(f"\ntotal upserts: {total}")
    print(json.dumps(db.stats(conn), indent=2))


def cmd_stats(_args):
    conn = db.connect()
    print(json.dumps(db.stats(conn), indent=2))


def cmd_export(args):
    from .export import run as export_run
    out = export_run(Path(args.out))
    print(f"wrote {out}")


def main():
    p = argparse.ArgumentParser(prog="ib_etl")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("ingest", help="run one or more source loaders")
    pi.add_argument("sources", nargs="*", help=f"any of: {', '.join(KNOWN_SOURCES)}, all")
    pi.set_defaults(func=cmd_ingest)

    ps = sub.add_parser("stats", help="show DB stats")
    ps.set_defaults(func=cmd_stats)

    pe = sub.add_parser("export", help="dump per-topic JSON for the site")
    pe.add_argument("--out", default=str(Path(__file__).resolve().parents[2] / "site" / "public" / "data"))
    pe.set_defaults(func=cmd_export)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

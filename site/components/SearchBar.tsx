"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

interface Row {
  id: number;
  s: string;            // subject
  t: string;            // topic
  title: string | null;
  sub: string | null;
  src: string;
  c: string | null;     // course
  l: string | null;     // level
  p: string | null;     // paper
  sess: string | null;  // session
}

const SUBJECT_LABELS: Record<string, string> = {
  maths: "Mathematics",
  physics: "Physics",
};

function searchIndexUrl(): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
  return `${base}/data/search.json`;
}

export function SearchBar() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [rows, setRows] = useState<Row[] | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Lazy-load the index the first time the user opens search
  useEffect(() => {
    if (!open || rows !== null) return;
    fetch(searchIndexUrl())
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: Row[]) => setRows(data))
      .catch((e) => setLoadErr(String(e)));
  }, [open, rows]);

  // Cmd/Ctrl-K to open
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(true);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (open) {
      requestAnimationFrame(() => inputRef.current?.focus());
    } else {
      setQuery("");
    }
  }, [open]);

  const results = useMemo(() => {
    if (!rows) return [];
    const q = query.trim().toLowerCase();
    if (!q) return [];
    const tokens = q.split(/\s+/).filter(Boolean);
    const out: Row[] = [];
    for (const r of rows) {
      const hay = (
        (r.title || "") + " " +
        (r.sub || "") + " " +
        (r.src || "") + " " +
        (r.c || "") + " " +
        (r.l || "") + " " +
        (r.sess || "") + " " +
        (SUBJECT_LABELS[r.s] || r.s)
      ).toLowerCase();
      let ok = true;
      for (const t of tokens) {
        if (!hay.includes(t)) { ok = false; break; }
      }
      if (ok) {
        out.push(r);
        if (out.length >= 200) break;
      }
    }
    return out;
  }, [rows, query]);

  return (
    <>
      <button
        type="button"
        className="search-trigger"
        onClick={() => setOpen(true)}
        aria-label="Search questions"
      >
        <span className="search-trigger-icon">⌕</span>
        <span className="search-trigger-text">Search</span>
        <kbd className="search-trigger-kbd">⌘K</kbd>
      </button>

      {open && (
        <div
          className="search-backdrop"
          onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
        >
          <div className="search-modal" role="dialog" aria-modal="true">
            <div className="search-modal-header">
              <input
                ref={inputRef}
                className="search-modal-input"
                type="search"
                placeholder="Search 3,228 questions by title, subtopic, session…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button
                type="button"
                className="search-modal-close"
                onClick={() => setOpen(false)}
                aria-label="Close search"
              >
                ✕
              </button>
            </div>
            <div className="search-modal-results">
              {loadErr && (
                <p className="empty">Failed to load search index: {loadErr}</p>
              )}
              {!loadErr && rows === null && (
                <p className="empty">Loading search index…</p>
              )}
              {rows !== null && !query && (
                <p className="empty">
                  Type to search across all 3,228 questions.
                </p>
              )}
              {rows !== null && query && results.length === 0 && (
                <p className="empty">No matches for “{query}”.</p>
              )}
              {results.length > 0 && (
                <ul className="q-list" style={{ margin: 0 }}>
                  {results.map((r) => (
                    <li key={r.id}>
                      <Link
                        href={`/q/${r.id}/`}
                        className="q-row"
                        onClick={() => setOpen(false)}
                      >
                        <span className="title">
                          {r.title || `#${r.id}`}
                          {r.sub && (
                            <span style={{ color: "var(--muted)", fontWeight: 400 }}>
                              {" — "}
                              {r.sub.length > 70 ? r.sub.slice(0, 70) + "…" : r.sub}
                            </span>
                          )}
                        </span>
                        <span className="meta">
                          {SUBJECT_LABELS[r.s] || r.s} · T{r.t}
                          {r.c ? ` · ${r.c}` : ""}
                          {r.l ? ` ${r.l}` : ""}
                        </span>
                        <span className="tag">{r.src}</span>
                      </Link>
                    </li>
                  ))}
                  {results.length === 200 && (
                    <li>
                      <p style={{ color: "var(--muted)", fontSize: 13, textAlign: "center", margin: "8px 0" }}>
                        Showing first 200 matches. Refine your query for more.
                      </p>
                    </li>
                  )}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

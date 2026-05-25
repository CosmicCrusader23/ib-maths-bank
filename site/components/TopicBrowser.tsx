"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { QuestionSummary } from "@/lib/data";

const ALL = "_all";

function uniqueSorted(values: (string | null | undefined)[]): string[] {
  const set = new Set<string>();
  for (const v of values) if (v) set.add(v);
  return Array.from(set).sort();
}

export function TopicBrowser({ questions }: { questions: QuestionSummary[] }) {
  const [course, setCourse] = useState<string>(ALL);
  const [level, setLevel] = useState<string>(ALL);
  const [source, setSource] = useState<string>(ALL);
  const [paper, setPaper] = useState<string>(ALL);
  const [query, setQuery] = useState("");

  const courses = useMemo(() => uniqueSorted(questions.map((q) => q.course)), [questions]);
  const levels = useMemo(() => uniqueSorted(questions.map((q) => q.level)), [questions]);
  const sources = useMemo(() => uniqueSorted(questions.map((q) => q.source)), [questions]);
  const papers = useMemo(() => uniqueSorted(questions.map((q) => q.paper)), [questions]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return questions.filter((row) => {
      if (course !== ALL && row.course !== course) return false;
      if (level !== ALL && row.level !== level) return false;
      if (source !== ALL && row.source !== source) return false;
      if (paper !== ALL && row.paper !== paper) return false;
      if (q) {
        const hay = (
          (row.title || "") +
          " " +
          (row.subtopic || "") +
          " " +
          (row.session || "")
        ).toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [questions, course, level, source, paper, query]);

  return (
    <>
      <div className="filter-bar">
        <label>
          Course
          <select value={course} onChange={(e) => setCourse(e.target.value)}>
            <option value={ALL}>All</option>
            {courses.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label>
          Level
          <select value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value={ALL}>All</option>
            {levels.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label>
          Source
          <select value={source} onChange={(e) => setSource(e.target.value)}>
            <option value={ALL}>All</option>
            {sources.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label>
          Paper
          <select value={paper} onChange={(e) => setPaper(e.target.value)}>
            <option value={ALL}>Any</option>
            {papers.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label style={{ flex: 1, minWidth: 200 }}>
          Search
          <input
            type="search"
            placeholder="subtopic, session, id…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ flex: 1 }}
          />
        </label>
        <span style={{ marginLeft: "auto", color: "var(--muted)", fontSize: 13 }}>
          {filtered.length.toLocaleString()} / {questions.length.toLocaleString()}
        </span>
      </div>

      {filtered.length === 0 ? (
        <p className="empty">No questions match those filters.</p>
      ) : (
        <ul className="q-list">
          {filtered.slice(0, 500).map((q) => (
            <li key={q.id}>
              <Link href={`/q/${q.id}/`} className="q-row">
                <span className="title">
                  {q.title || `#${q.id}`}
                  {q.subtopic && (
                    <span style={{ color: "var(--muted)", fontWeight: 400 }}>
                      {" "}— {q.subtopic.length > 80 ? q.subtopic.slice(0, 80) + "…" : q.subtopic}
                    </span>
                  )}
                </span>
                <span className="meta">
                  {q.course}
                  {q.level ? ` ${q.level}` : ""}
                  {q.paper ? ` · P${q.paper}` : ""}
                </span>
                <span className="tag">{q.source}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
      {filtered.length > 500 && (
        <p style={{ color: "var(--muted)", fontSize: 13, textAlign: "center" }}>
          Showing first 500 of {filtered.length.toLocaleString()}. Refine filters to see more.
        </p>
      )}
    </>
  );
}

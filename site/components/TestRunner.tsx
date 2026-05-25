"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

interface Summary {
  id: number;
  source: string;
  subject: string;
  course: string | null;
  level: string | null;
  paper: string | null;
  session: string | null;
  topic_id: string;
  title: string | null;
  subtopic: string | null;
}

interface Full extends Summary {
  source_url: string | null;
  question_html: string;
  solution_html: string | null;
}

interface Config {
  subject: string;
  topic?: string;
  n: number;
  course?: string;
  level?: string;
  paper?: string;
  seed?: string;
}

const SUBJECT_LABELS: Record<string, string> = {
  maths: "Mathematics",
  physics: "Physics",
};

function basePath(): string {
  return process.env.NEXT_PUBLIC_BASE_PATH || "";
}

function parseHash(): Config | null {
  if (typeof window === "undefined") return null;
  const h = window.location.hash.replace(/^#/, "");
  if (!h) return null;
  const params = new URLSearchParams(h);
  const subject = params.get("subject");
  if (!subject) return null;
  return {
    subject,
    topic: params.get("topic") || undefined,
    n: parseInt(params.get("n") || "10", 10),
    course: params.get("course") || undefined,
    level: params.get("level") || undefined,
    paper: params.get("paper") || undefined,
    seed: params.get("seed") || undefined,
  };
}

// Mulberry32 — small deterministic PRNG so a test is reproducible from its seed.
function mulberry32(seed: number) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hash(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function shuffle<T>(arr: T[], rand: () => number): T[] {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

async function loadSummaries(cfg: Config): Promise<Summary[]> {
  const base = basePath();
  if (cfg.topic) {
    const r = await fetch(`${base}/data/${cfg.subject}/topic-${cfg.topic}.json`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }
  // cross-topic: load every topic file for this subject and concatenate
  const idxR = await fetch(`${base}/data/${cfg.subject}/index.json`);
  if (!idxR.ok) throw new Error(`HTTP ${idxR.status}`);
  const idx = await idxR.json();
  const all: Summary[] = [];
  for (const t of idx.topics) {
    if (!t.count) continue;
    const r = await fetch(`${base}/data/${cfg.subject}/topic-${t.id}.json`);
    if (r.ok) {
      const rows: Summary[] = await r.json();
      all.push(...rows);
    }
  }
  return all;
}

function applyFilters(rows: Summary[], cfg: Config): Summary[] {
  return rows.filter((r) => {
    // Only pestle questions have full HTML — Christos rows are PDF links, not testable
    if (r.source !== "pestle") return false;
    if (cfg.course && r.course !== cfg.course) return false;
    if (cfg.level && r.level !== cfg.level) return false;
    if (cfg.paper && r.paper !== cfg.paper) return false;
    return true;
  });
}

async function fetchFull(ids: number[]): Promise<Full[]> {
  const base = basePath();
  const results = await Promise.all(
    ids.map(async (id) => {
      const r = await fetch(`${base}/data/questions/${id}.json`);
      if (!r.ok) throw new Error(`HTTP ${r.status} for q ${id}`);
      return r.json() as Promise<Full>;
    }),
  );
  return results;
}

export function TestRunner() {
  const [config, setConfig] = useState<Config | null>(null);
  const [questions, setQuestions] = useState<Full[]>([]);
  const [pool, setPool] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revealAll, setRevealAll] = useState(false);
  const [hashChange, setHashChange] = useState(0);

  useEffect(() => {
    const onHash = () => setHashChange((n) => n + 1);
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    const cfg = parseHash();
    setConfig(cfg);
    setRevealAll(false);
    setQuestions([]);
    setError(null);

    if (!cfg) {
      setLoading(false);
      return;
    }

    setLoading(true);
    (async () => {
      try {
        const summaries = await loadSummaries(cfg);
        const filtered = applyFilters(summaries, cfg);
        setPool(filtered.length);
        if (filtered.length === 0) {
          setError("No questions match those filters.");
          return;
        }
        const seedStr = cfg.seed || String(Date.now());
        const rand = mulberry32(hash(seedStr));
        const picked = shuffle(filtered, rand).slice(0, Math.min(cfg.n, filtered.length));
        const full = await fetchFull(picked.map((p) => p.id));
        setQuestions(full);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, [hashChange]);

  // Re-run MathJax when questions render
  useEffect(() => {
    if (typeof window === "undefined") return;
    const mj = (window as Window & {
      MathJax?: { typesetPromise?: (els?: HTMLElement[]) => Promise<void> };
    }).MathJax;
    if (mj?.typesetPromise) mj.typesetPromise().catch(() => undefined);
  }, [questions, revealAll]);

  const subjectLabel = config ? SUBJECT_LABELS[config.subject] || config.subject : "";
  const filterLine = useMemo(() => {
    if (!config) return "";
    const parts: string[] = [];
    if (config.topic) parts.push(`Topic ${config.topic}`);
    if (config.course) parts.push(config.course);
    if (config.level) parts.push(config.level);
    if (config.paper) parts.push(`Paper ${config.paper}`);
    return parts.join(" · ");
  }, [config]);

  if (!config) {
    return (
      <div className="empty">
        <p>No test configured.</p>
        <p>
          <Link href="/">← back home</Link>
        </p>
      </div>
    );
  }

  if (loading) {
    return <p className="empty">Building test…</p>;
  }

  if (error) {
    return (
      <div className="empty">
        <p>{error}</p>
        <p>
          <Link href={config.topic ? `/subject/${config.subject}/topic/${config.topic}/` : `/subject/${config.subject}/`}>
            ← back
          </Link>
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="test-header">
        <div>
          <p style={{ margin: 0 }}>
            <Link
              href={
                config.topic
                  ? `/subject/${config.subject}/topic/${config.topic}/`
                  : `/subject/${config.subject}/`
              }
            >
              ← back
            </Link>
          </p>
          <h1 style={{ margin: "4px 0 0" }}>
            {subjectLabel} test
          </h1>
          <p className="summary-bar" style={{ margin: "4px 0 0" }}>
            <span>
              {questions.length} of {pool.toLocaleString()} matching questions
            </span>
            {filterLine && <span>{filterLine}</span>}
          </p>
        </div>
        <div className="test-actions">
          <button
            type="button"
            className="btn"
            onClick={() => setRevealAll((v) => !v)}
          >
            {revealAll ? "Hide all solutions" : "Reveal all solutions"}
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => {
              setRevealAll(false);
              setHashChange((n) => n + 1);
            }}
          >
            Regenerate
          </button>
        </div>
      </div>

      <ol className="test-list">
        {questions.map((q, i) => (
          <li key={q.id} className="test-item">
            <div className="test-item-header">
              <h2>Question {i + 1}</h2>
              <span className="meta">
                {q.title}
                {q.course ? ` · ${q.course}` : ""}
                {q.level ? ` ${q.level}` : ""}
                {q.paper ? ` · P${q.paper}` : ""}
                {q.session ? ` · ${q.session}` : ""}
              </span>
            </div>
            <div
              className="q-content"
              dangerouslySetInnerHTML={{ __html: q.question_html }}
            />
            {q.solution_html && (
              <details className="solution" open={revealAll}>
                <summary>Show markscheme</summary>
                <div dangerouslySetInnerHTML={{ __html: q.solution_html }} />
              </details>
            )}
            <p style={{ fontSize: 12, color: "var(--muted)", margin: "8px 0 0" }}>
              <Link href={`/q/${q.id}/`}>Open standalone →</Link>
            </p>
          </li>
        ))}
      </ol>
    </>
  );
}

"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

interface Props {
  subject: string;
  topic?: string;       // omit for cross-topic tests
  // pool stats so we can suggest sensible Ns and disable impossible options
  hasMaths?: boolean;   // shows Course filter (AA/AI) when true
}

const SIZES = [5, 10, 15, 20, 30];

export function TestSetup({ subject, topic, hasMaths }: Props) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [n, setN] = useState(10);
  const [course, setCourse] = useState("");
  const [level, setLevel] = useState("");
  const [paper, setPaper] = useState("");
  const inputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  function start() {
    const params = new URLSearchParams({ subject, n: String(n) });
    if (topic) params.set("topic", topic);
    if (course) params.set("course", course);
    if (level) params.set("level", level);
    if (paper) params.set("paper", paper);
    router.push(`/test/#${params.toString()}`);
    setOpen(false);
  }

  return (
    <>
      <button
        type="button"
        className="btn btn-primary"
        onClick={() => setOpen(true)}
      >
        Generate test
      </button>

      {open && (
        <div
          className="search-backdrop"
          onClick={(e) => {
            if (e.target === e.currentTarget) setOpen(false);
          }}
        >
          <div
            className="search-modal"
            ref={inputRef}
            role="dialog"
            aria-modal="true"
            style={{ maxWidth: 480 }}
          >
            <div className="search-modal-header">
              <h2 style={{ margin: 0, fontSize: 18 }}>
                {topic ? "Test from this topic" : "Test across all topics"}
              </h2>
              <button
                type="button"
                className="search-modal-close"
                onClick={() => setOpen(false)}
                aria-label="Close"
              >
                ✕
              </button>
            </div>
            <div className="test-setup-body">
              <div className="test-setup-row">
                <label>Number of questions</label>
                <div className="size-buttons">
                  {SIZES.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className={`size-btn${s === n ? " active" : ""}`}
                      onClick={() => setN(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              {hasMaths && (
                <div className="test-setup-row">
                  <label htmlFor="course">Course</label>
                  <select
                    id="course"
                    value={course}
                    onChange={(e) => setCourse(e.target.value)}
                  >
                    <option value="">Any (AA + AI)</option>
                    <option value="AA">AA only</option>
                    <option value="AI">AI only</option>
                  </select>
                </div>
              )}

              <div className="test-setup-row">
                <label htmlFor="level">Level</label>
                <select
                  id="level"
                  value={level}
                  onChange={(e) => setLevel(e.target.value)}
                >
                  <option value="">Any</option>
                  <option value="SL">SL only</option>
                  <option value="HL">HL only</option>
                </select>
              </div>

              <div className="test-setup-row">
                <label htmlFor="paper">Paper</label>
                <select
                  id="paper"
                  value={paper}
                  onChange={(e) => setPaper(e.target.value)}
                >
                  <option value="">Any</option>
                  <option value="1">Paper 1</option>
                  <option value="2">Paper 2</option>
                  <option value="3">Paper 3</option>
                </select>
              </div>

              <p style={{ color: "var(--muted)", fontSize: 13, margin: 0 }}>
                Test pulls real exam questions from the pestle bank, randomly
                selected. Reload to get a different set.
              </p>

              <button type="button" className="btn btn-primary btn-block" onClick={start}>
                Start test
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

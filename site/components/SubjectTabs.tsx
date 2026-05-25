"use client";

import Link from "next/link";
import { useState } from "react";
import type { SubjectIndex } from "@/lib/data";
import { TestSetup } from "@/components/TestSetup";

interface Props {
  subjects: { key: string; data: SubjectIndex }[];
  defaultKey: string;
}

export function SubjectTabs({ subjects, defaultKey }: Props) {
  const [active, setActive] = useState(defaultKey);
  const current = subjects.find((s) => s.key === active) ?? subjects[0];
  const data = current.data;
  const sourceLine = Object.entries(data.sources)
    .map(([k, v]) => `${k} (${v.toLocaleString()})`)
    .join(" • ");

  return (
    <>
      <div className="subject-tabs">
        {subjects.map((s) => (
          <button
            key={s.key}
            type="button"
            className={`subject-tab${s.key === active ? " active" : ""}`}
            onClick={() => setActive(s.key)}
          >
            <span className="subject-tab-label">{s.data.label}</span>
            <span className="subject-tab-count">
              {s.data.total.toLocaleString()} questions
            </span>
          </button>
        ))}
      </div>

      <div className="page-header" style={{ margin: "16px 0 8px" }}>
        <div className="summary-bar" style={{ margin: 0 }}>
          <span>{data.total.toLocaleString()} questions in {data.label}</span>
          {sourceLine && <span>{sourceLine}</span>}
        </div>
        <TestSetup subject={current.key} hasMaths={current.key === "maths"} />
      </div>

      <div className="topic-grid">
        {data.topics.filter((t) => t.count > 0).map((t) => (
          <Link
            key={t.id}
            href={`/subject/${data.subject}/topic/${t.id}/`}
            className="topic-card"
          >
            <div className="num">{t.id}</div>
            <h3>{t.name}</h3>
            <div className="count">{t.count.toLocaleString()} questions</div>
          </Link>
        ))}
      </div>
    </>
  );
}

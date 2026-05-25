import Link from "next/link";
import { loadRoot } from "@/lib/data";

export default async function Home() {
  const idx = await loadRoot();
  const sourceLine = Object.entries(idx.sources)
    .map(([k, v]) => `${k} (${v.toLocaleString()})`)
    .join(" • ");

  return (
    <>
      <h1>IB Revision Bank</h1>
      <p>
        Browse {idx.total.toLocaleString()} IB questions across maths and
        physics, grouped by syllabus topic, pulled from public revision
        sources.
      </p>
      <div className="summary-bar">
        <span>{idx.total.toLocaleString()} questions</span>
        <span>{sourceLine}</span>
      </div>

      <div className="topic-grid">
        {idx.subjects.map((s) => (
          <Link key={s.key} href={`/subject/${s.key}/`} className="topic-card">
            <div className="num">{s.label.split(" ").pop()}</div>
            <h3>{s.label}</h3>
            <div className="count">
              {s.total.toLocaleString()} questions across {s.topic_count} topics
            </div>
          </Link>
        ))}
      </div>
    </>
  );
}

import Link from "next/link";
import { loadIndex } from "@/lib/data";

export default async function Home() {
  const idx = await loadIndex();
  const sourceLine = Object.entries(idx.sources)
    .map(([k, v]) => `${k} (${v})`)
    .join(" • ");

  return (
    <>
      <h1>IB Maths Bank</h1>
      <p>
        Browse {idx.total.toLocaleString()} IB mathematics questions, grouped by
        syllabus topic, pulled from public revision sources. Both Math AA and
        Math AI, HL and SL.
      </p>
      <div className="summary-bar">
        <span>{idx.total.toLocaleString()} questions</span>
        <span>{sourceLine}</span>
      </div>

      <div className="topic-grid">
        {idx.topics.map((t) => (
          <Link key={t.id} href={`/topic/${t.id}/`} className="topic-card">
            <div className="num">{t.id}</div>
            <h3>{t.name}</h3>
            <div className="count">{t.count.toLocaleString()} questions</div>
          </Link>
        ))}
      </div>
    </>
  );
}

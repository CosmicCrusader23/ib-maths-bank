import Link from "next/link";
import { notFound } from "next/navigation";
import { listSubjectKeys, loadSubject } from "@/lib/data";
import { TestSetup } from "@/components/TestSetup";

export async function generateStaticParams() {
  const keys = await listSubjectKeys();
  return keys.map((key) => ({ key }));
}

export default async function SubjectPage({
  params,
}: {
  params: Promise<{ key: string }>;
}) {
  const { key } = await params;
  let subj;
  try {
    subj = await loadSubject(key);
  } catch {
    notFound();
  }

  const sourceLine = Object.entries(subj.sources)
    .map(([k, v]) => `${k} (${v.toLocaleString()})`)
    .join(" • ");

  return (
    <>
      <p style={{ margin: 0 }}>
        <Link href="/">← all subjects</Link>
      </p>
      <div className="page-header">
        <h1>{subj.label}</h1>
        <TestSetup subject={key} hasMaths={key === "maths"} />
      </div>
      <div className="summary-bar">
        <span>{subj.total.toLocaleString()} questions</span>
        {sourceLine && <span>{sourceLine}</span>}
      </div>

      <div className="topic-grid">
        {subj.topics.filter((t) => t.count > 0).map((t) => (
          <Link
            key={t.id}
            href={`/subject/${subj.subject}/topic/${t.id}/`}
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

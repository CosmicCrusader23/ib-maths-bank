import Link from "next/link";
import { notFound } from "next/navigation";
import { listSubjectKeys, loadSubject, loadSubjectTopic } from "@/lib/data";
import { TopicBrowser } from "@/components/TopicBrowser";
import { TestSetup } from "@/components/TestSetup";

export async function generateStaticParams() {
  const keys = await listSubjectKeys();
  const params: { key: string; tid: string }[] = [];
  for (const key of keys) {
    const subj = await loadSubject(key);
    for (const t of subj.topics) {
      if (t.count > 0) params.push({ key, tid: t.id });
    }
  }
  return params;
}

export default async function TopicPage({
  params,
}: {
  params: Promise<{ key: string; tid: string }>;
}) {
  const { key, tid } = await params;
  let subj;
  try {
    subj = await loadSubject(key);
  } catch {
    notFound();
  }
  const topic = subj.topics.find((t) => t.id === tid);
  if (!topic) notFound();

  const questions = await loadSubjectTopic(key, tid);

  return (
    <>
      <p style={{ margin: 0 }}>
        <Link href={`/subject/${key}/`}>← {subj.label}</Link>
      </p>
      <div className="page-header">
        <h1>
          {topic.id}. {topic.name}
        </h1>
        <TestSetup subject={key} topic={tid} hasMaths={key === "maths"} />
      </div>
      <p className="summary-bar">
        <span>{questions.length.toLocaleString()} questions</span>
      </p>
      <TopicBrowser questions={questions} />
    </>
  );
}

import { notFound } from "next/navigation";
import Link from "next/link";
import { loadIndex, loadTopic } from "@/lib/data";
import { TopicBrowser } from "@/components/TopicBrowser";

export async function generateStaticParams() {
  const idx = await loadIndex();
  return idx.topics.map((t) => ({ id: t.id }));
}

export default async function TopicPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const idx = await loadIndex();
  const topic = idx.topics.find((t) => t.id === id);
  if (!topic) notFound();

  const questions = await loadTopic(id);

  return (
    <>
      <p style={{ margin: 0 }}>
        <Link href="/">← all topics</Link>
      </p>
      <h1>
        Topic {topic.id}: {topic.name}
      </h1>
      <p className="summary-bar">
        <span>{questions.length.toLocaleString()} questions</span>
      </p>
      <TopicBrowser questions={questions} />
    </>
  );
}

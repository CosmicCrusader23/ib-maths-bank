import Link from "next/link";
import { notFound } from "next/navigation";
import { listAllQuestionIds, loadQuestion } from "@/lib/data";

export async function generateStaticParams() {
  const ids = await listAllQuestionIds();
  return ids.map((id) => ({ id }));
}

export default async function QuestionPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let q;
  try {
    q = await loadQuestion(id);
  } catch {
    notFound();
  }

  return (
    <article className="q-page">
      <p style={{ margin: 0 }}>
        <Link href={`/topic/${q.topic_id}/`}>← back to topic {q.topic_id}</Link>
      </p>
      <h1>{q.title || `Question ${q.id}`}</h1>
      <div className="q-meta">
        <span className="tag">{q.source}</span>
        <span>{q.course}</span>
        {q.level && <span>{q.level}</span>}
        {q.paper && <span>Paper {q.paper}</span>}
        {q.session && <span>{q.session}</span>}
        {q.subtopic && <span>· {q.subtopic}</span>}
        {q.source_url && (
          <a href={q.source_url} target="_blank" rel="noopener">
            source ↗
          </a>
        )}
      </div>

      <div className="q-content" dangerouslySetInnerHTML={{ __html: q.question_html }} />

      {q.solution_html && (
        <details className="solution">
          <summary>Markscheme / solution</summary>
          <div dangerouslySetInnerHTML={{ __html: q.solution_html }} />
        </details>
      )}

      {q.examiners_html && (
        <details className="solution">
          <summary>Examiners’ report</summary>
          <div dangerouslySetInnerHTML={{ __html: q.examiners_html }} />
        </details>
      )}
    </article>
  );
}

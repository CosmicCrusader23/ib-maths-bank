import { loadRoot, loadSubject } from "@/lib/data";
import { SubjectTabs } from "@/components/SubjectTabs";

export default async function Home() {
  const idx = await loadRoot();
  const subjects = await Promise.all(
    idx.subjects.map(async (s) => ({ key: s.key, data: await loadSubject(s.key) })),
  );
  const defaultKey = idx.subjects[0]?.key ?? "maths";

  return (
    <>
      <h1 className="page-title">IB Revision Bank</h1>
      <p className="page-lede">
        Browse {idx.total.toLocaleString()} IB questions across maths and
        physics, grouped by syllabus topic, pulled from public revision sources.
        Pick a subject below.
      </p>
      <SubjectTabs subjects={subjects} defaultKey={defaultKey} />
    </>
  );
}

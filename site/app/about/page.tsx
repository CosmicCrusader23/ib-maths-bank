import Link from "next/link";

export default function About() {
  return (
    <article>
      <h1>About</h1>
      <p>
        This site curates publicly available IB mathematics revision materials
        — past paper questions, topic-organised exercises and worksheets — and
        groups them by IB syllabus topic so you can grind one topic at a time.
      </p>
      <h2>Sources used so far</h2>
      <ul>
        <li>
          <a href="https://pestle.pages.dev/" target="_blank" rel="noopener">
            Mortar & Pestle (pirateIB)
          </a>{" "}
          — IB QuestionBank questions for Math AA and AI, tagged by topic and
          subtopic.
        </li>
        <li>
          <a
            href="https://www.christosnikolaidis.com/en/maa-exercise/"
            target="_blank"
            rel="noopener"
          >
            Christos Nikolaidis MAA exercises
          </a>{" "}
          — PDF worksheets organised by AA syllabus subtopic.
        </li>
      </ul>
      <h2>Planned</h2>
      <ul>
        <li>Save My Exams archive</li>
        <li>ThinkIB / StudyIB</li>
        <li>Madas Maths topic booklets</li>
        <li>Original IB QuestionBank PDFs (ibdocs.re)</li>
      </ul>
      <p>
        Sources that need a login or token (Revision Village, ibtaskmaker,
        Alcumus) are stubbed in the loader and will be wired in when
        credentials are available.
      </p>
      <p>
        <Link href="/">← back to topics</Link>
      </p>
    </article>
  );
}

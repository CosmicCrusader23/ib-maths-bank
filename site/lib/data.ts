import { promises as fs } from "fs";
import path from "path";

const DATA_DIR = path.join(process.cwd(), "public", "data");

export interface Subject {
  key: string;
  label: string;
  total: number;
  topic_count: number;
}

export interface RootIndex {
  subjects: Subject[];
  sources: Record<string, number>;
  total: number;
}

export interface SubjectIndex {
  subject: string;
  label: string;
  topics: { id: string; name: string; count: number }[];
  sources: Record<string, number>;
  total: number;
}

export interface QuestionSummary {
  id: number;
  source: string;
  subject: string;
  course: "AA" | "AI" | null;
  level: string | null;
  paper: string | null;
  year: string | null;
  session: string | null;
  subtopic: string | null;
  title: string | null;
  topic_id: string;
}

export interface QuestionFull extends QuestionSummary {
  source_url: string | null;
  question_html: string;
  solution_html: string | null;
  examiners_html: string | null;
}

async function readJson<T>(rel: string): Promise<T> {
  const buf = await fs.readFile(path.join(DATA_DIR, rel), "utf-8");
  return JSON.parse(buf) as T;
}

export const loadRoot = (): Promise<RootIndex> => readJson("index.json");

export const loadSubject = (key: string): Promise<SubjectIndex> =>
  readJson(`${key}/index.json`);

export const loadSubjectTopic = (key: string, tid: string): Promise<QuestionSummary[]> =>
  readJson(`${key}/topic-${tid}.json`);

export const loadQuestion = (id: number | string): Promise<QuestionFull> =>
  readJson(`questions/${id}.json`);

export async function listAllQuestionIds(): Promise<string[]> {
  const dir = path.join(DATA_DIR, "questions");
  const names = await fs.readdir(dir);
  return names.filter((n) => n.endsWith(".json")).map((n) => n.slice(0, -5));
}

export async function listSubjectKeys(): Promise<string[]> {
  const root = await loadRoot();
  return root.subjects.map((s) => s.key);
}

import { promises as fs } from "fs";
import path from "path";

const DATA_DIR = path.join(process.cwd(), "public", "data");

export interface IndexFile {
  topics: { id: string; name: string; count: number }[];
  sources: Record<string, number>;
  total: number;
}

export interface QuestionSummary {
  id: number;
  source: string;
  course: "AA" | "AI";
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

export async function loadIndex(): Promise<IndexFile> {
  return readJson<IndexFile>("index.json");
}

export async function loadTopic(topicId: string): Promise<QuestionSummary[]> {
  return readJson<QuestionSummary[]>(`topic-${topicId}.json`);
}

export async function loadQuestion(id: number | string): Promise<QuestionFull> {
  return readJson<QuestionFull>(`questions/${id}.json`);
}

export async function listAllQuestionIds(): Promise<string[]> {
  const dir = path.join(DATA_DIR, "questions");
  const names = await fs.readdir(dir);
  return names.filter((n) => n.endsWith(".json")).map((n) => n.slice(0, -5));
}

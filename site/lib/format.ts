const SUBJECT_LABELS: Record<string, string> = {
  maths_aa: "Maths AA",
  maths_ai: "Maths AI",
  physics: "Physics",
};

export function formatSubject(key: string): string {
  return SUBJECT_LABELS[key] ?? key;
}

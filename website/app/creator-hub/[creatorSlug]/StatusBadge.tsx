const LABELS: Record<string, string> = {
  idea: "Idea",
  draft: "Draft",
  researching: "Researching",
  ready: "Ready",
  recorded: "Recorded",
  published: "Published",
  archived: "Archived",
};

export function StatusBadge({ status }: { status: string }) {
  return <span className={`ch-status ${status}`}>{LABELS[status] ?? status}</span>;
}

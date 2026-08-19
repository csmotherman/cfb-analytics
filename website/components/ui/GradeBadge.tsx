import type { Grade, ValueType } from "../../lib/michigan/types";
export function GradeBadge({ grade, label, valueType }: { grade?: Grade | null; label: string; valueType: ValueType }) {
  const missing = valueType === "BENCHMARK" ? "NOT RATED" : "AFTER KICKOFF";
  const gradeType = valueType === "BENCHMARK" ? "RECRUITING" : valueType === "PROJECTED" ? "PROJECTED" : "SEASON";
  return <div className="grade-lockup"><span>{label}</span><strong>{grade ?? (valueType === "BENCHMARK" ? "NR" : "—")}</strong><small>{grade ? gradeType : missing}</small></div>;
}

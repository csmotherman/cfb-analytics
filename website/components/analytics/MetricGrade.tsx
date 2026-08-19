import type { Grade, ValueType } from "../../lib/michigan/types";
export function MetricGrade({ label, grade, nationalRank, conferenceRank, value, valueType }: { label: string; grade?: Grade | null; nationalRank?: number | null; conferenceRank?: number | null; value?: string | null; valueType: ValueType }) {
  return <div className="metric-grade"><span>{label}</span><strong>{grade ?? "—"}</strong><div><b>{nationalRank ? `#${nationalRank} nationally` : "Not ranked"}</b><i>{conferenceRank ? `#${conferenceRank} Big Ten` : "Not ranked"}</i></div><p>{value ?? (valueType === "PRESEASON" ? "Starts after kickoff" : "No stat yet")}</p><small>{valueType}</small></div>;
}

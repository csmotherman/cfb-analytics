export function PercentileBar({ value, label }: { value?: number | null; label: string }) {
  const pct = value == null ? 0 : Math.max(0, Math.min(100, value * 100));
  return <div className="percentile"><div><span>{label}</span><b>{value == null ? "Pending" : `${Math.round(pct)}th percentile`}</b></div><i><span style={{ width: `${pct}%` }} /></i></div>;
}

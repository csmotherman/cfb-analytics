import { MetricGrade } from "./MetricGrade";
export function AnalyticsPending({ area }: { area: string }) { return <div className="metric-strip"><MetricGrade label={`${area} grade`} valueType="PRESEASON"/><MetricGrade label="National rank" valueType="PRESEASON"/><MetricGrade label="Big Ten rank" valueType="PRESEASON"/></div>; }

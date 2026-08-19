import { FieldDepthChart } from "../../../components/players/FieldDepthChart";
import { projectedLineups } from "../../../lib/michigan/depth-chart";

export default function DepthChartPage() {
  const lineup = projectedLineups();
  return <div className="page-stack page-pad"><section className="page-hero"><span className="eyebrow">2026 PROJECTED STARTERS</span><h1>THE<br/>FIRST 22.</h1><p>Michigan's projected starters. Not the official depth chart.</p></section>{lineup?<><FieldDepthChart offense={lineup.offense} defense={lineup.defense}/><section className="method-note"><strong>HOW WE PICKED IT</strong><p>Recruiting grade and experience.</p></section></>:<section className="empty-state"><strong>Lineup coming soon</strong></section>}</div>;
}

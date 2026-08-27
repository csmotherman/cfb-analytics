import { AnalyticsYearSwitch } from "../../../components/AnalyticsYearSwitch";
import { UnitDetailTables } from "../../../components/UnitDetailTables";
import { unitDetail } from "../../../lib/unit-detail";

const years=Array.from({length:17},(_,i)=>2010+i);

export default async function DefenseAnalyticsPage({searchParams}:{searchParams:Promise<{year?:string}>}){
  const params=await searchParams;
  const requested=Number(params.year);
  const year=years.includes(requested)?requested:2025;
  const profile=unitDetail(year,"defense");

  return <div className="ud-page">
    <AnalyticsYearSwitch year={year} basePath="/analytics/defense"/>
    <header className="ud-hero">
      <span>{year} DEFENSE</span>
      <h1>DEFENSE ANALYTICS</h1>
      <p>Everything the offense page shows, from the other side of the ball &mdash; efficiency and explosiveness allowed, defensive line disruption, pass defense, situational stops, and takeaways. Ranked against that season&apos;s FBS field only.</p>
    </header>
    <UnitDetailTables profile={profile} side="defense"/>
  </div>;
}

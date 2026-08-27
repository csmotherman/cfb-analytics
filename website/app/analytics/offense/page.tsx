import { AnalyticsYearSwitch } from "../../../components/AnalyticsYearSwitch";
import { UnitDetailTables } from "../../../components/UnitDetailTables";
import { unitDetail } from "../../../lib/unit-detail";

const years=Array.from({length:17},(_,i)=>2010+i);

export default async function OffenseAnalyticsPage({searchParams}:{searchParams:Promise<{year?:string}>}){
  const params=await searchParams;
  const requested=Number(params.year);
  const year=years.includes(requested)?requested:2025;
  const profile=unitDetail(year,"offense");

  return <div className="ud-page">
    <AnalyticsYearSwitch year={year} basePath="/analytics/offense"/>
    <header className="ud-hero">
      <span>{year} OFFENSE</span>
      <h1>OFFENSE ANALYTICS</h1>
      <p>Every metric behind the {year} offensive profile radar, plus the full breakdown the radar doesn&apos;t have room for &mdash; success rate splits, explosiveness, offensive line, passing, situational football, and turnovers. Ranked against that season&apos;s FBS field only.</p>
    </header>
    <UnitDetailTables profile={profile} side="offense"/>
  </div>;
}

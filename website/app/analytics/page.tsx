import {OpponentAdjustedLab} from "../../components/OpponentAdjustedLab";
import {opponentAdjustedLab,opponentAdjustedLabSeasons} from "../../lib/opponent-adjusted-lab";

export const metadata={
  title:"Opponent-Adjusted College Football Analytics",
  description:"Build custom opponent-adjusted college football charts, game views and national rankings for any FBS team.",
};

export default async function AnalyticsPage({searchParams}:{searchParams:Promise<{year?:string}>}){
  const params=await searchParams;
  const seasons=opponentAdjustedLabSeasons();
  const requested=Number(params.year);
  const fallback=seasons.includes(2025)?2025:seasons.at(-1)??2025;
  const year=seasons.includes(requested)?requested:fallback;
  const data=opponentAdjustedLab(year);

  return <div>
    {data?<OpponentAdjustedLab data={data} seasons={seasons}/>:<section className="oa-unavailable">
      <span>OPPONENT-ADJUSTED ANALYTICS LAB</span>
      <h1>Analytics data is being prepared.</h1>
      <p>The new analytics experience uses compact schedule-adjusted artifacts with strict leave-one-game-out game grading. Once the season artifact is published, this page unlocks custom team, game-range, chart and national-ranking views.</p>
    </section>}
  </div>;
}

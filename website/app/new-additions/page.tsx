import {currentRoster} from "../../lib/michigan/roster";
import {classLabel} from "../../lib/michigan/format";
import {readJson} from "../../lib/server-data";
import {NewAdditionsTabs,type NewAdditionRow} from "../../components/NewAdditionsTabs";

type CareerRow={playerId:string;seasons:Array<{season:number;team:string;teamId:number}>};

export default function NewAdditions(){
  const roster=currentRoster();
  const careers=readJson<CareerRow[]>("data","published","2026","michigan","player-career-stats.json")??[];
  const careerById=new Map(careers.map(row=>[row.playerId,row]));
  const additions=roster.filter(player=>player.rosterStatus==="FRESHMAN"||player.rosterStatus==="TRANSFER");

  const previousTeamId=(playerId:string,previousTeam?:string|null)=>{
    const seasons=careerById.get(playerId)?.seasons??[];
    return [...seasons].reverse().find(row=>row.team!=="Michigan"&&(previousTeam?row.team===previousTeam:true))?.teamId??null;
  };

  const rows:NewAdditionRow[]=additions.map(player=>({
    id:player.id,
    firstName:player.firstName,
    lastName:player.lastName,
    position:player.position??"ATH",
    jersey:player.jersey??null,
    classLabel:classLabel(player.year),
    type:player.rosterStatus as "FRESHMAN"|"TRANSFER",
    previousTeam:player.previousTeam??null,
    previousTeamId:player.rosterStatus==="TRANSFER"?previousTeamId(player.id,player.previousTeam):null,
    recruitRating:player.compositeRating??null,
    recruitingRatingStatus:player.recruitingRatingStatus??(player.compositeRating!=null?"RATED":"UNRATED"),
    stars:player.stars??null,
    nationalRecruitRank:player.nationalRecruitRank??null,
  }));

  const freshmen=rows.filter(player=>player.type==="FRESHMAN");
  const transfers=rows.filter(player=>player.type==="TRANSFER").sort((a,b)=>`${a.lastName}${a.firstName}`.localeCompare(`${b.lastName}${b.firstName}`));

  return <div className="new-additions-page">
    <section className="new-additions-hero">
      <div className="wrap">
        <span>2026 ROSTER</span>
        <h1>NEW ADDITIONS</h1>
        <p>Every new Wolverine in one place — switch between the incoming freshman class and transfer additions without leaving the page.</p>
        <div className="new-additions-summary"><b>{rows.length}<small>TOTAL</small></b><b>{freshmen.length}<small>FRESHMEN</small></b><b>{transfers.length}<small>TRANSFERS</small></b></div>
      </div>
    </section>

    <div className="wrap new-additions-content"><NewAdditionsTabs freshmen={freshmen} transfers={transfers}/></div>
  </div>;
}

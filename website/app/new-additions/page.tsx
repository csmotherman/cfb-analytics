import Link from "next/link";
import {currentRoster} from "../../lib/michigan/roster";
import {classLabel} from "../../lib/michigan/format";
import {readJson} from "../../lib/server-data";
import {teamLogoUrl} from "../../lib/team-assets";

type CareerRow={playerId:string;seasons:Array<{season:number;team:string;teamId:number}>};

export default function NewAdditions(){
  const roster=currentRoster();
  const careers=readJson<CareerRow[]>("data","published","2026","michigan","player-career-stats.json")??[];
  const careerById=new Map(careers.map(row=>[row.playerId,row]));
  const additions=roster.filter(player=>player.rosterStatus==="FRESHMAN"||player.rosterStatus==="TRANSFER").sort((a,b)=>{
    if(a.rosterStatus!==b.rosterStatus)return a.rosterStatus==="FRESHMAN"?-1:1;
    return `${a.lastName}${a.firstName}`.localeCompare(`${b.lastName}${b.firstName}`);
  });
  const freshmen=additions.filter(player=>player.rosterStatus==="FRESHMAN").length;
  const transfers=additions.length-freshmen;

  const previousTeamId=(playerId:string,previousTeam?:string|null)=>{
    const seasons=careerById.get(playerId)?.seasons??[];
    return [...seasons].reverse().find(row=>row.team!=="Michigan"&&(previousTeam?row.team===previousTeam:true))?.teamId??null;
  };

  return <div className="new-additions-page">
    <section className="new-additions-hero">
      <div className="wrap">
        <span>2026 ROSTER</span>
        <h1>NEW ADDITIONS</h1>
        <p>Every new Wolverine in one place — incoming freshmen and transfers, with where they came from and where they are now.</p>
        <div className="new-additions-summary"><b>{additions.length}<small>TOTAL</small></b><b>{freshmen}<small>FRESHMEN</small></b><b>{transfers}<small>TRANSFERS</small></b></div>
      </div>
    </section>

    <div className="wrap new-additions-content">
      <div className="new-additions-head"><span>PLAYER</span><span>CLASS</span><span>PATH TO MICHIGAN</span></div>
      <div className="new-additions-list">
        {additions.map(player=>{
          const isFreshman=player.rosterStatus==="FRESHMAN";
          const oldTeamId=previousTeamId(player.id,player.previousTeam);
          const origin=isFreshman?"HIGH SCHOOL":(player.previousTeam??"Previous team");
          return <Link href={`/players/${player.id}`} key={player.id} className="new-addition-row">
            <div className="new-addition-player"><strong>{player.firstName} {player.lastName}</strong><small>{player.position??"ATH"}{player.jersey!=null?` · #${player.jersey}`:""}</small></div>
            <div className="new-addition-class"><strong>{classLabel(player.year)}</strong><small>{isFreshman?"FRESHMAN":"TRANSFER"}</small></div>
            <div className="new-addition-path">
              <div className="new-addition-origin">
                {isFreshman?<span className="hs-badge">HS</span>:oldTeamId?<img src={teamLogoUrl(oldTeamId,64)} alt={`${origin} logo`}/>:<span className="hs-badge">—</span>}
                <small>{origin}</small>
              </div>
              <b>→</b>
              <div className="new-addition-origin michigan-destination"><img src={teamLogoUrl(130,64)} alt="Michigan logo"/><small>MICHIGAN</small></div>
            </div>
            <span className="new-addition-arrow">›</span>
          </Link>;
        })}
      </div>
    </div>
  </div>;
}

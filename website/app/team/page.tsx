import Link from "next/link";
import TeamDepthFormats from "../../components/TeamDepthFormats";
import TeamBattleList,{type TeamBattle} from "../../components/TeamBattleList";
import {FieldDepthChart} from "../../components/players/FieldDepthChart";
import {researchedDepthChart} from "../../lib/michigan/depth-chart";

export default function TeamPage(){
  const chart=researchedDepthChart();
  const battles:TeamBattle[]=[
    {position:"WR3",title:"Who earns the third receiver role?",players:["Jaime Ffrench","Travis Johnson","Salesi Moa","Channing Goodwin"],detail:"Andrew Marsh and JJ Buchanan are the clearest top-two options. The next major receiver role remains fluid, with multiple players still pushing for snaps."},
    {position:"LT / G",title:"How does the offensive line settle?",players:["Blake Frazier","Andrew Babalola","Evan Link","Nathan Efobi","Brady Norton"],detail:"Jake Guarnera and Andrew Sprague look like the safest pieces. Left tackle and both guard spots still have legitimate competition, so the final five can still move."},
    {position:"LB",title:"Who separates at linebacker?",players:["Troy Bowles","Chase Taylor","Nathaniel Staehling","Nate Owusu-Boateng"],detail:"Michigan has several playable options but less certainty about the final snap distribution. This is one of the most important defensive battles to watch before Week 1."},
    {position:"S",title:"How deep will the safety rotation go?",players:["Rod Moore","Chris Bracy","Mason Curtis","Jordan Young"],detail:"Moore and Bracy have the inside track, but Curtis and Young are talented enough to force a real rotation. The question is less whether Michigan has options and more how snaps get divided."},
  ];

  return <div className="mock-home team-formation-home"><div className="mock-shell">
    <section className="mock-section team-formation-intro">
      <header><div><span className="mock-eyebrow maize">2026 MICHIGAN · PROJECTED</span><h1>DEPTH CHART</h1><p>Desktop shows the full formation. Mobile switches automatically to the compact depth directory for faster scanning.</p></div><Link href="/team/roster">PLAYER DIRECTORY <b>›</b></Link></header>
    </section>

    {chart?<>
      <div className="team-depth-desktop"><FieldDepthChart offense={chart.offense} defense={chart.defense} specialists={chart.specialists}/></div>
      <div className="team-depth-mobile"><TeamDepthFormats offense={chart.offense} defense={chart.defense} specialists={chart.specialists} format={2}/></div>
    </>:<section className="mock-section"><div className="player-focus-empty"><b>Projected depth chart unavailable.</b></div></section>}

    <section className="mock-section team-battles-section">
      <header><div><span className="mock-eyebrow maize">FALL CAMP</span><h2>POSITION BATTLES</h2></div><span>Tap a battle to expand</span></header>
      <TeamBattleList battles={battles}/>
    </section>

    <section className="mock-section team-formation-footer">
      <div><small>UNOFFICIAL PROJECTION</small><p>Michigan has not published an official 2026 depth chart. This page is a researched projection and will change as camp roles become clearer.</p></div><Link className="mock-outline-button" href="/team/roster">BROWSE EVERY PLAYER <b>›</b></Link>
    </section>
  </div></div>;
}

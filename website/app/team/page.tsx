import Link from "next/link";
import {currentRoster} from "../../lib/michigan/roster";
import {classLabel} from "../../lib/michigan/format";
import TeamDepthBoard,{type DepthRow} from "../../components/TeamDepthBoard";

const normalize=(value:string)=>value.toLowerCase().replace(/[^a-z0-9]/g,"");

export default function TeamPage(){
  const roster=currentRoster();
  const byName=(name:string)=>roster.find(player=>normalize(`${player.firstName} ${player.lastName}`)===normalize(name));
  const player=(name:string)=>{const p=byName(name);return p?{id:p.id,name:`${p.firstName} ${p.lastName}`,jersey:p.jersey,position:p.position,year:classLabel(p.year),image:p.playerImageUrl}:null;};
  const players=(names:string[])=>names.map(player).filter(Boolean) as NonNullable<ReturnType<typeof player>>[];
  const row=(position:string,starter:string[],next:string[],battle=false,note?:string):DepthRow=>({position,starter:players(starter),next:players(next),battle,note});

  const offense:DepthRow[]=[
    row("QB",["Bryce Underwood"],["Tommy Carr","Brayden Fowler-Nicolosi"],false,"Underwood is the clear QB1; the backup job remains competitive."),
    row("RB",["Jordan Marshall","Savion Hiter"],["Bryson Kuzdzal"],false,"Marshall is RB1, but Hiter is expected to have a real 1A/1B role."),
    row("WR",["Andrew Marsh"],["Travis Johnson","Channing Goodwin"]),
    row("WR",["JJ Buchanan"],["Salesi Moa","Kendrick Bell"]),
    row("WR3",["Jaime Ffrench"],["Travis Johnson","Salesi Moa","Channing Goodwin"],true,"This is one of camp's most fluid skill-position battles."),
    row("TE",["Zack Marshall"],["Hogan Hansen","Deakon Tonielli"],true,"Expect rotation here even if Marshall opens with the first group."),
    row("LT",["Blake Frazier"],["Andrew Babalola","Evan Link"],true,"Frazier has the edge, but left tackle is not fully settled."),
    row("LG",["Evan Link"],["Brady Norton"],true),
    row("C",["Jake Guarnera"],["Houston Ka'aha'aina-Torres"]),
    row("RG",["Nathan Efobi"],["Brady Norton","Evan Link"],true),
    row("RT",["Andrew Sprague"],["Malakai Lee"]),
  ];

  const defense:DepthRow[]=[
    row("DE",["John Henry Daley"],["Dom Nichols","Nate Marshall"]),
    row("DT",["Trey Pierce"],["Jonah Lea'ea","Deyvid Palepale"]),
    row("DT",["Enow Etta"],["Deyvid Palepale","Bobby Kanka"]),
    row("DE",["Cam Brandt"],["Dom Nichols","Benny Patterson"],true,"Nichols is pushing hard for starter-level pass-rush snaps."),
    row("LB",["Troy Bowles"],["Nathaniel Staehling","Nate Owusu-Boateng"]),
    row("LB",["Chase Taylor"],["Nathaniel Staehling","Nate Owusu-Boateng"],true,"Linebacker remains one of the least settled groups in camp."),
    row("CB",["Jyaire Hill"],["Shamari Earls","Jo'Ziah Edmond"]),
    row("CB",["Smith Snowden"],["Shamari Earls","Jamarion Vincent"]),
    row("NICKEL",["Zeke Berry"],["Smith Snowden","Jordan Young"]),
    row("S",["Rod Moore"],["Mason Curtis","Jordan Young"]),
    row("S",["Chris Bracy"],["Mason Curtis","Jordan Young"],true,"Whittingham has said Moore and Bracy have the inside track, but Curtis remains in the mix."),
  ];

  const special:DepthRow[]=[
    row("K",["Trey Butkowski"],[]),
    row("P",["Cameron Brown"],[]),
    row("KR",["Salesi Moa","Savion Hiter"],["Smith Snowden"]),
    row("PR",["Salesi Moa"],["Andrew Marsh","Smith Snowden"],true,"Return roles are still being sorted during camp."),
  ];

  const returning=roster.filter(p=>p.rosterStatus==="RETURNING").length;
  const transfers=roster.filter(p=>p.rosterStatus==="TRANSFER").length;
  const freshmen=roster.filter(p=>p.rosterStatus==="FRESHMAN").length;

  return <div className="team-hub-page">
    <section className="team-hub-hero"><div className="wrap"><span className="kicker maize">2026 MICHIGAN · FALL CAMP</span><h1>WHO'S ACTUALLY<br/><b>PLAYING?</b></h1><p>A fan-first projected depth chart built from Michigan's current roster, fall-camp reporting and the latest position-battle updates. This is a projection—not an official Michigan release.</p><div className="team-hub-actions"><Link href="/team/roster">FULL ROSTER →</Link><Link href="/team/depth-chart">FORMATION VIEW →</Link></div></div></section>

    <main className="wrap team-hub-main">
      <section className="team-hub-snapshot"><span><small>ROSTER</small><b>{roster.length}</b></span><span><small>RETURNING</small><b>{returning}</b></span><span><small>TRANSFERS</small><b>{transfers}</b></span><span><small>FRESHMEN</small><b>{freshmen}</b></span></section>

      <section className="team-depth-section"><header><div><span className="kicker maize">PROJECTED DEPTH CHART</span><h2>The lineup Michigan is trending toward.</h2><p>Updated August 21. Yellow battle labels mean the job or rotation is still genuinely unsettled.</p></div><span className="team-depth-status">UNOFFICIAL · FALL CAMP</span></header><TeamDepthBoard offense={offense} defense={defense} special={special}/></section>

      <section className="team-camp-read"><div><span className="kicker maize">WHAT CHANGED IN CAMP</span><h2>The spots fans should actually watch.</h2></div><div className="team-camp-grid"><article><b>01</b><h3>WR3 is wide open</h3><p>Andrew Marsh and JJ Buchanan are established at the top. Jaime Ffrench, Travis Johnson, Salesi Moa and Channing Goodwin are still fighting for the next major role.</p></article><article><b>02</b><h3>The offensive line is not finished</h3><p>Jake Guarnera and Andrew Sprague look safest. Left tackle and both guard spots still have legitimate competition.</p></article><article><b>03</b><h3>Linebacker needs separation</h3><p>Troy Bowles brings the most experience, but Chase Taylor, Nathaniel Staehling and Nate Owusu-Boateng are all pushing for meaningful snaps.</p></article><article><b>04</b><h3>Safety has real depth</h3><p>Rod Moore and Chris Bracy have the inside track, with Mason Curtis and Jordan Young strong enough to keep the rotation fluid.</p></article></div></section>

      <section className="team-hub-note"><strong>HOW TO READ THIS</strong><p>Michigan has not published an official 2026 depth chart. This page combines the official 2026 roster with current fall-camp reporting and clearly marks unsettled jobs instead of presenting speculation as fact.</p></section>
    </main>
  </div>;
}

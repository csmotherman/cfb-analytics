import Link from "next/link";
import { avgMargin, fieldWinPct, findDynamicIdentity, findPowerRow, rankOf, tournamentRows } from "../../../../lib/data";

function label(value:unknown){
  if(value===null||value===undefined||value==="") return "—";
  return String(value).replaceAll("-"," ").replace(/\b\w/g,c=>c.toUpperCase());
}

type GradeRow={
  key:string;
  section:string;
  label:string;
  status?:string;
  percentile?:number|null;
  grade?:string|null;
  available?:boolean;
  description?:string|null;
};

function pctText(value:unknown){
  const n=Number(value);
  return Number.isFinite(n)?`${Math.round(n)}th percentile`:"Not yet available";
}

function gradeClass(grade:unknown){
  const g=String(grade||"");
  if(g.startsWith("A")) return "grade-badge grade-a";
  if(g.startsWith("B")) return "grade-badge grade-b";
  if(g.startsWith("C")) return "grade-badge grade-c";
  if(g.startsWith("D")) return "grade-badge grade-d";
  if(g==="F") return "grade-badge grade-f";
  return "grade-badge grade-na";
}

function GradeCard({row}:{row:GradeRow}){
  const available=row.available!==false&&row.percentile!==null&&row.percentile!==undefined;
  return <div className="grade-card">
    <div className="grade-card-top">
      <div>
        <div className="grade-label">{row.label}</div>
        {row.status&&row.status!=="READY"?<div className="metric-status">{label(row.status)}</div>:null}
      </div>
      <div className={gradeClass(row.grade)}>{available?(row.grade||"—"):"—"}</div>
    </div>
    <div className="grade-percentile">{available?pctText(row.percentile):"Not yet available"}</div>
    {row.description?<div className="grade-description">{row.description}</div>:null}
  </div>;
}

function GradeSection({title,rows}:{title:string;rows:GradeRow[]}){
  if(!rows.length) return null;
  return <div className="grade-section">
    <h3>{title}</h3>
    <div className="grade-grid">{rows.map(row=><GradeCard key={row.key} row={row}/>)}</div>
  </div>;
}

export default async function TeamSeason({params}:{params:Promise<{team:string;season:string}>}){
  const p=await params; const team=decodeURIComponent(p.team); const season=Number(p.season);
  const power=findPowerRow(team,season); const identity=findDynamicIdentity(team,season);
  const total=tournamentRows().length;
  const rank=power?rankOf(power):null;
  const win=power?fieldWinPct(power):null;
  const margin=power?avgMargin(power):null;
  const style=identity?.identityStyle||{};
  const tags=Array.isArray(identity?.identityTags)?identity.identityTags:[];
  const grades=(Array.isArray(identity?.grades)?identity.grades:[]) as GradeRow[];
  const offenseGrades=grades.filter(g=>g.section==="offense");
  const defenseGrades=grades.filter(g=>g.section==="defense");
  const styleGrades=grades.filter(g=>g.section==="style");
  const schemeGrades=grades.filter(g=>g.section==="scheme");
  const formGrades=grades.filter(g=>g.section==="form");

  return <>
    <section className="hero">
      <div className="muted">TEAM-SEASON</div>
      <h1>{season} {team}</h1>
      <div className="grid">
        <div>
          <div className="muted">Historical standing</div>
          <div className="big-number">{rank?`#${rank}`:"—"}</div>
          {rank&&total?<div className="muted">out of {total.toLocaleString()} team-seasons</div>:null}
        </div>
        <div>
          <div className="muted">How often they beat the field</div>
          <div className="big-number">{win!==null?(win*100).toFixed(1)+"%":"—"}</div>
          {win!==null?<div className="muted">Expected to beat about {Math.round(win*10)} of every 10 historical teams</div>:null}
        </div>
        <div>
          <div className="muted">Average neutral-field edge</div>
          <div className="big-number">{margin!==null?`${margin>=0?"+":""}${margin.toFixed(1)}`:"—"}</div>
          <div className="muted">model points per matchup</div>
        </div>
      </div>
      <div className="row" style={{marginTop:16}}>
        <Link className="button" href={`/simulator?homeYear=${season}&homeTeam=${encodeURIComponent(team)}`}>Simulate them</Link>
        <Link className="button secondary" href={`/compare?aYear=${season}&aTeam=${encodeURIComponent(team)}`}>Compare them</Link>
      </div>
    </section>

    <section className="panel">
      <div className="muted">TEAM IDENTITY</div>
      <h2 style={{marginBottom:8}}>{identity?.identityName||"—"}</h2>
      {tags.length?<div style={{marginBottom:14}}>{tags.map(tag=><span className="pill" key={tag}>{tag}</span>)}</div>:null}
      {identity?.identitySummary?<p style={{fontSize:17,lineHeight:1.6}}>{identity.identitySummary}</p>:null}
      {!identity?<div className="notice">No dynamic identity found for this team-season. Generate it with <code>python -m cfb_analytics.profiles.dynamic_profiles</code>.</div>:null}
    </section>

    {identity?<section className="panel">
      <div className="muted">SEASON-RELATIVE GRADES</div>
      <h2>How good were they?</h2>
      <p className="muted">Grades compare this team to its season peers. Letter grades are backed by the same 0–100 percentile scale used by the profile system.</p>
      <GradeSection title="Offense" rows={offenseGrades}/>
      <GradeSection title="Defense" rows={defenseGrades}/>
      <GradeSection title="Style & tendencies" rows={styleGrades}/>
      <GradeSection title="Scheme" rows={schemeGrades}/>
      <GradeSection title="Consistency & volatility" rows={formGrades}/>
    </section>:null}

    {identity?<section className="panel">
      <h2>How did they play?</h2>
      <div className="grid">
        <div><div className="muted">Usage</div><h3>{label(style.usage)}</h3></div>
        <div><div className="muted">Method</div><h3>{label(style.method)}</h3></div>
        <div><div className="muted">Drive shape</div><h3>{label(style.paceShape)}</h3></div>
        <div><div className="muted">Efficiency shape</div><h3>{label(style.efficiencyShape)}</h3></div>
        <div><div className="muted">Offensive strength</div><h3>{label(style.attackDriver)}</h3></div>
        <div><div className="muted">Commitment</div><h3>{label(style.commitment)}</h3></div>
        <div><div className="muted">Team structure</div><h3>{label(style.teamStructure)}</h3></div>
        <div><div className="muted">Effectiveness</div><h3>{label(style.effectiveness)}</h3></div>
        <div><div className="muted">Offense consistency</div><h3>{label(style.offenseConsistency||"typical")}</h3></div>
        <div><div className="muted">Defense consistency</div><h3>{label(style.defenseConsistency||"typical")}</h3></div>
      </div>
    </section>:null}

    <section className="panel">
      <h2>What should a fan know?</h2>
      <p>The identity is season-wide. Grades show how each component ranked against that season&apos;s teams, while tags add the strongest tendencies, quality signals, consistency, and late-season trajectory.</p>
      <p className="muted">Metrics marked Planned, Deferred, or Partial are shown transparently instead of receiving invented grades.</p>
    </section>
  </>;
}

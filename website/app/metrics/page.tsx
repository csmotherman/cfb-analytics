const metrics=[
  ["Staying on Schedule","Success Rate","How often does this team consistently win downs?"],
  ["Big-Play Threat","Explosive Play Rate","How often can one snap flip the field?"],
  ["Snap-to-Snap Production","Yards Per Play","How much does the team get out of a typical play?"],
  ["Drive Power","Yards Per Possession","How much offense does each possession create?"],
  ["Cash In","Points Per Opportunity","When scoring chances appear, does the team turn them into points?"],
  ["Field Position Edge","Average Starting Field Position","Who is consistently playing on the shorter field?"],
  ["Disruption","Havoc / TFL / sacks / turnovers","How often does the defense wreck the play before it develops?"],
  ["Run Game","Opponent-adjusted rushing attack","How good is the team at actually running the ball?"],
  ["Passing Attack","Opponent-adjusted passing attack","How dangerous and efficient is the passing game?"],
];

export default function Metrics(){return <><h1>Metrics, in fan language</h1><p className="muted">Pilot glossary. The website should answer the football question first and keep the technical label available underneath.</p><div className="grid">{metrics.map(([surface,technical,question])=><section className="card" key={surface}><h2>{surface}</h2><p>{question}</p><p className="muted">Technical: {technical}</p></section>)}</div></>;}

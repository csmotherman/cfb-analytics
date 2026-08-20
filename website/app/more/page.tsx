import Link from "next/link";

const sections=[
  {href:"/analytics",label:"Analytics",description:"Team performance, efficiency, player grades, and Michigan data tools.",tag:"DATA"},
  {href:"/articles",label:"News & Analysis",description:"Michigan stories, notebooks, previews, and long-form analysis.",tag:"READ"},
  {href:"/history",label:"Michigan History",description:"Explore past seasons, teams, results, and program history.",tag:"ARCHIVE"},
  {href:"/polls",label:"Fan Polls",description:"Vote on Michigan questions and see where fans stand.",tag:"FANS"},
  {href:"/metrics",label:"Metrics",description:"Browse the definitions and advanced metrics used throughout the site.",tag:"REFERENCE"},
  {href:"/methodology",label:"Methodology",description:"See how ratings, grades, projections, and site data are built.",tag:"HOW IT WORKS"},
] as const;

export default function More(){
  return <div className="more-page">
    <div className="wrap more-page-inner">
      <header className="more-page-header">
        <span>EXPLORE</span>
        <h1>MORE MICHIGAN</h1>
        <p>Everything beyond the main team, schedule, and recruiting tabs.</p>
      </header>
      <div className="more-hub-grid">
        {sections.map(item=><Link href={item.href} key={item.href} className="more-hub-card">
          <small>{item.tag}</small>
          <div><h2>{item.label}</h2><p>{item.description}</p></div>
          <span aria-hidden="true">›</span>
        </Link>)}
      </div>
    </div>
  </div>;
}

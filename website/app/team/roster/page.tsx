import Link from "next/link";
import {RosterExplorer} from "../../../components/players/RosterExplorer";
import {currentRoster} from "../../../lib/michigan/roster";

export default function RosterPage(){
  const roster=currentRoster();
  const returning=roster.filter(p=>p.rosterStatus==="RETURNING").length;
  const transfers=roster.filter(p=>p.rosterStatus==="TRANSFER").length;
  const freshmen=roster.filter(p=>p.rosterStatus==="FRESHMAN").length;
  return <div className="roster-directory-page">
    <div className="mock-shell roster-directory-shell">
      <section className="roster-directory-hero">
        <div><span className="mock-eyebrow maize">2026 MICHIGAN</span><h1>PLAYER DIRECTORY</h1><p>Find any Wolverine quickly by name, number, position, class or roster status.</p></div>
        <Link href="/team" className="mock-outline-button">DEPTH CHART <b>›</b></Link>
      </section>
      <section className="roster-directory-summary"><span><small>ROSTER</small><b>{roster.length}</b></span><span><small>RETURNING</small><b>{returning}</b></span><span><small>TRANSFERS</small><b>{transfers}</b></span><span><small>FRESHMEN</small><b>{freshmen}</b></span></section>
      <RosterExplorer players={roster}/>
    </div>
  </div>;
}

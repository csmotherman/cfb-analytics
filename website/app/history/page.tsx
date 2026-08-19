import Link from "next/link";
import { SeasonSelector } from "../../components/ui/SeasonSelector";
import { historySeasons } from "../../lib/michigan/history";
export default function HistoryPage(){const seasons=historySeasons();return <div className="page-stack page-pad history-page"><section className="page-hero history-index-hero"><span className="eyebrow">MICHIGAN HISTORY · 2010–2025</span><h1>SEASON HISTORY.</h1><p>Records, coaches, rosters and results.</p></section><SeasonSelector/><div className="history-grid">{seasons.map(row=><Link className="season-tile" href={`/history/${row.season}`} key={row.season}><strong>{row.season}</strong><p>{row.available?`${row.wins}–${row.losses}`:"—"}</p><b>{row.coach}</b></Link>)}</div></div>}

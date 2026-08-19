import Link from "next/link";
const links=[["/recruiting","Recruiting"],["/recruiting/portal","Transfers"],["/analytics","Analytics"],["/history","History"],["/articles","Articles"],["/methodology","Methodology"]];
export default function More(){return <div className="wrap route-page"><span className="kicker navy">EXPLORE</span><h1>More Michigan</h1><div className="more-grid">{links.map(([href,label])=><Link href={href} key={href}>{label}<span>→</span></Link>)}</div></div>}

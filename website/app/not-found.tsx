import Link from "next/link";

export default function NotFound(){
  return <div className="mock-home"><div className="mock-shell">
    <section className="mock-section" style={{marginTop:24}}>
      <span className="mock-eyebrow maize">404 · PAGE NOT FOUND</span>
      <h1 style={{margin:"8px 0 10px"}}>LOST IN THE BIG HOUSE</h1>
      <p style={{maxWidth:620}}>That Michigan Football Focus page does not exist or has moved. Head back home or jump straight into the 2026 team.</p>
      <div style={{display:"flex",gap:10,flexWrap:"wrap",marginTop:20}}>
        <Link className="mock-outline-button" href="/">BACK HOME <b>›</b></Link>
        <Link className="mock-outline-button" href="/team">EXPLORE THE TEAM <b>›</b></Link>
      </div>
    </section>
  </div></div>;
}

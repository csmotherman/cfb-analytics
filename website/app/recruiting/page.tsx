import Link from "next/link";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { currentRecruitingClass, gradeScale } from "../../lib/michigan/recruiting";

export default function RecruitingPage() {
  const data = currentRecruitingClass();
  const recruits = data?.recruits ?? [];
  const stars = (count: number | null | undefined) => "★".repeat(count ?? 0) + "☆".repeat(5 - (count ?? 0));
  return <div className="compact-page">
    <section className="page-hero recruiting-hero"><span className="eyebrow">2026 RECRUITING CLASS</span><h1>THE NEXT<br/>WAVE.</h1><p>Every Michigan commitment, star rating, national rank and SOAR grade.</p><div className="recruiting-score"><div><span>NATIONAL CLASS RANK</span><strong>#{data?.ranking?.rank ?? "—"}</strong></div><div><span>CLASS POINTS</span><strong>{data?.ranking?.points?.toFixed(2) ?? "—"}</strong></div><div><span>COMMITMENTS</span><strong>{recruits.length}</strong></div><div><span>BLUE CHIPS</span><strong>{recruits.filter(r => (r.stars ?? 0) >= 4).length}</strong></div></div></section>
    <section><SectionHeader eyebrow="THE CLASS" title="Michigan's next wave.">Ratings, stars and each recruit's SOAR grade.</SectionHeader><div className="recruit-board">{recruits.map(recruit => <Link href={`/recruiting/players/${recruit.id}`} key={recruit.id} className="recruit-row"><div className="recruit-rank"><small>NATL</small><strong>#{recruit.ranking ?? "—"}</strong></div><div><span className="recruit-stars" aria-label={`${recruit.stars ?? 0} stars`}>{stars(recruit.stars)}</span><h3>{recruit.name}</h3><p>{recruit.position ?? "ATH"} · {recruit.school ?? "School unavailable"} · {[recruit.city,recruit.stateProvince].filter(Boolean).join(", ")}</p></div><div className="recruit-rating"><small>RATING</small><strong>{recruit.rating?.toFixed(4) ?? "—"}</strong></div><div className="recruit-grade"><small>SOAR GRADE</small><strong>{recruit.grade ?? "NR"}</strong></div></Link>)}</div></section>
    <section className="grade-method"><SectionHeader eyebrow="SOAR GRADE SCALE" title="One grade. Easy to read.">Each national recruiting rating becomes an F–S+ score.</SectionHeader><div>{gradeScale.map(([grade, floor]) => <span key={grade}><strong>{grade}</strong><small>{floor}</small></span>)}</div></section>
    <div className="cta-row"><Link className="button" href="/recruiting/national">NATIONAL RECRUITS</Link><Link className="button secondary" href="/team/roster">ROSTER GRADES</Link><Link className="button secondary" href="/recruiting/portal">TRANSFER PORTAL</Link></div>
  </div>;
}

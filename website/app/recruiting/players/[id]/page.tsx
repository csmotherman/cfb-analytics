import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { recruitById } from "../../../../lib/michigan/recruiting";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const recruit = recruitById((await params).id);
  if (!recruit) return { title: "Recruit not found" };
  const title = `${recruit.name} recruiting profile`;
  const description = `2026 ${recruit.position ?? "prospect"} committed to ${recruit.committedTo ?? "uncommitted"}.`;
  return { title, description, openGraph: { title, description, images: [] }, twitter: { title, description, images: [] } };
}

export default async function RecruitPage({ params }: Props) {
  const recruit = recruitById((await params).id);
  if (!recruit) notFound();
  const stars = Math.max(0, Math.min(5, recruit.stars ?? 0));
  return <article className="recruit-dossier compact-page">
    <header><div><span className="eyebrow">2026 RECRUIT · #{recruit.ranking ?? "—"} NATIONALLY</span><h1>{recruit.name}</h1><p>{recruit.position ?? "ATH"} · {recruit.school ?? "School unavailable"} · {[recruit.city, recruit.stateProvince].filter(Boolean).join(", ")}</p></div><strong className="dossier-grade">{recruit.grade ?? "NR"}<small>PROSPECT GRADE</small></strong></header>
    <section className="dossier-grid"><div><span>COMMITTED</span><strong>{recruit.committedTo ?? "UNCOMMITTED"}</strong></div><div><span>STARS</span><strong className="star-cell">{"★".repeat(stars)}{"☆".repeat(5-stars)}</strong></div><div><span>COMPOSITE</span><strong>{recruit.rating?.toFixed(4) ?? "—"}</strong></div><div><span>NATIONAL RANK</span><strong>#{recruit.ranking ?? "—"}</strong></div><div><span>HEIGHT</span><strong>{recruit.height ? `${Math.floor(recruit.height/12)}′${recruit.height%12}″` : "—"}</strong></div><div><span>WEIGHT</span><strong>{recruit.weight ? `${recruit.weight} LBS` : "—"}</strong></div></section>
    <section className="dossier-note"><span className="eyebrow">THE GRADE</span><p>The grade comes from his national recruiting rating. It measures recruiting profile, not college production.</p></section>
    <footer>{recruit.committedTo && <Link className="button" href={`/recruiting/teams/${encodeURIComponent(recruit.committedTo)}`}>VIEW TEAM CLASS</Link>}<Link className="button secondary" href="/recruiting/national">NATIONAL BOARD</Link></footer>
  </article>;
}

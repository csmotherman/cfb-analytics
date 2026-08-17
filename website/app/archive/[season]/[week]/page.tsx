import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ArchiveBrowser } from "../../../../components/ArchiveBrowser";
import { ArchiveWeekView } from "../../../../components/ArchiveWeekView";
import { ARCHIVE_SEASONS, getArchiveIndex, getArchiveWeek } from "../../../../lib/archive";

export async function generateMetadata({ params }: { params: Promise<{ season: string; week: string }> }): Promise<Metadata> {
  const { season: seasonRaw, week: weekRaw } = await params;
  const season = Number(seasonRaw);
  const week = Number(weekRaw);
  return {
    title: `${season} Week ${week} Beat the Model Archive`,
    description: `See the ${season} Week ${week} Beat the Model Official 15 and model result.`,
  };
}

export default async function ArchiveWeekPage({ params }: { params: Promise<{ season: string; week: string }> }) {
  const { season: seasonRaw, week: weekRaw } = await params;
  const season = Number(seasonRaw);
  const week = Number(weekRaw);
  if (!ARCHIVE_SEASONS.includes(season) || !Number.isInteger(week) || week < 0 || week > 20) notFound();

  const data = getArchiveWeek(season, week);
  const index = getArchiveIndex();

  return (
    <>
      <Link className="back-link" href="/archive">← Archive</Link>

      <section className="archive-page-head btm-archive-page-head">
        <div>
          <span className="eyebrow">BEAT THE MODEL ARCHIVE</span>
          <h1>{season} <span>/</span> Week {week}</h1>
          <p>The Official 15 and The Model's straight-up result, preserved exactly as a weekly competition.</p>
        </div>
        <div className="archive-page-chip">
          <span>Scoring</span>
          <strong>1 point</strong>
          <small>per correct winner</small>
        </div>
      </section>

      <ArchiveBrowser index={index} />

      {data.games.length ? (
        <ArchiveWeekView data={data} />
      ) : (
        <section className="empty-panel archive-empty">
          <span className="eyebrow">NO DATA</span>
          <h2>This archive week has not been generated on this checkout.</h2>
          <p>Republish the website data from the repository root. Historical model picks are never fabricated after the result.</p>
        </section>
      )}
    </>
  );
}

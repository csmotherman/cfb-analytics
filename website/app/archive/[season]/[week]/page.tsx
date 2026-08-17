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
    title: `${season} Week ${week} College Football Archive`,
    description: `Browse the ${season} college football Week ${week} model archive, market lines, picks, and results.`,
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

      <section className="archive-page-head">
        <div>
          <span className="eyebrow">PREDICTION ARCHIVE</span>
          <h1>{season} <span>/</span> Week {week}</h1>
          <p>Historical market line, the model's margin prediction, and the result—kept together in one view.</p>
        </div>
        <div className="archive-page-chip">
          <span>Comparable seasons</span>
          <strong>2014–2025</strong>
          <small>2020 excluded</small>
        </div>
      </section>

      <ArchiveBrowser index={index} />

      {data.games.length ? (
        <ArchiveWeekView data={data} />
      ) : (
        <section className="empty-panel archive-empty">
          <span className="eyebrow">NO DATA</span>
          <h2>This archive week has not been generated on this checkout.</h2>
          <p>Regenerate the website archive from the repository root. Historical picks are never fabricated to fill an empty table.</p>
        </section>
      )}
    </>
  );
}

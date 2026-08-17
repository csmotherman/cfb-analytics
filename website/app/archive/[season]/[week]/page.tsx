import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ArchiveBrowser } from "../../../../components/ArchiveBrowser";
import { ArchiveGameCard } from "../../../../components/ArchiveGameCard";
import { ARCHIVE_SEASONS, getArchiveIndex, getArchiveWeek } from "../../../../lib/archive";

export async function generateMetadata({ params }: { params: Promise<{ season: string; week: string }> }): Promise<Metadata> {
  const { season: seasonRaw, week: weekRaw } = await params;
  const season = Number(seasonRaw);
  const week = Number(weekRaw);
  return {
    title: `${season} Week ${week} College Football Archive`,
    description: `Browse the ${season} college football Week ${week} model archive and historical slate.`,
  };
}

export default async function ArchiveWeekPage({ params }: { params: Promise<{ season: string; week: string }> }) {
  const { season: seasonRaw, week: weekRaw } = await params;
  const season = Number(seasonRaw);
  const week = Number(weekRaw);
  if (!ARCHIVE_SEASONS.includes(season) || !Number.isInteger(week) || week < 0 || week > 20) notFound();

  const data = getArchiveWeek(season, week);
  const index = getArchiveIndex();
  const title = week === 0 ? "Preseason" : `Week ${week}`;

  return (
    <>
      <Link className="back-link" href="/">← Current predictions</Link>

      <section className="page-hero compact-hero archive-page-hero">
        <span className="eyebrow">PREDICTION ARCHIVE</span>
        <h1>{season} · {title}</h1>
        <p>Go back through college football one week at a time. Archived model calls stay attached to the historical slate when a leakage-safe prediction exists.</p>
      </section>

      <ArchiveBrowser index={index} />

      <section className="archive-week-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">{data.label ?? `${season} ${title}`}</span>
            <h2>{data.games.length ? `${data.games.length} games` : "Archive data not generated yet"}</h2>
          </div>
        </div>

        {data.games.length ? (
          <div className="archive-game-list">
            {data.games.map((game) => <ArchiveGameCard key={game.id} game={game} />)}
          </div>
        ) : (
          <div className="empty-panel archive-empty">
            <h2>This week is ready for archive data.</h2>
            <p>The page exists now, but no historical export has been written for this season/week on this checkout. We do not fabricate old model picks to fill the screen.</p>
          </div>
        )}
      </section>
    </>
  );
}

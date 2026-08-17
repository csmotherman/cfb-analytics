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
    title: `${season} Week ${week} Model Results`,
    description: `See the actual games, model picks, and straight-up results from ${season} Week ${week}.`,
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
      <Link className="back-link" href="/archive">← All-time results</Link>

      <section className="fan-page-intro fan-archive-detail-intro">
        <div>
          <span className="fan-kicker">MODEL HISTORY</span>
          <h1>{season} Week {week}</h1>
          <p>Actual games from the week, their final scores, The Model’s supported pregame picks, and whether each call was correct.</p>
        </div>
      </section>

      <ArchiveBrowser index={index} initialSeason={season} initialWeek={week} compact />

      {data.games.length ? (
        <ArchiveWeekView data={data} />
      ) : (
        <section className="fan-empty-state archive-empty">
          <span className="fan-status fan-status-steel">No published data</span>
          <h2>This archive week is not available.</h2>
          <p>Historical games and model calls are only shown when they exist in the published archive; missing predictions are never reconstructed and presented as original calls.</p>
        </section>
      )}
    </>
  );
}

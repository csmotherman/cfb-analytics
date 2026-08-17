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
      <Link className="back-link" href="/archive">← Back to archive</Link>

      <section className="fan-page-intro fan-archive-detail-intro">
        <div>
          <span className="fan-kicker">ARCHIVE WEEK</span>
          <h1>{season} Week {week}</h1>
          <p>The Official 15 and The Model's straight-up result, preserved as the permanent record of that week.</p>
        </div>
        <div className="fan-rule-row fan-rule-row-intro">
          <span><strong>1</strong> point per winner</span>
          <span><strong>15</strong> official games</span>
        </div>
      </section>

      <ArchiveBrowser index={index} />

      {data.games.length ? (
        <ArchiveWeekView data={data} />
      ) : (
        <section className="fan-empty-state archive-empty">
          <span className="fan-status fan-status-steel">No published data</span>
          <h2>This archive week is not available on this checkout.</h2>
          <p>Historical model picks are only shown when a supported published record exists; they are never fabricated after the result.</p>
        </section>
      )}
    </>
  );
}

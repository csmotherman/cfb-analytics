"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import type { ArchiveIndexEntry } from "../lib/archive";

function preferredWeek(weeks: number[]): number {
  return weeks.includes(1) ? 1 : (weeks[0] ?? 1);
}

export function ArchiveBrowser({ index }: { index: ArchiveIndexEntry[] }) {
  const router = useRouter();
  const defaultSeason = index[0]?.season ?? 2025;
  const defaultWeeks = index.find((entry) => entry.season === defaultSeason)?.weeks ?? [];
  const [season, setSeason] = useState(defaultSeason);
  const weeks = useMemo(
    () => index.find((entry) => entry.season === season)?.weeks ?? [],
    [index, season],
  );
  const [week, setWeek] = useState(preferredWeek(defaultWeeks));

  function changeSeason(value: number) {
    setSeason(value);
    const nextWeeks = index.find((entry) => entry.season === value)?.weeks ?? [];
    setWeek(preferredWeek(nextWeeks));
  }

  return (
    <section className="archive-browser" aria-labelledby="archive-heading">
      <div className="archive-browser-copy">
        <span className="eyebrow">BEAT THE MODEL ARCHIVE</span>
        <div>
          <h2 id="archive-heading">Choose a season and week.</h2>
          <p>See the Official 15, the rankings attached to each matchup, and how The Model actually finished.</p>
        </div>
      </div>

      <div className="archive-picker">
        <label>
          <span>Season</span>
          <select value={season} onChange={(event) => changeSeason(Number(event.target.value))}>
            {index.map((entry) => <option key={entry.season} value={entry.season}>{entry.season}</option>)}
          </select>
        </label>
        <label>
          <span>Week</span>
          <select value={week} onChange={(event) => setWeek(Number(event.target.value))}>
            {weeks.map((value) => <option key={value} value={value}>Week {value}</option>)}
          </select>
        </label>
        <button type="button" onClick={() => router.push(`/archive/${season}/${week}`)}>
          View week <span aria-hidden="true">→</span>
        </button>
      </div>

      <p className="archive-browser-note">The game archive uses the same comparable-season contract as the model. 2020 remains intentionally excluded.</p>
    </section>
  );
}

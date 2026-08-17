"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import type { ArchiveIndexEntry } from "../lib/archive";

export function ArchiveBrowser({ index }: { index: ArchiveIndexEntry[] }) {
  const router = useRouter();
  const defaultSeason = index[0]?.season ?? 2025;
  const [season, setSeason] = useState(defaultSeason);
  const weeks = useMemo(
    () => index.find((entry) => entry.season === season)?.weeks ?? [],
    [index, season],
  );
  const [week, setWeek] = useState(weeks[0] ?? 1);

  function changeSeason(value: number) {
    setSeason(value);
    const nextWeeks = index.find((entry) => entry.season === value)?.weeks ?? [];
    setWeek(nextWeeks[0] ?? 1);
  }

  return (
    <section className="archive-home" aria-labelledby="archive-heading">
      <div className="archive-home-copy">
        <span className="eyebrow">PREDICTION ARCHIVE</span>
        <h2 id="archive-heading">Go back to any week.</h2>
        <p>Browse the college football slate year by year, week by week, from 2014 through 2025.</p>
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
            {weeks.map((value) => <option key={value} value={value}>{value === 0 ? "Preseason" : `Week ${value}`}</option>)}
          </select>
        </label>
        <button type="button" onClick={() => router.push(`/archive/${season}/${week}`)}>
          Open archive <span aria-hidden="true">→</span>
        </button>
      </div>
    </section>
  );
}

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
    <section className="archive-home" aria-labelledby="archive-heading">
      <div className="archive-home-copy">
        <span className="eyebrow">PREDICTION ARCHIVE</span>
        <h2 id="archive-heading">Go back to any week.</h2>
        <p>Browse the college football slate year by year, week by week, from 2014 through 2025.</p>
        <p className="archive-note">2020 is intentionally omitted because the COVID-disrupted season is not part of the comparable historical model universe.</p>
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
          Open archive <span aria-hidden="true">→</span>
        </button>
      </div>
    </section>
  );
}

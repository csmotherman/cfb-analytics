"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import type { ArchiveIndexEntry } from "../lib/archive";

function preferredWeek(weeks: number[], requested?: number): number {
  if (typeof requested === "number" && weeks.includes(requested)) return requested;
  return weeks.includes(1) ? 1 : (weeks[0] ?? 1);
}

export function ArchiveBrowser({
  index,
  initialSeason,
  initialWeek,
  compact = false,
}: {
  index: ArchiveIndexEntry[];
  initialSeason?: number;
  initialWeek?: number;
  compact?: boolean;
}) {
  const router = useRouter();
  const defaultSeason = index.some((entry) => entry.season === initialSeason)
    ? Number(initialSeason)
    : (index[0]?.season ?? 2025);
  const defaultWeeks = index.find((entry) => entry.season === defaultSeason)?.weeks ?? [];
  const [season, setSeason] = useState(defaultSeason);
  const weeks = useMemo(
    () => index.find((entry) => entry.season === season)?.weeks ?? [],
    [index, season],
  );
  const [week, setWeek] = useState(preferredWeek(defaultWeeks, initialWeek));

  useEffect(() => {
    if (typeof initialSeason !== "number") return;
    const nextSeason = index.some((entry) => entry.season === initialSeason)
      ? initialSeason
      : (index[0]?.season ?? initialSeason);
    const nextWeeks = index.find((entry) => entry.season === nextSeason)?.weeks ?? [];
    setSeason(nextSeason);
    setWeek(preferredWeek(nextWeeks, initialWeek));
  }, [index, initialSeason, initialWeek]);

  function changeSeason(value: number) {
    const nextWeeks = index.find((entry) => entry.season === value)?.weeks ?? [];
    setSeason(value);
    setWeek((current) => preferredWeek(nextWeeks, current));
  }

  function openWeek() {
    router.push(`/archive/${season}/${week}`);
  }

  return (
    <section className={`fan-archive-browser${compact ? " fan-archive-browser-compact" : ""}`} aria-labelledby="archive-picker-heading">
      {!compact ? (
        <div className="fan-archive-browser-copy">
          <span className="fan-kicker">EXPLORE THE RECEIPTS</span>
          <h2 id="archive-picker-heading">Go to any season. Go to any week.</h2>
          <p>Choose a year and week to see the actual games, final scores, The Model's supported pregame calls, and whether each pick was right or wrong.</p>
        </div>
      ) : <span className="sr-only" id="archive-picker-heading">Choose archive season and week</span>}

      <div className="fan-archive-picker">
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
        <button type="button" onClick={openWeek}>
          View results <span aria-hidden="true">→</span>
        </button>
      </div>

      {!compact ? (
        <small className="fan-archive-note">The game archive begins in 2014. 2020 is intentionally excluded from the comparable archive. Accuracy totals only count games with a supported model call and a final result.</small>
      ) : null}
    </section>
  );
}

"use client";

import { useMemo, useState } from "react";

import type { BeatTheModelGame, TeamPregameStats } from "../lib/beat-the-model";
import { TeamLogo } from "./TeamLogo";

type MetricKey = keyof TeamPregameStats;

type Metric = {
  label: string;
  key: MetricKey;
  format: "number" | "percent" | "signed";
  lowerIsBetter?: boolean;
};

const METRICS: Metric[] = [
  { label: "Points / game", key: "pointsPerGame", format: "number" },
  { label: "Points allowed", key: "pointsAllowedPerGame", format: "number", lowerIsBetter: true },
  { label: "Success rate", key: "offenseSuccessRate", format: "percent" },
  { label: "Success allowed", key: "defenseSuccessRateAllowed", format: "percent", lowerIsBetter: true },
  { label: "PPA / play", key: "offensePPA", format: "signed" },
  { label: "PPA allowed", key: "defensePPAAllowed", format: "signed", lowerIsBetter: true },
  { label: "Points / opportunity", key: "pointsPerOpportunity", format: "number" },
  { label: "Opp. points / opportunity", key: "pointsPerOpportunityAllowed", format: "number", lowerIsBetter: true },
];

function numberValue(stats: TeamPregameStats | null | undefined, key: MetricKey): number | null {
  const value = stats?.[key];
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function formatMetric(value: number | null, format: Metric["format"]): string {
  if (value == null) return "—";
  if (format === "percent") return `${(value * 100).toFixed(1)}%`;
  if (format === "signed") return `${value > 0 ? "+" : ""}${value.toFixed(2)}`;
  return value.toFixed(1);
}

function formatRecord(stats: TeamPregameStats | null | undefined): string {
  if (!stats || !stats.games) return "—";
  return stats.ties > 0
    ? `${stats.wins}-${stats.losses}-${stats.ties}`
    : `${stats.wins}-${stats.losses}`;
}

function edge(
  away: number | null,
  home: number | null,
  lowerIsBetter = false,
): { away: boolean; home: boolean } {
  if (away == null || home == null || Math.abs(away - home) < 0.0001) {
    return { away: false, home: false };
  }
  const awayBetter = lowerIsBetter ? away < home : away > home;
  return { away: awayBetter, home: !awayBetter };
}

export function TeamStatsComparison({ game }: { game: BeatTheModelGame }) {
  const [open, setOpen] = useState(false);
  const away = game.awayPregameStats;
  const home = game.homePregameStats;
  const hasStats = Boolean(away || home);

  const throughWeek = useMemo(() => {
    const values = [away?.throughWeek, home?.throughWeek].filter((value): value is number => typeof value === "number");
    return values.length ? Math.max(...values) : null;
  }, [away?.throughWeek, home?.throughWeek]);

  if (!hasStats) return null;

  return (
    <section className={`btm-team-stats${open ? " open" : ""}`} aria-label={`Pregame team stats for ${game.awayTeam} at ${game.homeTeam}`}>
      <button
        type="button"
        className="btm-stats-toggle"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
      >
        <span className="btm-stats-toggle-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M4 19V9M10 19V5M16 19v-7M22 19H2" /></svg>
        </span>
        <span className="btm-stats-toggle-copy">
          <small>MATCHUP INTEL</small>
          <strong>Compare team stats</strong>
          <em>{throughWeek != null ? `Current season · through Week ${throughWeek}` : "Pregame season snapshot"}</em>
        </span>
        <span className="btm-stats-toggle-action">{open ? "Hide" : "Compare"}<span aria-hidden="true">⌄</span></span>
      </button>

      {open ? (
        <div className="btm-stats-panel">
          <div className="btm-stats-teams">
            <div>
              <TeamLogo team={game.awayTeam} src={game.awayLogo} size="md" />
              <span>#{game.awayRank}</span>
              <strong>{game.awayTeam}</strong>
              <small>{game.awayConference ?? "Away"}</small>
            </div>
            <span className="btm-stats-vs">VS</span>
            <div>
              <TeamLogo team={game.homeTeam} src={game.homeLogo} size="md" />
              <span>#{game.homeRank}</span>
              <strong>{game.homeTeam}</strong>
              <small>{game.homeConference ?? "Home"}</small>
            </div>
          </div>

          <div className="btm-stat-table" role="table" aria-label="Team stat comparison">
            <div className="btm-stat-row overview" role="row">
              <strong role="cell">{formatRecord(away)}</strong>
              <span role="rowheader">Record</span>
              <strong role="cell">{formatRecord(home)}</strong>
            </div>

            {METRICS.map((metric) => {
              const awayValue = numberValue(away, metric.key);
              const homeValue = numberValue(home, metric.key);
              const advantage = edge(awayValue, homeValue, metric.lowerIsBetter);
              return (
                <div className="btm-stat-row" role="row" key={String(metric.key)}>
                  <strong className={advantage.away ? "edge" : ""} role="cell">{formatMetric(awayValue, metric.format)}</strong>
                  <span role="rowheader">{metric.label}</span>
                  <strong className={advantage.home ? "edge" : ""} role="cell">{formatMetric(homeValue, metric.format)}</strong>
                </div>
              );
            })}
          </div>

          <div className="btm-stats-note">
            <span>Pregame only</span>
            <p>
              Numbers use completed games before this week. Success rate measures consistent play efficiency; PPA estimates expected points added per play. Advanced rates exclude garbage time.
            </p>
          </div>
        </div>
      ) : null}
    </section>
  );
}

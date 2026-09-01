// PRESENTATION layer: pure JSX. Takes a fully-analyzed MatchupGraphicData
// and renders it -- there is deliberately no team name, statistic, edge
// score, or sentence hardcoded anywhere in this file. Every word on the
// graphic comes from `data`, `teamAbbreviation` (lib/team-colors.ts,
// keyed by teamId), or `teamLogoUrl` (lib/team-assets.ts, keyed by
// teamId) -- swap the gameId this is built from and the whole graphic
// becomes a different team's story with zero JSX changes.
//
// Fixed 1600x900 landscape canvas (a hard requirement -- see
// app/matchup-graphic/[gameId]/route.tsx). Four horizontal zones:
// header, team snapshot, two possession panels side by side, and a
// closing prediction strip.
//
// Color system: cream page, Michigan navy for essentially all text
// (Michigan's AND the opponent's -- this is a consistent MFF identity,
// not a dynamically-recolored one), maize used only as a single tiny
// accent line. No quality-based rank coloring, no per-team accent
// coloring of data. Hierarchy comes from size/weight/position, not a
// rainbow of colors -- the graphic should still make sense in
// grayscale. Team identity comes from the real logos and the words on
// the page, not from paint.
import { teamLogoUrl } from "../team-assets";
import { teamAbbreviation } from "../team-colors";
import type { MatchupGraphicData, PhaseEdgeRow, PossessionPhase } from "./types";

const CREAM = "#F5F0E6";
const CREAM_TEXT = "#F5F0E6";
const NAVY = "#00274C"; // official Michigan navy
const MAIZE = "#FFCB05"; // tiny accent only -- never text on cream
const SLATE = "#3D5166"; // darkened from the site's usual slate for legibility at small sizes on cream
const LIGHT_BLUE_GRAY = "#D7DEE4";
const LINE = "rgba(0,39,76,0.14)"; // navy at low opacity -- the one border system, used everywhere
const CHIP_BG = "rgba(0,39,76,0.055)"; // subtle navy wash shared by rank chips, edge badges, and THE READ boxes
const CHIP_BORDER = "rgba(0,39,76,0.18)";

// Uses the real team abbreviation (e.g. "WMU", "OU") rather than a
// generic "OPP" -- an edge label must always explicitly name a team.
// Every tier/direction renders in the same navy-on-light-wash style;
// only the wording changes ("MICH EDGE" vs "WMU EDGE" vs "EVEN") --
// color is not what tells the reader who has the edge.
function shortVerdict(tier: PhaseEdgeRow["tier"], direction: PhaseEdgeRow["direction"], opponentAbbr: string): string {
  if (tier === "insufficient") return "NO DATA";
  if (direction === "even") return "EVEN";
  const team = direction === "michigan" ? "MICH" : opponentAbbr;
  if (tier === "strong") return `STRONG ${team} EDGE`;
  if (tier === "moderate") return `${team} EDGE`;
  return `SLIGHT ${team} EDGE`;
}

// ---- tiny presentation-only derivation (no new analysis) ----

function fieldPositionEdgeLabel(mich: MatchupGraphicData["michigan"]["fieldPosition"], opp: MatchupGraphicData["opponent"]["fieldPosition"], michAbbr: string, oppAbbr: string): string {
  if (!mich || !opp) return "FIELD POSITION: N/A";
  const diff = mich.ownYardLine - opp.ownYardLine; // higher own-yard-line = starts further from own goal = better
  if (Math.abs(diff) < 1) return "FIELD POSITION: EVEN";
  const better = diff > 0 ? michAbbr : oppAbbr;
  return `EDGE: ${better} +${Math.abs(diff).toFixed(1)} YDS`;
}

// Average starting field position is rarely more than a few yards
// apart, which on a 250px track can put two markers only a few px
// apart -- visually indistinguishable dots even with labels above them.
// Nudges two close positions apart to a minimum visual gap around their
// shared midpoint, preserving which one leads -- the exact values are
// still shown precisely in the text readout below, this only keeps the
// schematic dots from visually merging into one.
function declutter(a: number, b: number, minGap: number): [number, number] {
  const gap = b - a;
  if (Math.abs(gap) >= minGap) return [a, b];
  const mid = (a + b) / 2;
  const half = minGap / 2;
  return gap >= 0 ? [mid - half, mid + half] : [mid + half, mid - half];
}

// ---- header (zone 1) ----

function Header({ data }: { data: MatchupGraphicData }) {
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "short", month: "short", day: "numeric", year: "numeric" });
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", backgroundColor: NAVY, padding: "7px 44px" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.michigan.teamId, 256)} width={64} height={64} alt="" />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 52, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>
          MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 19, fontWeight: 600, color: "rgba(245,240,230,0.55)", margin: "0 14px" }}>vs</span>{data.opponent.name.toUpperCase()}
        </div>
        <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: "rgba(245,240,230,0.75)", letterSpacing: 1.8, marginTop: 6 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.opponent.teamId, 256)} width={72} height={72} alt="" />
    </div>
  );
}

function RankChip({ rank }: { rank: number }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: CHIP_BG, border: `1px solid ${CHIP_BORDER}`, borderRadius: 6, padding: "3px 10px", minWidth: 42 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: NAVY }}>{`#${rank}`}</span>
    </div>
  );
}

// ---- zone 2: team snapshot ----

function TeamColumn({ name, quality, runPct, align }: { name: string; quality: MatchupGraphicData["michigan"]["quality"]; runPct: number; align: "left" | "right" }) {
  const passPct = 100 - runPct;
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, alignItems: align === "left" ? "flex-start" : "flex-end" }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: NAVY }}>{name.toUpperCase()}</span>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 8, marginTop: 2 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 44, fontWeight: 700, color: NAVY, lineHeight: 1 }}>{`#${quality.overall.rank}`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, color: SLATE, letterSpacing: 0.6 }}>OVERALL</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 14, marginTop: 5 }}>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 6 }}>
          <RankChip rank={quality.offense.rank} />
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: SLATE }}>OFF</span>
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 6 }}>
          <RankChip rank={quality.defense.rank} />
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: SLATE }}>DEF</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 8, marginTop: 6 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 24, fontWeight: 700, color: NAVY }}>{`${runPct}% RUN`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 14, fontWeight: 600, color: SLATE }}>{`${passPct}% PASS`}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", width: 270, height: 10, borderRadius: 3, overflow: "hidden", marginTop: 4 }}>
        <div style={{ display: "flex", width: `${runPct}%`, backgroundColor: NAVY }} />
        <div style={{ display: "flex", width: `${passPct}%`, backgroundColor: LIGHT_BLUE_GRAY }} />
      </div>
    </div>
  );
}

// Both markers are the same navy dot -- the two teams are told apart by
// the abbreviation label, not by color, so the label (not the dot) is
// what needs collision handling. `lift` raises the label further above
// the track when the two yard lines land close together (the common
// case -- average starting field position is rarely more than a few
// yards apart), which at this panel's ~250px track width happens often
// enough that it can't be treated as an edge case.
function FieldPositionMarker({ abbr, leftPct, lift }: { abbr: string; leftPct: number; lift: boolean }) {
  const topOffset = lift ? -34 : -16;
  const dotTop = -4.5 - topOffset; // nested-absolute offset that compensates for topOffset, so the dot stays at a fixed height on the track regardless of whether the label is lifted
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", position: "absolute", left: `${leftPct}%`, top: topOffset, marginLeft: -16, width: 32 }}>
      <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, color: NAVY, letterSpacing: 0.4 }}>{abbr}</span>
      <div style={{ display: "flex", position: "absolute", left: "50%", top: dotTop, width: 9, height: 9, borderRadius: 5, backgroundColor: NAVY, marginLeft: -4.5, border: `2px solid ${CREAM}` }} />
    </div>
  );
}

function FieldPositionMini({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  const pct = (yardLine: number) => Math.max(6, Math.min(94, (yardLine / 50) * 100));
  const rawMichPct = mich ? pct(mich.ownYardLine) : null;
  const rawOppPct = opp ? pct(opp.ownYardLine) : null;
  const [michPct, oppPct] = rawMichPct != null && rawOppPct != null ? declutter(rawMichPct, rawOppPct, 9) : [rawMichPct, rawOppPct];
  const closeMarkers = michPct != null && oppPct != null && Math.abs(michPct - oppPct) < 14;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 300 }}>
      <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1.2, color: SLATE }}>FIELD POSITION</span>
      <div style={{ display: "flex", position: "relative", width: 250, height: 4, backgroundColor: LIGHT_BLUE_GRAY, marginTop: 39, borderRadius: 2 }}>
        {mich && michPct != null && <FieldPositionMarker abbr={michAbbr} leftPct={michPct} lift={false} />}
        {opp && oppPct != null && <FieldPositionMarker abbr={oppAbbr} leftPct={oppPct} lift={closeMarkers} />}
      </div>
      <div style={{ display: "flex", flexDirection: "row", gap: 22, marginTop: 15 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: NAVY }}>{`${michAbbr} ${mich ? `OWN ${mich.ownYardLine.toFixed(1)}` : "—"}`}</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: NAVY }}>{`${oppAbbr} ${opp ? `OWN ${opp.ownYardLine.toFixed(1)}` : "—"}`}</span>
      </div>
      <div style={{ display: "flex", marginTop: 9, backgroundColor: NAVY, borderRadius: 4, padding: "4px 14px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 14, fontWeight: 700, color: CREAM_TEXT, letterSpacing: 0.3 }}>{fieldPositionEdgeLabel(mich, opp, michAbbr, oppAbbr)}</span>
      </div>
    </div>
  );
}

function TeamSnapshotZone({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between", gap: 20 }}>
      <TeamColumn name={data.michigan.name} quality={data.michigan.quality} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} align="left" />
      <FieldPositionMini data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />
      <TeamColumn name={data.opponent.name} quality={data.opponent.quality} runPct={Math.round(data.opponent.tendencies.rushDecisionRate * 100)} align="right" />
    </div>
  );
}

// ---- zone 3: possession panels ----
//
// Inside each panel, offense always renders left and defense always
// renders right (row.offense / row.defense, never a "michigan"/
// "opponent" pair) -- that's what makes the two panels' internal layout
// identical while the teams occupying each side flip between them. The
// scale marker's MICH-left/OPP-right orientation is a separate, fixed
// convention (row.score is always Michigan-centric) shown once per
// panel instead of relabeling every row. Every row uses the same navy
// marker regardless of which team the row favors -- position says who,
// the label spells it out, color stays constant.

function PhaseRow({ row, opponentAbbr }: { row: PhaseEdgeRow; opponentAbbr: string }) {
  const hasData = row.tier !== "insufficient";
  const markerPct = 50 - (row.score ?? 0) / 2;
  return (
    <div style={{ display: "flex", flexDirection: "column", padding: "3px 0", borderTop: `1px solid ${LINE}` }}>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", justifyContent: "space-between" }}>
        <span style={{ fontFamily: "Inter", fontSize: 19, fontWeight: 700, color: NAVY, letterSpacing: 0.3 }}>{row.label}</span>
        <div style={{ display: "flex", backgroundColor: CHIP_BG, border: `1px solid ${CHIP_BORDER}`, borderRadius: 3, padding: "2px 9px" }}>
          <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 800, letterSpacing: 0.3, color: NAVY }}>{hasData ? shortVerdict(row.tier, row.direction, opponentAbbr) : "NO DATA"}</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", marginTop: 4, gap: 10 }}>
        <RankChip rank={row.offense.rank} />
        <div style={{ display: "flex", flex: 1, position: "relative", height: 4, backgroundColor: LIGHT_BLUE_GRAY, borderRadius: 2 }}>
          <div style={{ display: "flex", position: "absolute", left: "50%", top: -4, width: 1, height: 12, backgroundColor: SLATE }} />
          {hasData && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -5, width: 14, height: 14, borderRadius: 7, backgroundColor: NAVY, marginLeft: -7, border: `2px solid ${CREAM}` }} />}
        </div>
        <RankChip rank={row.defense.rank} />
      </div>
    </div>
  );
}

function PhasePanel({ phase, title, subtitle, opponentAbbr }: { phase: PossessionPhase; title: string; subtitle: string; opponentAbbr: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 28, fontWeight: 700, color: NAVY, lineHeight: 1 }}>{title}</span>
      <div style={{ display: "flex", width: 78, height: 3, backgroundColor: NAVY, marginTop: 4, borderRadius: 2 }} />
      <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: SLATE, marginTop: 3 }}>{subtitle}</span>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "center", gap: 18, marginTop: 6 }}>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.6, color: SLATE }}>MICH ADVANTAGE</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.6, color: SLATE }}>EVEN</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.6, color: SLATE }}>{`${opponentAbbr} ADVANTAGE`}</span>
      </div>
      {phase.rows.map((row) => <PhaseRow key={row.id} row={row} opponentAbbr={opponentAbbr} />)}
      <div style={{ display: "flex", flexDirection: "column", marginTop: 5, padding: "6px 14px", borderRadius: 6, backgroundColor: CHIP_BG }}>
        <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 800, letterSpacing: 1, color: NAVY }}>THE READ</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 18, fontWeight: 700, color: NAVY, marginTop: 2, lineHeight: 1.15 }}>{phase.whatItMeans}</span>
      </div>
    </div>
  );
}

// ---- zone 4: prediction ----

function PredictionOutlookZone({ data }: { data: MatchupGraphicData }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", backgroundColor: NAVY, padding: "11px 44px 9px" }}>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center" }}>
        {data.prediction.type === "model" && (
          <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 56 }}>
            {data.prediction.winProbabilityPct != null && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <span style={{ fontFamily: "Barlow Condensed", fontSize: 32, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{`${data.prediction.winProbabilityPct}%`}</span>
                <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.8, color: "rgba(245,240,230,0.6)", marginTop: 2 }}>WIN PROBABILITY</span>
              </div>
            )}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 44, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{data.prediction.marginLabel}</span>
              <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.8, color: "rgba(245,240,230,0.6)", marginTop: 2 }}>MFF PROJECTION</span>
            </div>
            {data.prediction.marketNote && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{data.prediction.marketNote.replace("Market: ", "")}</span>
                <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.8, color: "rgba(245,240,230,0.6)", marginTop: 2 }}>MARKET</span>
              </div>
            )}
          </div>
        )}
        {data.prediction.type === "market" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 44, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{data.prediction.spreadLabel}</span>
            <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 0.8, color: "rgba(245,240,230,0.75)", marginTop: 4 }}>{`MARKET EXPECTATION · ${data.prediction.book}`}</span>
          </div>
        )}
        {data.prediction.type === "unavailable" && (
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: "rgba(245,240,230,0.55)" }}>PREDICTION NOT AVAILABLE</span>
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", width: "100%", marginTop: 8, paddingTop: 7, borderTop: "1px solid rgba(245,240,230,0.16)" }}>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 9 }}>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.8, color: "rgba(245,240,230,0.6)" }}>THE BOTTOM LINE</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 18, fontWeight: 700, color: CREAM_TEXT }}>{data.bottomLine}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 10 }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="https://michiganfootballfocus.com/brand/michigan-football-focus.png" width={62} height={20} alt="" />
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, color: CREAM_TEXT }}>MICHIGANFOOTBALLFOCUS.COM</span>
        </div>
      </div>
    </div>
  );
}

// ---- root ----

export function MatchupGraphic({ data }: { data: MatchupGraphicData }) {
  const oppAbbr = teamAbbreviation(data.opponent.teamId, data.opponent.name);
  const michAbbr = "MICH";

  return (
    <div style={{ display: "flex", flexDirection: "column", width: 1600, backgroundColor: CREAM, fontFamily: "Inter", border: `1px solid ${LINE}` }}>
      {/* Maize appears exactly once on the whole graphic -- a 3px seal line, never as text. */}
      <div style={{ display: "flex", width: "100%", height: 3, backgroundColor: MAIZE }} />

      <Header data={data} />

      <div style={{ display: "flex", flexDirection: "column", padding: "9px 44px 0" }}>
        <TeamSnapshotZone data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "10px 0" }} />

        <div style={{ display: "flex", flexDirection: "row", gap: 26 }}>
          <PhasePanel
            phase={data.whenMichiganHasBall}
            title="WHEN MICHIGAN HAS THE BALL"
            subtitle={`MICH OFFENSE vs ${oppAbbr} DEFENSE`}
            opponentAbbr={oppAbbr}
          />
          <PhasePanel
            phase={data.whenOpponentHasBall}
            title={`WHEN ${data.opponent.name.toUpperCase()} HAS THE BALL`}
            subtitle={`${oppAbbr} OFFENSE vs MICH DEFENSE`}
            opponentAbbr={oppAbbr}
          />
        </div>
      </div>

      <PredictionOutlookZone data={data} />
    </div>
  );
}

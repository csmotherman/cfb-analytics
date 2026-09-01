// PRESENTATION layer: pure JSX. Takes a fully-analyzed MatchupGraphicData
// and renders it -- there is deliberately no team name, statistic, edge
// score, or sentence hardcoded anywhere in this file. Every word on the
// graphic comes from `data`, `teamColors`/`accentColorOnLight`/
// `teamAbbreviation` (lib/team-colors.ts, keyed by teamId), or
// `teamLogoUrl` (lib/team-assets.ts, keyed by teamId) -- swap the gameId
// this is built from and the whole graphic becomes a different team's
// story with zero JSX changes.
//
// Fixed 1600x900 landscape canvas (a hard requirement, not a target --
// see app/matchup-graphic/[gameId]/route.tsx). Four horizontal zones:
// header, team snapshot (quality + play-calling + field position side by
// side), two possession panels side by side, and a closing prediction
// strip. Cream page background, dark navy used only as an accent.
import { teamLogoUrl } from "../team-assets";
import { accentColorOnLight, teamAbbreviation, teamColors } from "../team-colors";
import type { EdgeDirection, EdgeTier, MatchupGraphicData, PhaseEdgeRow, PossessionPhase } from "./types";

const CREAM = "#F5F0E6";
const CREAM_TEXT = "#F5F0E6";
const NAVY = "#0B1F33";
const MAIZE = "#FFCB05";
const SLATE = "#6E7781";
const LINE = "rgba(11,31,51,0.14)";
const PASS_BAR = "#9AA9B8";

function hexToRgba(hex: string, alpha: number): string {
  const clean = hex.replace("#", "");
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

// National-rank quality color -- a fixed, team-agnostic scale (top 25 =
// green ... 101+ = red), unrelated to the maize/opponent-accent edge
// colors below. This encodes "how good is this rank" in absolute terms;
// the edge colors encode "which team" -- two different questions, so two
// separate, non-overlapping color systems.
function rankChipColors(rank: number): { bg: string; text: string } {
  if (rank <= 25) return { bg: "rgba(22,101,52,0.14)", text: "#1a6b3c" };
  if (rank <= 50) return { bg: "rgba(15,118,110,0.14)", text: "#0f6d64" };
  if (rank <= 75) return { bg: "rgba(110,119,129,0.17)", text: "#5b636c" };
  if (rank <= 100) return { bg: "rgba(194,120,3,0.15)", text: "#9c5c04" };
  return { bg: "rgba(153,27,27,0.14)", text: "#96201f" };
}

function verdictColors(direction: EdgeDirection, opponentAccent: string): { bg: string; text: string; dot: string } {
  if (direction === "michigan") return { bg: "rgba(255,203,5,0.24)", text: NAVY, dot: MAIZE };
  if (direction === "opponent") return { bg: hexToRgba(opponentAccent, 0.16), text: NAVY, dot: opponentAccent };
  return { bg: "rgba(110,119,129,0.14)", text: SLATE, dot: SLATE };
}

// Uses the real team abbreviation (e.g. "WMU", "OU") rather than a
// generic "OPP" -- an edge label must always explicitly name a team.
function shortVerdict(tier: EdgeTier, direction: EdgeDirection, opponentAbbr: string): string {
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

// ---- header (zone 1) ----

function Header({ data }: { data: MatchupGraphicData }) {
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "short", month: "short", day: "numeric", year: "numeric" });
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", backgroundColor: NAVY, padding: "9px 44px" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.michigan.teamId, 256)} width={64} height={64} alt="" />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 52, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>
          MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 19, fontWeight: 600, color: "rgba(245,240,230,0.55)", margin: "0 14px" }}>vs</span>{data.opponent.name.toUpperCase()}
        </div>
        <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: MAIZE, letterSpacing: 1.8, marginTop: 6 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.opponent.teamId, 256)} width={72} height={72} alt="" />
    </div>
  );
}

function RankChip({ rank }: { rank: number }) {
  const { bg, text } = rankChipColors(rank);
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: bg, borderRadius: 6, padding: "3px 10px", minWidth: 42 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: text }}>{`#${rank}`}</span>
    </div>
  );
}

// ---- zone 2: team snapshot ----

function TeamColumn({ name, quality, runPct, nameColor, barColor, align }: { name: string; quality: MatchupGraphicData["michigan"]["quality"]; runPct: number; nameColor: string; barColor: string; align: "left" | "right" }) {
  const overallColor = rankChipColors(quality.overall.rank).text;
  const passPct = 100 - runPct;
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, alignItems: align === "left" ? "flex-start" : "flex-end" }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: nameColor }}>{name.toUpperCase()}</span>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 8, marginTop: 2 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 44, fontWeight: 700, color: overallColor, lineHeight: 1 }}>{`#${quality.overall.rank}`}</span>
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
        <div style={{ display: "flex", width: `${runPct}%`, backgroundColor: barColor }} />
        <div style={{ display: "flex", width: `${passPct}%`, backgroundColor: PASS_BAR }} />
      </div>
    </div>
  );
}

// Dots only, no per-marker text label -- at this panel's width (~340px)
// two close yard lines put the dots only a few px apart, and any label
// text there would collide. Color alone (maize vs opponent accent)
// distinguishes them; the readout line below spells out which is which.
function FieldPositionMini({ data, michAbbr, oppAbbr, opponentAccent }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string; opponentAccent: string }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  const pct = (yardLine: number) => Math.max(6, Math.min(94, (yardLine / 50) * 100));
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 300 }}>
      <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1.2, color: SLATE }}>FIELD POSITION</span>
      <div style={{ display: "flex", position: "relative", width: 250, height: 4, backgroundColor: LINE, marginTop: 16, borderRadius: 2 }}>
        {mich && (
          <div style={{ display: "flex", position: "absolute", left: `${pct(mich.ownYardLine)}%`, top: -6, width: 15, height: 15, borderRadius: 8, backgroundColor: NAVY, alignItems: "center", justifyContent: "center", marginLeft: -7.5 }}>
            <div style={{ display: "flex", width: 8, height: 8, borderRadius: 4, backgroundColor: MAIZE }} />
          </div>
        )}
        {opp && (
          <div style={{ display: "flex", position: "absolute", left: `${pct(opp.ownYardLine)}%`, top: -6, width: 15, height: 15, borderRadius: 8, backgroundColor: NAVY, alignItems: "center", justifyContent: "center", marginLeft: -7.5 }}>
            <div style={{ display: "flex", width: 8, height: 8, borderRadius: 4, backgroundColor: opponentAccent }} />
          </div>
        )}
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

function TeamSnapshotZone({ data, opponentAccent, michAbbr, oppAbbr }: { data: MatchupGraphicData; opponentAccent: string; michAbbr: string; oppAbbr: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between", gap: 20 }}>
      <TeamColumn name={data.michigan.name} quality={data.michigan.quality} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} nameColor={NAVY} barColor={MAIZE} align="left" />
      <FieldPositionMini data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} opponentAccent={opponentAccent} />
      <TeamColumn name={data.opponent.name} quality={data.opponent.quality} runPct={Math.round(data.opponent.tendencies.rushDecisionRate * 100)} nameColor={opponentAccent} barColor={opponentAccent} align="right" />
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
// panel instead of relabeling every row.

function PhaseRow({ row, opponentAccent, opponentAbbr }: { row: PhaseEdgeRow; opponentAccent: string; opponentAbbr: string }) {
  const vcolors = verdictColors(row.direction, opponentAccent);
  const hasData = row.tier !== "insufficient";
  const markerPct = 50 - (row.score ?? 0) / 2;
  return (
    <div style={{ display: "flex", flexDirection: "column", padding: "4px 0", borderTop: `1px solid ${LINE}` }}>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", justifyContent: "space-between" }}>
        <span style={{ fontFamily: "Inter", fontSize: 19, fontWeight: 700, color: NAVY, letterSpacing: 0.3 }}>{row.label}</span>
        <div style={{ display: "flex", backgroundColor: vcolors.bg, borderRadius: 3, padding: "2px 9px" }}>
          <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 800, letterSpacing: 0.3, color: vcolors.text }}>{hasData ? shortVerdict(row.tier, row.direction, opponentAbbr) : "NO DATA"}</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", marginTop: 4, gap: 10 }}>
        <RankChip rank={row.offense.rank} />
        <div style={{ display: "flex", flex: 1, position: "relative", height: 4, backgroundColor: "rgba(11,31,51,0.13)", borderRadius: 2 }}>
          <div style={{ display: "flex", position: "absolute", left: "50%", top: -4, width: 1, height: 12, backgroundColor: LINE }} />
          {hasData && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -5, width: 14, height: 14, borderRadius: 7, backgroundColor: vcolors.dot, marginLeft: -7, border: `2px solid ${CREAM}` }} />}
        </div>
        <RankChip rank={row.defense.rank} />
      </div>
    </div>
  );
}

function PhasePanel({ phase, title, subtitle, headingColor, opponentAccent, opponentAbbr }: { phase: PossessionPhase; title: string; subtitle: string; headingColor: string; opponentAccent: string; opponentAbbr: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 28, fontWeight: 700, color: NAVY, lineHeight: 1 }}>{title}</span>
      <div style={{ display: "flex", width: 78, height: 4, backgroundColor: headingColor, marginTop: 4, borderRadius: 2 }} />
      <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: SLATE, marginTop: 3 }}>{subtitle}</span>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "center", gap: 18, marginTop: 6 }}>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.6, color: MAIZE }}>MICH ADVANTAGE</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.6, color: SLATE }}>EVEN</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.6, color: opponentAccent }}>{`${opponentAbbr} ADVANTAGE`}</span>
      </div>
      {phase.rows.map((row) => <PhaseRow key={row.id} row={row} opponentAccent={opponentAccent} opponentAbbr={opponentAbbr} />)}
      <div style={{ display: "flex", flexDirection: "column", marginTop: 5, padding: "6px 14px", borderRadius: 6, backgroundColor: hexToRgba(headingColor, 0.1) }}>
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
                <span style={{ fontFamily: "Barlow Condensed", fontSize: 32, fontWeight: 700, color: MAIZE, lineHeight: 1 }}>{`${data.prediction.winProbabilityPct}%`}</span>
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
            <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 0.8, color: MAIZE, marginTop: 4 }}>{`MARKET EXPECTATION · ${data.prediction.book}`}</span>
          </div>
        )}
        {data.prediction.type === "unavailable" && (
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: "rgba(245,240,230,0.55)" }}>PREDICTION NOT AVAILABLE</span>
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", width: "100%", marginTop: 8, paddingTop: 7, borderTop: "1px solid rgba(245,240,230,0.16)" }}>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 9 }}>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 0.8, color: MAIZE }}>THE BOTTOM LINE</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 18, fontWeight: 700, color: CREAM_TEXT }}>{data.bottomLine}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 10 }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="https://michiganfootballfocus.com/brand/michigan-football-focus.png" width={62} height={20} alt="" />
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, color: MAIZE }}>MICHIGANFOOTBALLFOCUS.COM</span>
        </div>
      </div>
    </div>
  );
}

// ---- root ----

export function MatchupGraphic({ data }: { data: MatchupGraphicData }) {
  const opponentColors = teamColors(data.opponent.teamId);
  const opponentAccent = accentColorOnLight(opponentColors);
  const oppAbbr = teamAbbreviation(data.opponent.teamId, data.opponent.name);
  const michAbbr = "MICH";

  return (
    <div style={{ display: "flex", flexDirection: "column", width: 1600, backgroundColor: CREAM, fontFamily: "Inter", border: `1px solid ${LINE}` }}>
      <Header data={data} />

      <div style={{ display: "flex", flexDirection: "column", padding: "11px 44px 0" }}>
        <TeamSnapshotZone data={data} opponentAccent={opponentAccent} michAbbr={michAbbr} oppAbbr={oppAbbr} />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "10px 0" }} />

        <div style={{ display: "flex", flexDirection: "row", gap: 26 }}>
          <PhasePanel
            phase={data.whenMichiganHasBall}
            title="WHEN MICHIGAN HAS THE BALL"
            subtitle={`MICH OFFENSE vs ${oppAbbr} DEFENSE`}
            headingColor={MAIZE}
            opponentAccent={opponentAccent}
            opponentAbbr={oppAbbr}
          />
          <PhasePanel
            phase={data.whenOpponentHasBall}
            title={`WHEN ${data.opponent.name.toUpperCase()} HAS THE BALL`}
            subtitle={`${oppAbbr} OFFENSE vs MICH DEFENSE`}
            headingColor={opponentAccent}
            opponentAccent={opponentAccent}
            opponentAbbr={oppAbbr}
          />
        </div>
      </div>

      <PredictionOutlookZone data={data} />
    </div>
  );
}

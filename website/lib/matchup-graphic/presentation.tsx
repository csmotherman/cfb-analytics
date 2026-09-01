// PRESENTATION layer: pure JSX. Takes a fully-analyzed MatchupGraphicData
// and renders it -- there is deliberately no team name, statistic, edge
// score, or sentence hardcoded anywhere in this file. Every word on the
// graphic comes from `data`, `teamColors`/`accentColorOnLight`
// (lib/team-colors.ts, keyed by teamId), or `teamLogoUrl`
// (lib/team-assets.ts, keyed by teamId) -- swap the gameId this is built
// from and the whole graphic becomes a different team's story with zero
// JSX changes.
//
// Visual direction: a compact, premium weekly-matchup card, not a long
// analytics report. Cream page background, dark navy used only as an
// accent -- header, section labels, dividers, the prediction strip, the
// footer -- everything else stays on cream so the numbers stay legible.
import { teamLogoUrl } from "../team-assets";
import { accentColorOnLight, teamColors } from "../team-colors";
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

function shortVerdict(tier: EdgeTier, direction: EdgeDirection): string {
  if (tier === "insufficient") return "NO DATA";
  if (direction === "even") return "EVEN";
  const team = direction === "michigan" ? "MICH" : "OPP";
  if (tier === "strong") return `STRONG ${team} EDGE`;
  if (tier === "moderate") return `${team} EDGE`;
  return `SLIGHT ${team} EDGE`;
}

// ---- tiny presentation-only derivation (no new analysis) ----

function fieldPositionEdge(mich: MatchupGraphicData["michigan"]["fieldPosition"], opp: MatchupGraphicData["opponent"]["fieldPosition"], michiganName: string, opponentName: string): string {
  if (!mich || !opp) return "FIELD POSITION: DATA UNAVAILABLE";
  const diff = mich.ownYardLine - opp.ownYardLine; // higher own-yard-line = starts further from own goal = better
  if (Math.abs(diff) < 1) return "FIELD POSITION: EVEN";
  const better = diff > 0 ? michiganName : opponentName;
  return `EDGE: ${better.toUpperCase()} +${Math.abs(diff).toFixed(1)} YDS`;
}

// ---- header ----

function Header({ data }: { data: MatchupGraphicData }) {
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "long", month: "long", day: "numeric", year: "numeric" });
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", backgroundColor: NAVY, padding: "17px 56px" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.michigan.teamId, 256)} width={92} height={92} alt="" />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 50, fontWeight: 700, color: CREAM_TEXT }}>
          MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 20, fontWeight: 600, color: "rgba(245,240,230,0.55)", margin: "0 16px" }}>vs</span>{data.opponent.name.toUpperCase()}
        </div>
        <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: MAIZE, letterSpacing: 2.2, marginTop: 7 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.opponent.teamId, 256)} width={102} height={102} alt="" />
    </div>
  );
}

function SectionLabel({ children }: { children: string }) {
  return (
    <div style={{ display: "flex", alignSelf: "flex-start", backgroundColor: NAVY, borderRadius: 3, padding: "6px 14px", marginBottom: 14 }}>
      <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 1.8, color: CREAM_TEXT }}>{children}</span>
    </div>
  );
}

function RankChip({ rank }: { rank: number }) {
  const { bg, text } = rankChipColors(rank);
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: bg, borderRadius: 6, padding: "4px 11px", minWidth: 44 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: text }}>{`#${rank}`}</span>
    </div>
  );
}

// ---- team comparison (quality + play-calling combined) ----

function TeamColumn({ name, quality, runPct, nameColor, barColor, align }: { name: string; quality: MatchupGraphicData["michigan"]["quality"]; runPct: number; nameColor: string; barColor: string; align: "left" | "right" }) {
  const overallColor = rankChipColors(quality.overall.rank).text;
  const passPct = 100 - runPct;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: align === "left" ? "flex-start" : "flex-end" }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: nameColor }}>{name.toUpperCase()}</span>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 8, marginTop: 2 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 46, fontWeight: 700, color: overallColor, lineHeight: 1 }}>{`#${quality.overall.rank}`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, color: SLATE, letterSpacing: 0.8 }}>OVERALL</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 16, marginTop: 8 }}>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 6 }}>
          <RankChip rank={quality.offense.rank} />
          <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, color: SLATE }}>OFF</span>
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 6 }}>
          <RankChip rank={quality.defense.rank} />
          <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, color: SLATE }}>DEF</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 8, marginTop: 11 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: NAVY }}>{`${runPct}% RUN`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: SLATE }}>{`${passPct}% PASS`}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", width: 300, height: 10, borderRadius: 3, overflow: "hidden", marginTop: 6 }}>
        <div style={{ display: "flex", width: `${runPct}%`, backgroundColor: barColor }} />
        <div style={{ display: "flex", width: `${passPct}%`, backgroundColor: PASS_BAR }} />
      </div>
    </div>
  );
}

// Dot sits right on the track; the abbreviation renders below it. `drop`
// pushes a marker's whole label further down when the two markers land
// close together on the yard line, which happens often -- average
// starting field position is rarely more than a few yards apart -- so
// two close markers stack instead of overlapping, regardless of how
// close the actual yard lines are.
function FieldPositionMarker({ abbr, color, leftPct, drop }: { abbr: string; color: string; leftPct: number; drop: boolean }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", position: "absolute", left: `${leftPct}%`, top: drop ? 24 : 6, marginLeft: -16, width: 32 }}>
      <div style={{ display: "flex", width: 13, height: 13, borderRadius: 7, backgroundColor: NAVY, alignItems: "center", justifyContent: "center" }}>
        <div style={{ display: "flex", width: 7, height: 7, borderRadius: 4, backgroundColor: color }} />
      </div>
      <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 800, color, letterSpacing: 0.4, marginTop: 3 }}>{abbr}</span>
    </div>
  );
}

function FieldPositionStrip({ data, opponentAccent }: { data: MatchupGraphicData; opponentAccent: string }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  const pct = (yardLine: number) => Math.max(4, Math.min(96, (yardLine / 50) * 100));
  const michPct = mich ? pct(mich.ownYardLine) : null;
  const oppPct = opp ? pct(opp.ownYardLine) : null;
  const closeMarkers = michPct != null && oppPct != null && Math.abs(michPct - oppPct) < 8;
  return (
    <div style={{ display: "flex", flexDirection: "column", marginTop: 18, paddingTop: 14, borderTop: `1px solid ${LINE}` }}>
      <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 1.4, color: SLATE, alignSelf: "center" }}>AVERAGE STARTING FIELD POSITION</span>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", padding: "0 1px", marginTop: 14 }}>
        {["OWN 20", "OWN 30", "OWN 40", "50"].map((t) => (
          <span key={t} style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, color: SLATE }}>{t}</span>
        ))}
      </div>
      <div style={{ display: "flex", position: "relative", width: "100%", height: 3, backgroundColor: LINE, marginTop: 8, marginBottom: 58 }}>
        {mich && michPct != null && <FieldPositionMarker abbr="MICH" color={MAIZE} leftPct={michPct} drop={false} />}
        {opp && oppPct != null && <FieldPositionMarker abbr="OPP" color={opponentAccent} leftPct={oppPct} drop={closeMarkers} />}
      </div>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: NAVY }}>{`${data.michigan.name.toUpperCase()}: ${mich ? `OWN ${mich.ownYardLine.toFixed(1)}` : "—"}`}</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: NAVY }}>{`${data.opponent.name.toUpperCase()}: ${opp ? `OWN ${opp.ownYardLine.toFixed(1)}` : "—"}`}</span>
      </div>
      <div style={{ display: "flex", alignSelf: "center", marginTop: 12, backgroundColor: NAVY, borderRadius: 4, padding: "6px 16px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 14, fontWeight: 700, color: CREAM_TEXT, letterSpacing: 0.4 }}>{fieldPositionEdge(mich, opp, data.michigan.name, data.opponent.name)}</span>
      </div>
    </div>
  );
}

function TeamComparisonBlock({ data, opponentAccent }: { data: MatchupGraphicData; opponentAccent: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <SectionLabel>TEAM COMPARISON</SectionLabel>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between" }}>
        <TeamColumn name={data.michigan.name} quality={data.michigan.quality} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} nameColor={NAVY} barColor={MAIZE} align="left" />
        <TeamColumn name={data.opponent.name} quality={data.opponent.quality} runPct={Math.round(data.opponent.tendencies.rushDecisionRate * 100)} nameColor={opponentAccent} barColor={opponentAccent} align="right" />
      </div>
      <FieldPositionStrip data={data} opponentAccent={opponentAccent} />
    </div>
  );
}

// ---- possession phase (main centerpiece) ----

function PhaseRow({ row, opponentAccent }: { row: PhaseEdgeRow; opponentAccent: string }) {
  const vcolors = verdictColors(row.direction, opponentAccent);
  const hasData = row.tier !== "insufficient";
  const markerPct = 50 - (row.score ?? 0) / 2;
  return (
    <div style={{ display: "flex", flexDirection: "column", padding: "7px 2px", borderTop: `1px solid ${LINE}` }}>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 9, width: 150 }}>
          <RankChip rank={row.offense.rank} />
          {hasData && <span style={{ fontFamily: "Inter", fontSize: 12.5, fontWeight: 600, color: SLATE }}>{`${(row.offense.value * 100).toFixed(1)}%`}</span>}
        </div>
        <span style={{ display: "flex", flex: 1, justifyContent: "center", fontFamily: "Inter", fontSize: 16, fontWeight: 700, color: NAVY, letterSpacing: 0.6, textAlign: "center" }}>{row.label}</span>
        <div style={{ display: "flex", flexDirection: "row-reverse", alignItems: "baseline", gap: 9, width: 150 }}>
          <RankChip rank={row.defense.rank} />
          {hasData && <span style={{ fontFamily: "Inter", fontSize: 12.5, fontWeight: 600, color: SLATE }}>{`${(row.defense.value * 100).toFixed(1)}%`}</span>}
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 14, marginTop: 5 }}>
        <div style={{ display: "flex", position: "relative", width: 130, height: 5, borderRadius: 2.5, backgroundColor: "rgba(11,31,51,0.13)" }}>
          {hasData && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -3.5, width: 12, height: 12, borderRadius: 6, backgroundColor: vcolors.dot, marginLeft: -6, border: `2px solid ${CREAM}` }} />}
        </div>
        <div style={{ display: "flex", backgroundColor: vcolors.bg, borderRadius: 3, padding: "4px 11px" }}>
          <span style={{ fontFamily: "Inter", fontSize: 14, fontWeight: 800, letterSpacing: 0.5, color: vcolors.text }}>{shortVerdict(row.tier, row.direction)}</span>
        </div>
      </div>
    </div>
  );
}

function PhaseSection({ phase, title, headingColor, opponentAccent, offenseLabel, defenseLabel }: { phase: PossessionPhase; title: string; headingColor: string; opponentAccent: string; offenseLabel: string; defenseLabel: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 32, fontWeight: 700, color: NAVY }}>{title}</span>
        <div style={{ display: "flex", width: 90, height: 4, backgroundColor: headingColor, marginTop: 5, borderRadius: 2 }} />
      </div>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", marginTop: 13, padding: "0 2px" }}>
        <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1, color: SLATE }}>{offenseLabel}</span>
        <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1, color: SLATE }}>{defenseLabel}</span>
      </div>
      {phase.rows.map((row) => <PhaseRow key={row.id} row={row} opponentAccent={opponentAccent} />)}
      <div style={{ display: "flex", flexDirection: "column", marginTop: 10, padding: "11px 16px", borderRadius: 6, backgroundColor: hexToRgba(headingColor, 0.1) }}>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 1.4, color: NAVY }}>THE READ</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, color: NAVY, marginTop: 3, lineHeight: 1.2 }}>{phase.whatItMeans}</span>
      </div>
    </div>
  );
}

// ---- prediction ----

function PredictionOutlook({ data }: { data: MatchupGraphicData }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", backgroundColor: NAVY, borderRadius: 6, padding: "18px 40px", alignItems: "center" }}>
      <span style={{ fontFamily: "Inter", fontSize: 14, fontWeight: 800, letterSpacing: 2.6, color: "rgba(245,240,230,0.62)" }}>MFF MATCHUP OUTLOOK</span>

      {data.prediction.type === "model" && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 52, fontWeight: 700, color: CREAM_TEXT, marginTop: 5, lineHeight: 1 }}>{data.prediction.marginLabel}</span>
          <div style={{ display: "flex", flexDirection: "row", gap: 28, marginTop: 8 }}>
            {data.prediction.winProbabilityPct != null && (
              <span style={{ fontFamily: "Inter", fontSize: 16, fontWeight: 700, color: MAIZE }}>{`${data.prediction.winProbabilityPct}% WIN PROBABILITY`}</span>
            )}
            {data.prediction.marketNote && (
              <span style={{ fontFamily: "Inter", fontSize: 16, fontWeight: 600, color: "rgba(245,240,230,0.72)" }}>{data.prediction.marketNote}</span>
            )}
          </div>
        </div>
      )}

      {data.prediction.type === "market" && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 1.8, color: MAIZE, marginTop: 8 }}>MARKET EXPECTATION</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 52, fontWeight: 700, color: CREAM_TEXT, marginTop: 6, lineHeight: 1 }}>{data.prediction.spreadLabel}</span>
          <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 600, color: "rgba(245,240,230,0.72)", marginTop: 7 }}>{data.prediction.book}</span>
        </div>
      )}

      {data.prediction.type === "unavailable" && (
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 36, fontWeight: 700, color: "rgba(245,240,230,0.55)", marginTop: 14 }}>PREDICTION NOT AVAILABLE</span>
      )}

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%", marginTop: 13, paddingTop: 12, borderTop: "1px solid rgba(245,240,230,0.16)" }}>
        <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 800, letterSpacing: 1.4, color: MAIZE }}>THE BOTTOM LINE</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: CREAM_TEXT, marginTop: 5, textAlign: "center", lineHeight: 1.25 }}>{data.bottomLine}</span>
      </div>
    </div>
  );
}

function Footer() {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "14px 0 20px", marginTop: 4 }}>
      <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: SLATE }}>2025 opponent-adjusted metrics · FBS ranks · MFF model · Market line labeled separately</span>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 12 }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="https://michiganfootballfocus.com/brand/michigan-football-focus.png" width={78} height={26} alt="" />
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, color: NAVY }}>MICHIGANFOOTBALLFOCUS.COM</span>
      </div>
    </div>
  );
}

// ---- root ----

export function MatchupGraphic({ data }: { data: MatchupGraphicData }) {
  const opponentColors = teamColors(data.opponent.teamId);
  const opponentAccent = accentColorOnLight(opponentColors);

  return (
    <div style={{ display: "flex", flexDirection: "column", width: 1600, backgroundColor: CREAM, fontFamily: "Inter", border: `1px solid ${LINE}` }}>
      <Header data={data} />

      <div style={{ display: "flex", flexDirection: "column", padding: "22px 60px 0" }}>
        <TeamComparisonBlock data={data} opponentAccent={opponentAccent} />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "20px 0 18px" }} />

        <PhaseSection
          phase={data.whenMichiganHasBall}
          title="WHEN MICHIGAN HAS THE BALL"
          headingColor={MAIZE}
          opponentAccent={opponentAccent}
          offenseLabel="MICHIGAN OFFENSE"
          defenseLabel={`${data.opponent.name.toUpperCase()} DEFENSE`}
        />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "18px 0" }} />

        <PhaseSection
          phase={data.whenOpponentHasBall}
          title={`WHEN ${data.opponent.name.toUpperCase()} HAS THE BALL`}
          headingColor={opponentAccent}
          opponentAccent={opponentAccent}
          offenseLabel={`${data.opponent.name.toUpperCase()} OFFENSE`}
          defenseLabel="MICHIGAN DEFENSE"
        />

        <div style={{ display: "flex", flexDirection: "column", marginTop: 18 }}>
          <PredictionOutlook data={data} />
        </div>

        <Footer />
      </div>
    </div>
  );
}

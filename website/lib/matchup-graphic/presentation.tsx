// PRESENTATION layer: pure JSX. Takes a fully-analyzed MatchupGraphicData
// and renders it -- there is deliberately no team name, statistic, edge
// score, or sentence hardcoded anywhere in this file. Every word on the
// graphic comes from `data`, `teamColors`/`accentColorOnLight`
// (lib/team-colors.ts, keyed by teamId), or `teamLogoUrl`
// (lib/team-assets.ts, keyed by teamId) -- swap the gameId this is built
// from and the whole graphic becomes a different team's story with zero
// JSX changes.
//
// Visual direction: a bright cream editorial "scouting sheet," not a dark
// dashboard. Dark navy is used only as an accent -- header, section
// labels, dividers, the prediction strip, the footer -- everything else
// stays on the cream page background so the numbers stay easy to read.
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
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", backgroundColor: NAVY, padding: "24px 56px" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.michigan.teamId, 256)} width={92} height={92} alt="" />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 46, fontWeight: 700, color: CREAM_TEXT }}>
          MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 20, fontWeight: 600, color: "rgba(245,240,230,0.55)", margin: "0 16px" }}>vs</span>{data.opponent.name.toUpperCase()}
        </div>
        <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: MAIZE, letterSpacing: 2.2, marginTop: 8 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.opponent.teamId, 256)} width={92} height={92} alt="" />
    </div>
  );
}

function SectionLabel({ children }: { children: string }) {
  return (
    <div style={{ display: "flex", alignSelf: "flex-start", backgroundColor: NAVY, borderRadius: 3, padding: "7px 14px", marginBottom: 16 }}>
      <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 1.8, color: CREAM_TEXT }}>{children}</span>
    </div>
  );
}

function RankChip({ rank }: { rank: number }) {
  const { bg, text } = rankChipColors(rank);
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: bg, borderRadius: 6, padding: "5px 12px", minWidth: 46 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: text }}>{`#${rank}`}</span>
    </div>
  );
}

// ---- team quality ----

function TeamQuality({ data, opponentAccent }: { data: MatchupGraphicData; opponentAccent: string }) {
  const rows = [
    { label: "OVERALL", mich: data.michigan.quality.overall.rank, opp: data.opponent.quality.overall.rank },
    { label: "OFFENSE", mich: data.michigan.quality.offense.rank, opp: data.opponent.quality.offense.rank },
    { label: "DEFENSE", mich: data.michigan.quality.defense.rank, opp: data.opponent.quality.defense.rank },
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <SectionLabel>TEAM QUALITY</SectionLabel>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", padding: "0 2px 10px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, color: NAVY }}>{data.michigan.name.toUpperCase()}</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, color: opponentAccent }}>{data.opponent.name.toUpperCase()}</span>
      </div>
      {rows.map((r) => (
        <div key={r.label} style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "12px 2px", borderTop: `1px solid ${LINE}` }}>
          <RankChip rank={r.mich} />
          <span style={{ display: "flex", flex: 1, justifyContent: "center", fontFamily: "Inter", fontSize: 16, fontWeight: 700, color: NAVY, letterSpacing: 1.4 }}>{r.label}</span>
          <RankChip rank={r.opp} />
        </div>
      ))}
    </div>
  );
}

// ---- how they play ----

function PlayCallColumn({ name, nameColor, barColor, runPct, passPct }: { name: string; nameColor: string; barColor: string; runPct: number; passPct: number }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 18, fontWeight: 700, color: nameColor }}>{name.toUpperCase()}</span>
      <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 4 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 27, fontWeight: 700, color: NAVY }}>{`${runPct}% RUN`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 600, color: SLATE }}>{`${passPct}% PASS`}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", width: "100%", height: 14, borderRadius: 4, overflow: "hidden", marginTop: 9 }}>
        <div style={{ display: "flex", width: `${runPct}%`, backgroundColor: barColor }} />
        <div style={{ display: "flex", width: `${passPct}%`, backgroundColor: PASS_BAR }} />
      </div>
    </div>
  );
}

function HowTheyPlay({ data, opponentAccent }: { data: MatchupGraphicData; opponentAccent: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <SectionLabel>PLAY-CALL SPLIT</SectionLabel>
      <div style={{ display: "flex", flexDirection: "row", gap: 48 }}>
        <PlayCallColumn name={data.michigan.name} nameColor={NAVY} barColor={MAIZE} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} passPct={100 - Math.round(data.michigan.tendencies.rushDecisionRate * 100)} />
        <PlayCallColumn name={data.opponent.name} nameColor={opponentAccent} barColor={opponentAccent} runPct={Math.round(data.opponent.tendencies.rushDecisionRate * 100)} passPct={100 - Math.round(data.opponent.tendencies.rushDecisionRate * 100)} />
      </div>
    </div>
  );
}

// ---- field position ----

function FieldPositionMarker({ color, leftPct }: { color: string; leftPct: number }) {
  return (
    <div style={{ display: "flex", position: "absolute", left: `${leftPct}%`, top: -7, width: 16, height: 16, borderRadius: 8, backgroundColor: NAVY, alignItems: "center", justifyContent: "center", marginLeft: -8 }}>
      <div style={{ display: "flex", width: 9, height: 9, borderRadius: 5, backgroundColor: color }} />
    </div>
  );
}

function FieldPositionSection({ data, opponentAccent }: { data: MatchupGraphicData; opponentAccent: string }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  const pct = (yardLine: number) => Math.max(2, Math.min(98, (yardLine / 50) * 100));
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <SectionLabel>AVERAGE STARTING FIELD POSITION</SectionLabel>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", padding: "0 1px" }}>
        {["OWN GOAL", "20", "30", "40", "50"].map((t) => (
          <span key={t} style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, color: SLATE }}>{t}</span>
        ))}
      </div>
      <div style={{ display: "flex", position: "relative", width: "100%", height: 3, backgroundColor: LINE, marginTop: 10 }}>
        {mich && <FieldPositionMarker color={MAIZE} leftPct={pct(mich.ownYardLine)} />}
        {opp && <FieldPositionMarker color={opponentAccent} leftPct={pct(opp.ownYardLine)} />}
      </div>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", marginTop: 26 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 17, fontWeight: 700, color: NAVY }}>{`${data.michigan.name.toUpperCase()}: ${mich ? `OWN ${mich.ownYardLine.toFixed(1)}` : "—"}`}</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 17, fontWeight: 700, color: opponentAccent }}>{`${data.opponent.name.toUpperCase()}: ${opp ? `OWN ${opp.ownYardLine.toFixed(1)}` : "—"}`}</span>
      </div>
      <div style={{ display: "flex", alignSelf: "center", marginTop: 16, backgroundColor: NAVY, borderRadius: 4, padding: "7px 18px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, color: CREAM_TEXT, letterSpacing: 0.4 }}>{fieldPositionEdge(mich, opp, data.michigan.name, data.opponent.name)}</span>
      </div>
    </div>
  );
}

// ---- possession phase (main centerpiece) ----

function PhaseRow({ row, opponentAccent }: { row: PhaseEdgeRow; opponentAccent: string }) {
  const vcolors = verdictColors(row.direction, opponentAccent);
  const hasData = row.tier !== "insufficient";
  const markerPct = 50 - (row.score ?? 0) / 2;
  return (
    <div style={{ display: "flex", flexDirection: "column", padding: "12px 2px", borderTop: `1px solid ${LINE}` }}>
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
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 12, marginTop: 8 }}>
        <div style={{ display: "flex", position: "relative", width: 64, height: 3, borderRadius: 2, backgroundColor: "rgba(11,31,51,0.13)" }}>
          {hasData && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -3, width: 9, height: 9, borderRadius: 5, backgroundColor: vcolors.dot, marginLeft: -4.5 }} />}
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
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 36, fontWeight: 700, color: NAVY }}>{title}</span>
        <div style={{ display: "flex", width: 96, height: 4, backgroundColor: headingColor, marginTop: 6, borderRadius: 2 }} />
      </div>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", marginTop: 20, padding: "0 2px" }}>
        <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1, color: SLATE }}>{offenseLabel}</span>
        <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1, color: SLATE }}>{defenseLabel}</span>
      </div>
      {phase.rows.map((row) => <PhaseRow key={row.id} row={row} opponentAccent={opponentAccent} />)}
      <div style={{ display: "flex", flexDirection: "column", marginTop: 16, paddingTop: 16, borderTop: `2px solid ${NAVY}` }}>
        <span style={{ fontFamily: "Inter", fontSize: 11.5, fontWeight: 800, letterSpacing: 1.4, color: NAVY }}>WHAT IT MEANS</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: NAVY, marginTop: 5, lineHeight: 1.25 }}>{phase.whatItMeans}</span>
      </div>
    </div>
  );
}

// ---- prediction ----

function PredictionOutlook({ data }: { data: MatchupGraphicData }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", backgroundColor: NAVY, borderRadius: 6, padding: "24px 40px", alignItems: "center" }}>
      <span style={{ fontFamily: "Inter", fontSize: 14, fontWeight: 800, letterSpacing: 2.6, color: "rgba(245,240,230,0.62)" }}>MATCHUP OUTLOOK</span>

      {data.prediction.type === "model" && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 54, fontWeight: 700, color: CREAM_TEXT, marginTop: 8, lineHeight: 1 }}>{data.prediction.marginLabel}</span>
          <div style={{ display: "flex", flexDirection: "row", gap: 30, marginTop: 12 }}>
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
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 1.8, color: MAIZE, marginTop: 10 }}>MARKET EXPECTATION</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 54, fontWeight: 700, color: CREAM_TEXT, marginTop: 8, lineHeight: 1 }}>{data.prediction.spreadLabel}</span>
          <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 600, color: "rgba(245,240,230,0.72)", marginTop: 8 }}>{data.prediction.book}</span>
        </div>
      )}

      {data.prediction.type === "unavailable" && (
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 38, fontWeight: 700, color: "rgba(245,240,230,0.55)", marginTop: 16 }}>NO PREDICTION AVAILABLE</span>
      )}
    </div>
  );
}

function Footer() {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "22px 0 30px", marginTop: 8 }}>
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

      <div style={{ display: "flex", flexDirection: "column", padding: "30px 60px 0" }}>
        <TeamQuality data={data} opponentAccent={opponentAccent} />

        <div style={{ display: "flex", flexDirection: "column", marginTop: 32 }}>
          <HowTheyPlay data={data} opponentAccent={opponentAccent} />
        </div>

        <div style={{ display: "flex", flexDirection: "column", marginTop: 32 }}>
          <FieldPositionSection data={data} opponentAccent={opponentAccent} />
        </div>

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "36px 0 32px" }} />

        <PhaseSection
          phase={data.whenMichiganHasBall}
          title="WHEN MICHIGAN HAS THE BALL"
          headingColor={MAIZE}
          opponentAccent={opponentAccent}
          offenseLabel="MICHIGAN OFFENSE"
          defenseLabel={`${data.opponent.name.toUpperCase()} DEFENSE`}
        />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "32px 0" }} />

        <PhaseSection
          phase={data.whenOpponentHasBall}
          title={`WHEN ${data.opponent.name.toUpperCase()} HAS THE BALL`}
          headingColor={opponentAccent}
          opponentAccent={opponentAccent}
          offenseLabel={`${data.opponent.name.toUpperCase()} OFFENSE`}
          defenseLabel="MICHIGAN DEFENSE"
        />

        <div style={{ display: "flex", flexDirection: "column", marginTop: 32 }}>
          <PredictionOutlook data={data} />
        </div>

        <Footer />
      </div>
    </div>
  );
}

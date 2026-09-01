// PRESENTATION layer: pure JSX. Takes a fully-analyzed MatchupGraphicData
// and renders it -- there is deliberately no team name, statistic, edge
// score, or sentence hardcoded anywhere in this file. Every word on the
// graphic comes from `data`, `teamAbbreviation` (lib/team-colors.ts,
// keyed by teamId), or `teamLogoUrl` (lib/team-assets.ts, keyed by
// teamId) -- swap the gameId this is built from and the whole graphic
// becomes a different team's story with zero JSX changes.
//
// Fixed 1600x900 landscape canvas (a hard requirement -- see
// app/matchup-graphic/[gameId]/route.tsx). Five horizontal zones:
// header, team snapshot, two possession panels side by side, a closing
// navy prediction strip, and a small cream footer.
//
// Color system: cream page, Michigan navy for essentially all text
// (Michigan's AND the opponent's), maize used only as tiny accents
// (a seal line, one divider, the wordmark). No quality-based rank
// coloring, no per-team accent coloring of data -- team identity comes
// from the real logos and the words on the page, not from paint.
import { teamLogoUrl } from "../team-assets";
import { teamAbbreviation } from "../team-colors";
import type { EdgeCategoryId, MatchupGraphicData, PhaseEdgeRow, PossessionPhase } from "./types";

const CREAM = "#F5F0E6";
const CREAM_TEXT = "#F5F0E6";
const OFFWHITE = "#FAF8F2";
const NAVY = "#00274C"; // official Michigan navy
const MAIZE = "#FFCB05"; // tiny accent only -- never body text on cream
const SLATE = "#3D5166"; // darkened for legibility at small sizes on cream -- see team-colors contrast note below
const LIGHT_BLUE_GRAY = "#D7E0E8";
const LINE = "rgba(0,39,76,0.14)"; // navy at low opacity -- the one border system, used everywhere
const CHIP_BORDER = "rgba(0,39,76,0.22)";

// Uses the real team abbreviation (e.g. "WMU", "OU") rather than a
// generic "OPP" -- an edge label must always explicitly name a team.
// Every tier/direction renders in the same navy-outlined style; only
// the wording changes ("MICH EDGE" vs "WMU EDGE" vs "EVEN") -- color is
// not what tells the reader who has the edge.
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
// apart. Nudges two close positions apart to a minimum visual gap
// around their shared midpoint, preserving which one leads -- the
// exact values are still shown precisely in the text readout below,
// this only keeps the schematic dots from visually merging into one.
function declutter(a: number, b: number, minGap: number): [number, number] {
  const gap = b - a;
  if (Math.abs(gap) >= minGap) return [a, b];
  const mid = (a + b) / 2;
  const half = minGap / 2;
  return gap >= 0 ? [mid - half, mid + half] : [mid + half, mid - half];
}

// ---- small inline icons (no external icon library) ----

function EfficiencyGlyph() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <rect x="1" y="8" width="3" height="5" fill={CREAM} />
      <rect x="5.5" y="4.5" width="3" height="8.5" fill={CREAM} />
      <rect x="10" y="1" width="3" height="12" fill={CREAM} />
    </svg>
  );
}
function RunGlyph() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <circle cx="8.2" cy="2.6" r="1.5" fill={CREAM} />
      <path d="M6 5.2 L9 6 L11 4.6 M9 6 L8 9.5 L10.2 12.8 M8 9.5 L4.8 11.5 M9 6 L5.8 7.8" stroke={CREAM} strokeWidth="1.15" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    </svg>
  );
}
function PassGlyph() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M1.5 7 C1.5 4 4.5 2 7 2 C9.5 2 12.5 4 12.5 7 C12.5 10 9.5 12 7 12 C4.5 12 1.5 10 1.5 7 Z" stroke={CREAM} strokeWidth="1.2" fill="none" />
      <line x1="7" y1="4.3" x2="7" y2="9.7" stroke={CREAM} strokeWidth="0.9" />
      <line x1="5.8" y1="5.4" x2="8.2" y2="5.4" stroke={CREAM} strokeWidth="0.7" />
      <line x1="5.8" y1="8.6" x2="8.2" y2="8.6" stroke={CREAM} strokeWidth="0.7" />
    </svg>
  );
}
function ExplosivenessGlyph() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M7 0.5 L8.6 5 L13 5.3 L9.5 8.2 L10.6 12.8 L7 10.2 L3.4 12.8 L4.5 8.2 L1 5.3 L5.4 5 Z" fill={CREAM} />
    </svg>
  );
}
function ThirdDownGlyph() {
  return <span style={{ display: "flex", fontFamily: "Inter", fontSize: 8.5, fontWeight: 800, color: CREAM }}>3RD</span>;
}
function TrendGlyph() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M1.5 11.5 L6 6.5 L9 9 L14.5 2.5" stroke={CREAM} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <path d="M10.5 2.5 L14.5 2.5 L14.5 6.5" stroke={CREAM} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    </svg>
  );
}
function DollarGlyph() {
  return <span style={{ display: "flex", fontFamily: "Inter", fontSize: 15, fontWeight: 800, color: CREAM }}>$</span>;
}

const CATEGORY_GLYPH: Record<EdgeCategoryId, () => React.ReactElement> = {
  efficiency: EfficiencyGlyph,
  run: RunGlyph,
  pass: PassGlyph,
  explosiveness: ExplosivenessGlyph,
  situational: ThirdDownGlyph,
};

function IconBadge({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", width: 28, height: 28, borderRadius: 14, backgroundColor: NAVY, alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
      {children}
    </div>
  );
}

function OutlineIconBadge({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", width: 34, height: 34, borderRadius: 17, border: "1.5px solid rgba(245,240,230,0.5)", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
      {children}
    </div>
  );
}

// ---- header (zone 1) ----

function Header({ data }: { data: MatchupGraphicData }) {
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "long", month: "long", day: "numeric", year: "numeric" });
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", backgroundColor: NAVY, padding: "7px 40px" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.michigan.teamId, 256)} width={92} height={92} alt="" />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 58, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>
          MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 28, fontWeight: 600, color: "rgba(245,240,230,0.55)", margin: "0 16px" }}>vs</span>{data.opponent.name.toUpperCase()}
        </div>
        <div style={{ display: "flex", fontFamily: "Inter", fontSize: 18, fontWeight: 700, color: "rgba(245,240,230,0.8)", letterSpacing: 1.2, marginTop: 6 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.opponent.teamId, 256)} width={100} height={100} alt="" />
    </div>
  );
}

function RankChip({ rank, size }: { rank: number; size: "sm" | "lg" }) {
  const fontSize = size === "lg" ? 24 : 19;
  const padding = size === "lg" ? "5px 12px" : "3px 9px";
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: OFFWHITE, border: `1.5px solid ${CHIP_BORDER}`, borderRadius: 6, padding, minWidth: size === "lg" ? 52 : 40 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize, fontWeight: 700, color: NAVY }}>{`#${rank}`}</span>
    </div>
  );
}

function VDivider({ height }: { height: number }) {
  return <div style={{ display: "flex", width: 1, height, backgroundColor: LINE }} />;
}

// ---- zone 2: team snapshot ----

function TeamColumn({ name, quality, runPct, align }: { name: string; quality: MatchupGraphicData["michigan"]["quality"]; runPct: number; align: "left" | "right" }) {
  const passPct = 100 - runPct;
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, alignItems: align === "left" ? "flex-start" : "flex-end" }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: NAVY }}>{name.toUpperCase()}</span>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 10, marginTop: 2 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 60, fontWeight: 700, color: NAVY, lineHeight: 1 }}>{`#${quality.overall.rank}`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 17, fontWeight: 800, color: SLATE, letterSpacing: 0.6 }}>OVERALL</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 16, marginTop: 6 }}>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 7 }}>
          <RankChip rank={quality.offense.rank} size="lg" />
          <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 700, color: SLATE }}>OFFENSE</span>
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 7 }}>
          <RankChip rank={quality.defense.rank} size="lg" />
          <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 700, color: SLATE }}>DEFENSE</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 10, marginTop: 7 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 31, fontWeight: 700, color: NAVY }}>{`${runPct}% RUN`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 20, fontWeight: 600, color: SLATE }}>{`${passPct}% PASS`}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", width: 320, height: 11, borderRadius: 3, overflow: "hidden", marginTop: 5 }}>
        <div style={{ display: "flex", width: `${runPct}%`, backgroundColor: NAVY }} />
        <div style={{ display: "flex", width: `${passPct}%`, backgroundColor: LIGHT_BLUE_GRAY }} />
      </div>
    </div>
  );
}

// Dot is the positioned root (fixed height, always on the track); the
// label is a normal-flow child below it, so a taller `lift` margin can
// never disturb the dot's own position -- a nested-absolute version of
// this once broke percentage-based positioning in Satori (see git log).
function FieldPositionMarker({ abbr, leftPct, lift }: { abbr: string; leftPct: number; lift: boolean }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", position: "absolute", left: `${leftPct}%`, top: -5, marginLeft: -18, width: 36 }}>
      <div style={{ display: "flex", width: 10, height: 10, borderRadius: 5, backgroundColor: NAVY, border: `2px solid ${CREAM}` }} />
      <span style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 800, color: NAVY, marginTop: lift ? 22 : 7 }}>{abbr}</span>
    </div>
  );
}

function FieldPositionMini({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  const pct = (yardLine: number) => Math.max(3, Math.min(97, (yardLine / 50) * 100));
  const rawMichPct = mich ? pct(mich.ownYardLine) : null;
  const rawOppPct = opp ? pct(opp.ownYardLine) : null;
  const [michPct, oppPct] = rawMichPct != null && rawOppPct != null ? declutter(rawMichPct, rawOppPct, 6) : [rawMichPct, rawOppPct];
  const closeMarkers = michPct != null && oppPct != null && Math.abs(michPct - oppPct) < 9;
  const trackWidth = 480;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 560 }}>
      <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 800, letterSpacing: 1.2, color: SLATE }}>AVERAGE STARTING FIELD POSITION</span>
      <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", width: trackWidth, marginTop: 13 }}>
        {["20", "30", "40", "50"].map((t) => (
          <span key={t} style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: SLATE }}>{t}</span>
        ))}
      </div>
      <div style={{ display: "flex", position: "relative", width: trackWidth, height: 3, backgroundColor: LIGHT_BLUE_GRAY, marginTop: 8, marginBottom: 46 }}>
        {[0, 33.3, 66.6, 100].map((t) => (
          <div key={t} style={{ display: "flex", position: "absolute", left: `${t}%`, top: -3, width: 1, height: 9, backgroundColor: "rgba(0,39,76,0.3)", marginLeft: t === 100 ? -1 : 0 }} />
        ))}
        {mich && michPct != null && <FieldPositionMarker abbr={michAbbr} leftPct={michPct} lift={false} />}
        {opp && oppPct != null && <FieldPositionMarker abbr={oppAbbr} leftPct={oppPct} lift={closeMarkers} />}
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", width: 340 }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", flex: 1 }}>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, color: SLATE, letterSpacing: 0.6 }}>{michAbbr}</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, color: NAVY, marginTop: 1 }}>{mich ? `OWN ${mich.ownYardLine.toFixed(1)}` : "—"}</span>
        </div>
        <VDivider height={34} />
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", flex: 1 }}>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, color: SLATE, letterSpacing: 0.6 }}>{oppAbbr}</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, color: NAVY, marginTop: 1 }}>{opp ? `OWN ${opp.ownYardLine.toFixed(1)}` : "—"}</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: 14 }}>
        <div style={{ display: "flex", backgroundColor: NAVY, borderRadius: 4, padding: "6px 18px" }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: CREAM_TEXT, letterSpacing: 0.3 }}>{fieldPositionEdgeLabel(mich, opp, michAbbr, oppAbbr)}</span>
        </div>
        <div style={{ display: "flex", width: 60, height: 2, backgroundColor: MAIZE, marginTop: 4, borderRadius: 1 }} />
      </div>
    </div>
  );
}

function TeamSnapshotZone({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between" }}>
      <TeamColumn name={data.michigan.name} quality={data.michigan.quality} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} align="left" />
      <div style={{ display: "flex", padding: "6px 26px 0" }}><VDivider height={150} /></div>
      <FieldPositionMini data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />
      <div style={{ display: "flex", padding: "6px 26px 0" }}><VDivider height={150} /></div>
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
  const Glyph = CATEGORY_GLYPH[row.id];
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 12, padding: "6px 0", borderTop: `1px solid ${LINE}` }}>
      <IconBadge><Glyph /></IconBadge>
      <span style={{ display: "flex", width: 150, flexShrink: 0, fontFamily: "Barlow Condensed", fontSize: 17, fontWeight: 700, color: NAVY, letterSpacing: 0.2 }}>{row.label}</span>
      <RankChip rank={row.offense.rank} size="sm" />
      <div style={{ display: "flex", flex: 1, position: "relative", height: 3, backgroundColor: LIGHT_BLUE_GRAY, borderRadius: 2 }}>
        <div style={{ display: "flex", position: "absolute", left: "50%", top: -4.5, width: 1, height: 12, backgroundColor: "rgba(0,39,76,0.35)" }} />
        {hasData && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -5.5, width: 14, height: 14, borderRadius: 7, backgroundColor: NAVY, marginLeft: -7, border: `2px solid ${CREAM}` }} />}
      </div>
      <RankChip rank={row.defense.rank} size="sm" />
      <div style={{ display: "flex", minWidth: 148, justifyContent: "center", backgroundColor: OFFWHITE, border: `1.5px solid ${NAVY}`, borderRadius: 5, padding: "4px 10px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, letterSpacing: 0.2, color: NAVY }}>{hasData ? shortVerdict(row.tier, row.direction, opponentAbbr) : "NO DATA"}</span>
      </div>
    </div>
  );
}

function PhasePanel({ phase, title, subtitle, opponentAbbr }: { phase: PossessionPhase; title: string; subtitle: string; opponentAbbr: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, border: `1px solid ${CHIP_BORDER}`, borderRadius: 8, overflow: "hidden", backgroundColor: CREAM }}>
      <div style={{ display: "flex", backgroundColor: NAVY, padding: "10px 20px", justifyContent: "center" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 25, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{title}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", padding: "8px 22px 10px" }}>
        <span style={{ display: "flex", alignSelf: "center", fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: SLATE }}>{subtitle}</span>
        <div style={{ display: "flex", flexDirection: "row", justifyContent: "center", gap: 20, marginTop: 4 }}>
          <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 0.6, color: SLATE }}>MICH ADVANTAGE</span>
          <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 0.6, color: SLATE }}>EVEN</span>
          <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 0.6, color: SLATE }}>{`${opponentAbbr} ADVANTAGE`}</span>
        </div>
        {phase.rows.map((row) => <PhaseRow key={row.id} row={row} opponentAbbr={opponentAbbr} />)}
        <div style={{ display: "flex", flexDirection: "column", marginTop: 4, padding: "6px 16px", borderRadius: 6, backgroundColor: LIGHT_BLUE_GRAY }}>
          <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1, color: NAVY }}>THE READ</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: NAVY, marginTop: 2, lineHeight: 1.15 }}>{phase.whatItMeans}</span>
        </div>
      </div>
    </div>
  );
}

// ---- zone 4: prediction ----

function PredictionOutlookZone({ data }: { data: MatchupGraphicData }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", backgroundColor: NAVY, padding: "10px 40px 8px" }}>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center" }}>
        {data.prediction.type === "model" && (
          <div style={{ display: "flex", flexDirection: "row", alignItems: "center" }}>
            {data.prediction.winProbabilityPct != null && (
              <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 12 }}>
                <OutlineIconBadge><TrendGlyph /></OutlineIconBadge>
                <div style={{ display: "flex", flexDirection: "column" }}>
                  <span style={{ fontFamily: "Barlow Condensed", fontSize: 40, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{`${data.prediction.winProbabilityPct}%`}</span>
                  <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, letterSpacing: 0.6, color: "rgba(245,240,230,0.65)" }}>WIN PROBABILITY</span>
                </div>
              </div>
            )}
            {data.prediction.winProbabilityPct != null && <div style={{ display: "flex", width: 1, height: 46, backgroundColor: "rgba(245,240,230,0.25)", margin: "0 40px" }} />}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, letterSpacing: 0.6, color: "rgba(245,240,230,0.65)" }}>MFF PROJECTION</span>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 52, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{data.prediction.marginLabel}</span>
            </div>
            {data.prediction.marketNote && <div style={{ display: "flex", width: 1, height: 46, backgroundColor: "rgba(245,240,230,0.25)", margin: "0 40px" }} />}
            {data.prediction.marketNote && (
              <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 12 }}>
                <OutlineIconBadge><DollarGlyph /></OutlineIconBadge>
                <div style={{ display: "flex", flexDirection: "column" }}>
                  <span style={{ fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{data.prediction.marketNote.replace("Market: ", "")}</span>
                  <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, letterSpacing: 0.6, color: "rgba(245,240,230,0.65)" }}>MARKET</span>
                </div>
              </div>
            )}
          </div>
        )}
        {data.prediction.type === "market" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 1.4, color: MAIZE }}>MARKET EXPECTATION</span>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 52, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1, marginTop: 2 }}>{data.prediction.spreadLabel}</span>
            <span style={{ fontFamily: "Inter", fontSize: 14, fontWeight: 600, color: "rgba(245,240,230,0.75)", marginTop: 3 }}>{data.prediction.book}</span>
          </div>
        )}
        {data.prediction.type === "unavailable" && (
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: "rgba(245,240,230,0.55)" }}>PREDICTION NOT AVAILABLE</span>
        )}
      </div>
      <div style={{ display: "flex", width: "100%", height: 1, backgroundColor: "rgba(255,203,5,0.55)", marginTop: 7 }} />
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", justifyContent: "center", gap: 10, marginTop: 6 }}>
        <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1, color: MAIZE }}>THE BOTTOM LINE</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: CREAM_TEXT }}>{data.bottomLine}</span>
      </div>
    </div>
  );
}

function Footer() {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "6px 40px", backgroundColor: CREAM }}>
      <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: SLATE }}>2025 OPPONENT-ADJUSTED METRICS · FBS RANKS · MFF MODEL · MARKET LABELED SEPARATELY</span>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 10 }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="https://michiganfootballfocus.com/brand/michigan-football-focus.png" width={54} height={18} alt="" />
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 14, fontWeight: 700, color: NAVY }}>MICHIGANFOOTBALLFOCUS.COM</span>
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
      {/* Maize appears only as tiny accents -- this seal line, one divider above THE BOTTOM LINE, one under the field-position edge badge, and the wordmark image. */}
      <div style={{ display: "flex", width: "100%", height: 3, backgroundColor: MAIZE }} />

      <Header data={data} />

      <div style={{ display: "flex", flexDirection: "column", padding: "10px 40px 0" }}>
        <TeamSnapshotZone data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "11px 0" }} />

        <div style={{ display: "flex", flexDirection: "row", gap: 28 }}>
          <PhasePanel
            phase={data.whenMichiganHasBall}
            title="WHEN MICHIGAN HAS THE BALL"
            subtitle={`MICHIGAN OFFENSE vs ${oppAbbr} DEFENSE`}
            opponentAbbr={oppAbbr}
          />
          <PhasePanel
            phase={data.whenOpponentHasBall}
            title={`WHEN ${data.opponent.name.toUpperCase()} HAS THE BALL`}
            subtitle={`${oppAbbr} OFFENSE vs MICHIGAN DEFENSE`}
            opponentAbbr={oppAbbr}
          />
        </div>
      </div>

      <PredictionOutlookZone data={data} />
      <Footer />
    </div>
  );
}

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
import type { MatchupGraphicData, PhaseEdgeRow, PossessionPhase } from "./types";

const CREAM = "#F4EFE4"; // main page cream
const CREAM_TEXT = "#F4EFE4";
const CARD_CREAM = "#FBF8F1"; // raised/card surfaces, e.g. the possession panels
const OFFWHITE = "#FAF8F2";
const NAVY = "#00274C"; // official Michigan navy
const MEDIUM_BLUE = "#315A7D";
const MAIZE = "#FFCB05"; // tiny accent only -- never body text on cream
const SLATE = "#3D5166"; // darkened for legibility at small sizes on cream -- see team-colors contrast note below
const LIGHT_BLUE_GRAY = "#D7E0E8";
const SOFT_BLUE = "#DCE6EC"; // Michigan-side slider/track tint
const WARM_TAUPE = "#D9D0C2"; // opponent-side slider tint, opponent PASS bar
const DARK_WARM_GRAY = "#625E58"; // neutral/even marker and text
const LINE = "rgba(0,39,76,0.14)"; // navy at low opacity -- the one border system, used everywhere
const CHIP_BORDER = "rgba(0,39,76,0.22)";

// Michigan is always cool/navy family; the opponent is always this same
// restrained warm family regardless of which real team it is -- a
// consistent MFF identity week to week, the same reason the site never
// pulls a real opponent's brand color into the data. "Opponent" here is
// a fixed second color slot, not Western Michigan's actual brand brown.
const OPPONENT_ACCENT = "#6C3F2A"; // opponent RUN bar, opponent-edge text, opponent slider marker
const OPPONENT_HEADER = "#593827"; // opponent possession-panel header bar (muted vs. OPPONENT_ACCENT so it doesn't fight the navy header next to it)
const MICHIGAN_TINT = "#EEF3F6"; // pale cool wash behind Michigan's snapshot column
const OPPONENT_TINT = "#F3ECE6"; // pale warm wash behind the opponent's snapshot column -- same visual weight as MICHIGAN_TINT for symmetry
const MICH_EDGE_TINT = "#E6EEF3";
const MICH_EDGE_TINT_STRONG = "#D3E3EC";
const OPPONENT_EDGE_TINT = "#EEE4DC";
const OPPONENT_EDGE_TINT_STRONG = "#E3D2C4";
const EVEN_EDGE_TINT = "#E9E6E0";
const READ_BG = "#E8E1D7"; // warm off-white for THE READ, distinct from the cool edge tints above

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

// Team ownership (Michigan = cool blue family, opponent = warm brown
// family, even = neutral) communicated through fill and border, not
// through statistical quality -- this is deliberately the only axis of
// color variation here. "Strong" tier gets a richer tint/border of the
// *same* hue rather than a different color.
function edgeChipStyle(tier: PhaseEdgeRow["tier"], direction: PhaseEdgeRow["direction"]): { bg: string; text: string; border: string } {
  if (direction === "even" || tier === "insufficient") return { bg: EVEN_EDGE_TINT, text: DARK_WARM_GRAY, border: CHIP_BORDER };
  if (direction === "michigan") return { bg: tier === "strong" ? MICH_EDGE_TINT_STRONG : MICH_EDGE_TINT, text: NAVY, border: tier === "strong" ? MEDIUM_BLUE : CHIP_BORDER };
  return { bg: tier === "strong" ? OPPONENT_EDGE_TINT_STRONG : OPPONENT_EDGE_TINT, text: OPPONENT_ACCENT, border: tier === "strong" ? OPPONENT_ACCENT : CHIP_BORDER };
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
// Category row icons were removed for clarity (see git log) -- only the
// prediction strip's two icons remain.

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
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", backgroundColor: NAVY, padding: "5px 40px" }}>
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

// One consistent size and style everywhere a rank appears -- the team
// snapshot and the matchup rows should read as the same typographic
// scale (see the symmetry note on TeamColumn/PhaseRow).
function RankChip({ rank }: { rank: number }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: OFFWHITE, border: `1.5px solid ${CHIP_BORDER}`, borderRadius: 6, padding: "4px 13px", minWidth: 56 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 23, fontWeight: 700, color: NAVY }}>{`#${rank}`}</span>
    </div>
  );
}

function VDivider({ height }: { height: number }) {
  return <div style={{ display: "flex", width: 1, height, backgroundColor: LINE }} />;
}

// ---- zone 2: team snapshot ----

function TeamColumn({ name, quality, runPct, align, tintBg, runColor, passColor }: { name: string; quality: MatchupGraphicData["michigan"]["quality"]; runPct: number; align: "left" | "right"; tintBg: string; runColor: string; passColor: string }) {
  const passPct = 100 - runPct;
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, alignItems: align === "left" ? "flex-start" : "flex-end", justifyContent: "center", backgroundColor: tintBg, padding: "4px 22px" }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: NAVY }}>{name.toUpperCase()}</span>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 10, marginTop: 2 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 60, fontWeight: 700, color: NAVY, lineHeight: 1 }}>{`#${quality.overall.rank}`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 17, fontWeight: 800, color: SLATE, letterSpacing: 0.6 }}>OVERALL</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 16, marginTop: 6 }}>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 7 }}>
          <RankChip rank={quality.offense.rank} />
          <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 700, color: SLATE }}>OFFENSE</span>
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 7 }}>
          <RankChip rank={quality.defense.rank} />
          <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 700, color: SLATE }}>DEFENSE</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", gap: 10, marginTop: 7 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 31, fontWeight: 700, color: NAVY }}>{`${runPct}% RUN`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 20, fontWeight: 600, color: SLATE }}>{`${passPct}% PASS`}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "row", width: 320, height: 11, borderRadius: 3, overflow: "hidden", marginTop: 5 }}>
        <div style={{ display: "flex", width: `${runPct}%`, backgroundColor: runColor }} />
        <div style={{ display: "flex", width: `${passPct}%`, backgroundColor: passColor }} />
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
      {lift && <div style={{ display: "flex", width: 1, height: 15, backgroundColor: DARK_WARM_GRAY, marginTop: 2 }} />}
      <span style={{ display: "flex", fontFamily: "Inter", fontSize: 15, fontWeight: 800, color: NAVY, marginTop: lift ? 2 : 8 }}>{abbr}</span>
    </div>
  );
}

function FieldPositionMini({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  const pct = (yardLine: number) => Math.max(3, Math.min(97, (yardLine / 50) * 100));
  const rawMichPct = mich ? pct(mich.ownYardLine) : null;
  const rawOppPct = opp ? pct(opp.ownYardLine) : null;
  const [michPct, oppPct] = rawMichPct != null && rawOppPct != null ? declutter(rawMichPct, rawOppPct, 8) : [rawMichPct, rawOppPct];
  const closeMarkers = michPct != null && oppPct != null && Math.abs(michPct - oppPct) < 11;
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
    <div style={{ display: "flex", flexDirection: "row", alignItems: "stretch", justifyContent: "space-between" }}>
      <TeamColumn name={data.michigan.name} quality={data.michigan.quality} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} align="left" tintBg={MICHIGAN_TINT} runColor={NAVY} passColor={SOFT_BLUE} />
      <div style={{ display: "flex", alignItems: "center", padding: "0 26px" }}><VDivider height={150} /></div>
      <div style={{ display: "flex", alignItems: "center" }}><FieldPositionMini data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} /></div>
      <div style={{ display: "flex", alignItems: "center", padding: "0 26px" }}><VDivider height={150} /></div>
      <TeamColumn name={data.opponent.name} quality={data.opponent.quality} runPct={Math.round(data.opponent.tendencies.rushDecisionRate * 100)} align="right" tintBg={OPPONENT_TINT} runColor={OPPONENT_ACCENT} passColor={WARM_TAUPE} />
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

// Fixed 4-column row: offense rank | metric name + slider (stacked) |
// defense rank | edge label. Column widths are fixed (not per-row
// content-fit) so every row's rank chips and edge chips line up exactly
// down the panel, and rank ownership never has to be inferred --
// column 1 is always this panel's offense rank, column 3 always its
// defense rank, matching the ownership header above.
//
// `flip` makes the slider's own left/right match the panel's offense/
// defense sides instead of a fixed Michigan-left convention: row.score
// is always Michigan-centric, so on the panel where the opponent is on
// offense (left), the marker position is mirrored so "left side of the
// slider" still means "the team in the offense column," consistent
// with the rank columns next to it.
function PhaseRow({ row, opponentAbbr, flip }: { row: PhaseEdgeRow; opponentAbbr: string; flip: boolean }) {
  const hasData = row.tier !== "insufficient";
  const rawMarkerPct = 50 - (row.score ?? 0) / 2;
  const markerPct = flip ? 100 - rawMarkerPct : rawMarkerPct;
  const chip = edgeChipStyle(row.tier, row.direction);
  const markerColor = row.direction === "michigan" ? NAVY : row.direction === "opponent" ? OPPONENT_ACCENT : DARK_WARM_GRAY;
  const trackLeftColor = flip ? WARM_TAUPE : SOFT_BLUE;
  const trackRightColor = flip ? SOFT_BLUE : WARM_TAUPE;
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 14, padding: "5px 0", borderTop: `1px solid ${LINE}` }}>
      <div style={{ display: "flex", width: 96, justifyContent: "center" }}>
        <RankChip rank={row.offense.rank} />
      </div>
      <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: NAVY, letterSpacing: 0.2 }}>{row.label}</span>
        <div style={{ display: "flex", position: "relative", height: 4, marginTop: 5 }}>
          <div style={{ display: "flex", flexDirection: "row", width: "100%", height: "100%", borderRadius: 2, overflow: "hidden" }}>
            <div style={{ display: "flex", width: "50%", height: "100%", backgroundColor: trackLeftColor }} />
            <div style={{ display: "flex", width: "50%", height: "100%", backgroundColor: trackRightColor }} />
          </div>
          <div style={{ display: "flex", position: "absolute", left: "50%", top: -4.5, width: 1, height: 13, backgroundColor: DARK_WARM_GRAY }} />
          {hasData && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -5.5, width: 15, height: 15, borderRadius: 7.5, backgroundColor: markerColor, marginLeft: -7.5, border: `2px solid ${CARD_CREAM}` }} />}
        </div>
      </div>
      <div style={{ display: "flex", width: 96, justifyContent: "center" }}>
        <RankChip rank={row.defense.rank} />
      </div>
      <div style={{ display: "flex", width: 168, justifyContent: "center", backgroundColor: chip.bg, border: `1.5px solid ${chip.border}`, borderRadius: 5, padding: "6px 8px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, letterSpacing: 0.2, color: chip.text, textAlign: "center" }}>{hasData ? shortVerdict(row.tier, row.direction, opponentAbbr) : "NO DATA"}</span>
      </div>
    </div>
  );
}

// `orientation` is the one piece of panel-role data everything else in
// this component derives from -- which real team sits in the offense
// column (left) here is the only thing that differs between the two
// panels, so column labels, the legend, and the slider's flip all read
// off this one flag rather than being written twice by hand.
function PhasePanel({ phase, title, opponentAbbr, headerColor, orientation }: { phase: PossessionPhase; title: string; opponentAbbr: string; headerColor: string; orientation: "michigan-left" | "opponent-left" }) {
  const flip = orientation === "opponent-left";
  const leftOwnerLabel = flip ? `${opponentAbbr} OFFENSE` : "MICHIGAN OFFENSE";
  const rightOwnerLabel = flip ? "MICHIGAN DEFENSE" : `${opponentAbbr} DEFENSE`;
  const legendLeft = flip ? opponentAbbr : "MICH";
  const legendRight = flip ? "MICH" : opponentAbbr;
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, border: `1px solid ${CHIP_BORDER}`, borderRadius: 8, overflow: "hidden", backgroundColor: CARD_CREAM }}>
      <div style={{ display: "flex", backgroundColor: headerColor, padding: "10px 20px", justifyContent: "center" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 25, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{title}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", padding: "8px 22px 8px" }}>
        <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between" }}>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 0.5, color: NAVY }}>{leftOwnerLabel}</span>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 0.5, color: NAVY }}>{rightOwnerLabel}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", justifyContent: "center", gap: 10, marginTop: 3 }}>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 0.4, color: SLATE }}>{legendLeft}</span>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: SLATE }}>&larr;</span>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, letterSpacing: 0.6, color: SLATE }}>EVEN</span>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: SLATE }}>&rarr;</span>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 0.4, color: SLATE }}>{legendRight}</span>
        </div>
        {phase.rows.map((row) => <PhaseRow key={row.id} row={row} opponentAbbr={opponentAbbr} flip={flip} />)}
        <div style={{ display: "flex", flexDirection: "column", marginTop: 4, padding: "6px 16px", borderRadius: 6, backgroundColor: READ_BG }}>
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

      <div style={{ display: "flex", flexDirection: "column", padding: "5px 40px 0" }}>
        <TeamSnapshotZone data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "6px 0" }} />

        <div style={{ display: "flex", flexDirection: "row", gap: 28 }}>
          <PhasePanel
            phase={data.whenMichiganHasBall}
            title="WHEN MICHIGAN HAS THE BALL"
            orientation="michigan-left"
            opponentAbbr={oppAbbr}
            headerColor={NAVY}
          />
          <PhasePanel
            phase={data.whenOpponentHasBall}
            title={`WHEN ${data.opponent.name.toUpperCase()} HAS THE BALL`}
            orientation="opponent-left"
            opponentAbbr={oppAbbr}
            headerColor={OPPONENT_HEADER}
          />
        </div>
      </div>

      <PredictionOutlookZone data={data} />
      <Footer />
    </div>
  );
}

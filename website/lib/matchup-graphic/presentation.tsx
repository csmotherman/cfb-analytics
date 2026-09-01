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
// Every zone is built on one strict grid, symmetric around x=800 (the
// canvas's true center), with fixed pixel widths rather than flex-
// computed ones. The two "mirrored" halves of the graphic (Michigan
// panel/opponent panel, left team/right team, left/right prediction
// blocks) are never two independently-styled JSX blocks -- each pair is
// ONE component (TeamSummary, MatchupPanel) rendered twice with only a
// side/data prop differing, so the two halves are geometrically
// identical by construction and can't drift out of alignment with each
// other as opponents change.
//
// Color system: cream page, Michigan navy for essentially all text and
// structure, maize used only as tiny accents (a seal line, one divider,
// the wordmark). Deliberately neutral otherwise -- no opponent-specific
// color anywhere in the base template. Opponent identity comes from the
// real logo and the team name text, not paint.
import { teamLogoUrl } from "../team-assets";
import { teamAbbreviation } from "../team-colors";
import type { MatchupGraphicData, PhaseEdgeRow, PossessionPhase } from "./types";

const CREAM = "#F4EFE4"; // main page cream
const CREAM_TEXT = "#F4EFE4";
const CARD_CREAM = "#FBF8F1"; // panel backgrounds -- possession panels AND both team-snapshot columns alike
const OFFWHITE = "#FAF8F2"; // rank chip / edge chip background
const NAVY = "#00274C"; // official Michigan navy -- header, footer/prediction strip, panel headers, all primary text
const MAIZE = "#FFCB05"; // tiny accent only -- never body text on cream
const SLATE = "#3D5166"; // secondary text, darkened for legibility at small sizes on cream
const NEUTRAL_TRACK = "#D7E0E8"; // light gray-blue: slider tracks, field-position track, pass-bar fill -- one neutral color, not team-coded
const NEUTRAL_SURFACE = "#E9E5DE"; // very light warm gray: secondary surfaces (THE READ)
const NEUTRAL_DARK = "#5C6570"; // neutral dark gray: slider center tick, EVEN marker/text
const LINE = "rgba(0,39,76,0.14)"; // navy at low opacity -- the one border system, used everywhere
const CHIP_BORDER = "rgba(0,39,76,0.22)";

// ---- the grid ----
//
// Canvas is 1600 wide with a 40px margin each side (1520px usable,
// centered on x=800). Every zone below divides that same 1520px into
// fixed pieces that sum exactly, so nothing is flex-computed and
// nothing needs an eyeballed nudge to line up.

const CANVAS_WIDTH = 1600;

// Top section: TEAM | gap | FIELD POSITION | gap | TEAM.
// 426 + 27 + 614 + 27 + 426 = 1520.
const TOP_SIDE_WIDTH = 426;
const TOP_CENTER_WIDTH = 614;
const TOP_GAP = 27;

// Matchup panel row: PANEL | gap | PANEL.
// 746 + 28 + 746 = 1520.
const PANEL_WIDTH = 746;
const PANEL_GAP = 28;
const PANEL_H_PADDING = 22;

// Row grid inside a panel, shared by MatchupRow AND the owner-label/
// legend header rows above the rows, so a rank chip and everything
// that labels it share one center axis:
// 80 + 14 + 300 + 14 + 80 + 14 + 200 = 702, exactly PANEL_WIDTH minus
// its own left+right padding (746 - 44).
const ROW_OFFENSE_COL = 80;
const ROW_METRIC_COL = 300;
const ROW_DEFENSE_COL = 80;
const ROW_EDGE_COL = 200;
const ROW_GAP = 14;
const ROW_HEIGHT = 48;

// Centers of the two rank columns, in the row grid's own coordinate
// space (relative to the panel's padded content area) -- used to plant
// the owner labels in Header row and MatchupRow's rank chips on the
// same axis despite the label text being wider than an 80px column.
const OFFENSE_COL_CENTER = ROW_OFFENSE_COL / 2;
const DEFENSE_COL_CENTER = ROW_OFFENSE_COL + ROW_GAP + ROW_METRIC_COL + ROW_GAP + ROW_DEFENSE_COL / 2;

// Uses the real team abbreviation (e.g. "WMU", "OU") rather than a
// generic "OPP" -- an edge label must always explicitly name a team.
// Every row renders in the identical neutral style regardless of tier
// or which team it favors; wording ("MICH EDGE" vs "WMU EDGE" vs
// "EVEN") and the slider marker's position are what carry the meaning.
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

// The title/subtitle block never touches the logos' geometry at all --
// it's a plain width:100% column with its own centered text, so it's
// exactly centered on the canvas (x=800) no matter what the two logos
// look like. The logos are anchored independently, symmetric about the
// same 40px canvas margin used everywhere else (45 = 40 + 5px breathing
// room; the opponent logo's *right* edge sits the same 45px from the
// right canvas edge: 1600 - 45 = 1555).
const HEADER_HEIGHT = 98;
const MICH_LOGO_SIZE = 92;
const OPP_LOGO_SIZE = 100;

function Header({ data }: { data: MatchupGraphicData }) {
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "long", month: "long", day: "numeric", year: "numeric" });
  return (
    <div style={{ display: "flex", flexDirection: "column", position: "relative", width: "100%", height: HEADER_HEIGHT, backgroundColor: NAVY, justifyContent: "center" }}>
      <div style={{ display: "flex", position: "absolute", left: 45, top: (HEADER_HEIGHT - MICH_LOGO_SIZE) / 2 }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={teamLogoUrl(data.michigan.teamId, 256)} width={MICH_LOGO_SIZE} height={MICH_LOGO_SIZE} alt="" />
      </div>
      <div style={{ display: "flex", position: "absolute", left: 1555 - OPP_LOGO_SIZE, top: (HEADER_HEIGHT - OPP_LOGO_SIZE) / 2 }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={teamLogoUrl(data.opponent.teamId, 256)} width={OPP_LOGO_SIZE} height={OPP_LOGO_SIZE} alt="" />
      </div>
      <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "center", width: "100%", fontFamily: "Barlow Condensed", fontSize: 58, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>
          MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 28, fontWeight: 600, color: "rgba(245,240,230,0.55)", margin: "0 16px" }}>vs</span>{data.opponent.name.toUpperCase()}
        </div>
        <div style={{ display: "flex", justifyContent: "center", width: "100%", fontFamily: "Inter", fontSize: 18, fontWeight: 700, color: "rgba(245,240,230,0.8)", letterSpacing: 1.2, marginTop: 6 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
    </div>
  );
}

// One consistent size and style everywhere a rank appears -- the team
// snapshot and the matchup rows should read as the same typographic
// scale.
function RankChip({ rank }: { rank: number }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: OFFWHITE, border: `1.5px solid ${CHIP_BORDER}`, borderRadius: 6, padding: "4px 10px", minWidth: 52 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 23, fontWeight: 700, color: NAVY }}>{`#${rank}`}</span>
    </div>
  );
}

function VDivider({ height }: { height: number }) {
  return <div style={{ display: "flex", width: 1, height, backgroundColor: LINE }} />;
}

// ---- zone 2: team snapshot ----

// ONE component for both sides of the top section. Fixed 426px width
// (not flex:1) so its size is a grid fact, not a computed one; `side`
// is the only thing that differs between the two call sites -- same
// background, same padding, same typography, same rank sizes, same bar
// width on both sides.
function TeamSummary({ name, quality, runPct, side }: { name: string; quality: MatchupGraphicData["michigan"]["quality"]; runPct: number; side: "left" | "right" }) {
  const passPct = 100 - runPct;
  const alignItems = side === "left" ? "flex-start" : "flex-end";
  return (
    <div style={{ display: "flex", flexDirection: "column", width: TOP_SIDE_WIDTH, alignItems, justifyContent: "center", backgroundColor: CARD_CREAM, padding: "4px 22px" }}>
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
        <div style={{ display: "flex", width: `${runPct}%`, backgroundColor: NAVY }} />
        <div style={{ display: "flex", width: `${passPct}%`, backgroundColor: NEUTRAL_TRACK }} />
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
      {lift && <div style={{ display: "flex", width: 1, height: 15, backgroundColor: NEUTRAL_DARK, marginTop: 2 }} />}
      <span style={{ display: "flex", fontFamily: "Inter", fontSize: 15, fontWeight: 800, color: NAVY, marginTop: lift ? 2 : 8 }}>{abbr}</span>
    </div>
  );
}

// Every sub-element (title, ticks, track, readout, edge badge) is an
// explicit fixed width, and every one is centered via the parent's own
// alignItems:"center" -- so they all share the same horizontal center
// axis regardless of their own differing widths. This whole block is
// itself centered inside the 614px center column by TeamSnapshotZone,
// which is what lands it exactly on x=800.
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
      <div style={{ display: "flex", position: "relative", width: trackWidth, height: 3, backgroundColor: NEUTRAL_TRACK, marginTop: 8, marginBottom: 46 }}>
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

// Five explicit-width children (426 / 27 / 614 / 27 / 426) summing to
// exactly 1520px -- no flex:1, no gap shorthand standing in for a real
// number. The two dividers are their own 27px-wide slots so the gap
// itself always contains a visible, centered rule rather than blank
// flex spacing.
function TeamSnapshotZone({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "row" }}>
      <TeamSummary name={data.michigan.name} quality={data.michigan.quality} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} side="left" />
      <div style={{ display: "flex", width: TOP_GAP, alignItems: "center", justifyContent: "center" }}><VDivider height={150} /></div>
      <div style={{ display: "flex", width: TOP_CENTER_WIDTH, alignItems: "center", justifyContent: "center" }}>
        <FieldPositionMini data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />
      </div>
      <div style={{ display: "flex", width: TOP_GAP, alignItems: "center", justifyContent: "center" }}><VDivider height={150} /></div>
      <TeamSummary name={data.opponent.name} quality={data.opponent.quality} runPct={Math.round(data.opponent.tendencies.rushDecisionRate * 100)} side="right" />
    </div>
  );
}

// ---- zone 3: possession panels ----
//
// Inside each panel, offense always renders left and defense always
// renders right (row.offense / row.defense, never a "michigan"/
// "opponent" pair) -- that's what makes the two panels' internal layout
// identical while the teams occupying each side flip between them.

// `flip` mirrors the marker's position (row.score is always
// Michigan-centric, but which side is "offense" flips between panels)
// so "left side of the slider" always means "the team in the offense
// column," matching the rank chip beside it. This is an alignment fact,
// not a color one -- the track itself is a single neutral color.
//
// Fixed ROW_HEIGHT (not content-driven padding) so all five rows in
// both panels are pixel-identical in height, with no per-row margins --
// that's what guarantees row N sits at the same y in both panels.
function MatchupRow({ row, opponentAbbr, flip }: { row: PhaseEdgeRow; opponentAbbr: string; flip: boolean }) {
  const hasData = row.tier !== "insufficient";
  const rawMarkerPct = 50 - (row.score ?? 0) / 2;
  const markerPct = flip ? 100 - rawMarkerPct : rawMarkerPct;
  const markerColor = row.direction === "even" ? NEUTRAL_DARK : NAVY;
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: ROW_GAP, height: ROW_HEIGHT, borderTop: `1px solid ${LINE}` }}>
      <div style={{ display: "flex", width: ROW_OFFENSE_COL, justifyContent: "center" }}>
        <RankChip rank={row.offense.rank} />
      </div>
      <div style={{ display: "flex", flexDirection: "column", width: ROW_METRIC_COL }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: NAVY, letterSpacing: 0.2 }}>{row.label}</span>
        <div style={{ display: "flex", position: "relative", height: 4, marginTop: 5 }}>
          <div style={{ display: "flex", width: "100%", height: "100%", borderRadius: 2, backgroundColor: NEUTRAL_TRACK }} />
          <div style={{ display: "flex", position: "absolute", left: "50%", top: -4.5, width: 1, height: 13, backgroundColor: NEUTRAL_DARK }} />
          {hasData && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -5.5, width: 15, height: 15, borderRadius: 7.5, backgroundColor: markerColor, marginLeft: -7.5, border: `2px solid ${CARD_CREAM}` }} />}
        </div>
      </div>
      <div style={{ display: "flex", width: ROW_DEFENSE_COL, justifyContent: "center" }}>
        <RankChip rank={row.defense.rank} />
      </div>
      <div style={{ display: "flex", width: ROW_EDGE_COL, justifyContent: "center", backgroundColor: OFFWHITE, border: `1.5px solid ${CHIP_BORDER}`, borderRadius: 5, padding: "6px 8px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, letterSpacing: 0.2, color: NAVY, textAlign: "center" }}>{hasData ? shortVerdict(row.tier, row.direction, opponentAbbr) : "NO DATA"}</span>
      </div>
    </div>
  );
}

// Satori does not symmetrically center a flex child that's wider than
// its box -- confirmed by measuring rendered pixels, it anchors the
// child at the box's own start edge instead of splitting the overflow
// evenly. "MICHIGAN OFFENSE" is far wider than the 80px rank column it
// must be centered over, so centering it can't go through
// justifyContent on an 80px box. Instead this renders it in a
// comfortably wide (220px) box, absolutely positioned so *that box's*
// center -- not the rank column's box -- lands exactly on centerX; a
// wide box centering a smaller child is the ordinary, already-proven
// case, so the label's own text still centers correctly inside it.
function OwnerLabel({ label, centerX }: { label: string; centerX: number }) {
  const boxWidth = 220;
  return (
    <div style={{ display: "flex", position: "absolute", top: 0, left: centerX - boxWidth / 2, width: boxWidth, justifyContent: "center" }}>
      <span style={{ fontFamily: "Inter", fontSize: 12.5, fontWeight: 800, letterSpacing: 0.4, color: NAVY, whiteSpace: "nowrap" }}>{label}</span>
    </div>
  );
}

// ONE component for both possession panels. Everything -- which real
// team is "offense," the panel title, the owner labels, the legend, and
// the slider flip -- is derived from `phase` alone (offenseTeamName /
// defenseTeamName), so the two call sites differ only in which phase
// object they pass. Width, padding, header height, row height, and
// column widths are identical by construction, not by two copies
// happening to agree.
function MatchupPanel({ phase, opponentAbbr }: { phase: PossessionPhase; opponentAbbr: string }) {
  const flip = phase.defenseTeamName === "Michigan";
  const leftOwnerLabel = flip ? `${opponentAbbr} OFFENSE` : "MICHIGAN OFFENSE";
  const rightOwnerLabel = flip ? "MICHIGAN DEFENSE" : `${opponentAbbr} DEFENSE`;
  const legendLeft = flip ? opponentAbbr : "MICH";
  const legendRight = flip ? "MICH" : opponentAbbr;
  const title = `WHEN ${phase.offenseTeamName.toUpperCase()} HAS THE BALL`;
  return (
    // No overflow:hidden here -- the owner labels below are deliberately
    // wider than the narrow rank column they're centered over (see
    // OwnerLabel), and on the side closest to this panel's own edge that
    // overflow can extend past the panel's own boundary. overflow:hidden
    // would silently clip it. The header bar gets its own top-corner
    // radius instead, so the rounded-corner look doesn't depend on
    // clipping the panel's contents.
    <div style={{ display: "flex", flexDirection: "column", width: PANEL_WIDTH, border: `1px solid ${CHIP_BORDER}`, borderRadius: 8, backgroundColor: CARD_CREAM }}>
      <div style={{ display: "flex", width: "100%", backgroundColor: NAVY, padding: "8px 20px", justifyContent: "center", borderTopLeftRadius: 7, borderTopRightRadius: 7 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 25, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{title}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", padding: `4px ${PANEL_H_PADDING}px` }}>
        <div style={{ display: "flex", position: "relative", width: PANEL_WIDTH - PANEL_H_PADDING * 2, height: 14 }}>
          <OwnerLabel label={leftOwnerLabel} centerX={OFFENSE_COL_CENTER} />
          <OwnerLabel label={rightOwnerLabel} centerX={DEFENSE_COL_CENTER} />
        </div>
        {/* Same 4-column grid as MatchupRow below (via placeholder
            spacer divs), so the legend sits centered specifically over
            the metric column -- not the whole panel, which has a
            different, off-center midpoint once the rank/edge columns
            are unequal widths. */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: ROW_GAP, marginTop: 2 }}>
          <div style={{ display: "flex", width: ROW_OFFENSE_COL }} />
          <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", justifyContent: "center", width: ROW_METRIC_COL, gap: 10 }}>
            <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 0.4, color: SLATE }}>{legendLeft}</span>
            <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: SLATE }}>&larr;</span>
            <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, letterSpacing: 0.6, color: SLATE }}>EVEN</span>
            <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: SLATE }}>&rarr;</span>
            <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 0.4, color: SLATE }}>{legendRight}</span>
          </div>
          <div style={{ display: "flex", width: ROW_DEFENSE_COL }} />
          <div style={{ display: "flex", width: ROW_EDGE_COL }} />
        </div>
        {phase.rows.map((row) => <MatchupRow key={row.id} row={row} opponentAbbr={opponentAbbr} flip={flip} />)}
        {/* Fixed height (not minHeight) so both panels' READ boxes match
            exactly regardless of how long either generated sentence is --
            the amount of text must never change the box's own height. */}
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", height: 72, marginTop: 3, padding: "6px 16px", borderRadius: 6, backgroundColor: NEUTRAL_SURFACE }}>
          <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1, color: NAVY }}>THE READ</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: NAVY, marginTop: 2, lineHeight: 1.15 }}>{phase.whatItMeans}</span>
        </div>
      </div>
    </div>
  );
}

// ---- zone 4: prediction ----

// Three literal equal-width (flex:1) columns -- win probability / MFF
// projection / market -- rather than two flex regions hugging a
// content-sized center. This is what guarantees the projection's own
// center lands exactly on x=800 regardless of how wide its text is:
// with a symmetric 40px outer margin and three equal columns, column 2
// always spans the same fixed span of the strip no matter what it
// contains. The divider lines are a border on the center column itself
// (stretched to the row's full height) rather than a separately
// positioned/sized element -- they fall exactly on the column
// boundaries by construction.
function PredictionOutlookZone({ data }: { data: MatchupGraphicData }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", backgroundColor: NAVY, padding: "7px 40px 6px" }}>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "stretch", width: "100%" }}>
        <div style={{ display: "flex", flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center" }}>
          {data.prediction.type === "model" && data.prediction.winProbabilityPct != null && (
            <div style={{ display: "flex", flexDirection: "row", alignItems: "center" }}>
              <OutlineIconBadge><TrendGlyph /></OutlineIconBadge>
              <div style={{ display: "flex", flexDirection: "column", marginLeft: 12 }}>
                <span style={{ fontFamily: "Barlow Condensed", fontSize: 40, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{`${data.prediction.winProbabilityPct}%`}</span>
                <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, letterSpacing: 0.6, color: "rgba(245,240,230,0.65)" }}>WIN PROBABILITY</span>
              </div>
            </div>
          )}
        </div>
        <div style={{ display: "flex", flex: 1, flexDirection: "column", alignItems: "center", justifyContent: "center", borderLeft: "1px solid rgba(245,240,230,0.25)", borderRight: "1px solid rgba(245,240,230,0.25)" }}>
          {data.prediction.type === "model" && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, letterSpacing: 0.6, color: "rgba(245,240,230,0.65)" }}>MFF PROJECTION</span>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 52, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{data.prediction.marginLabel}</span>
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
        <div style={{ display: "flex", flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center" }}>
          {data.prediction.type === "model" && data.prediction.marketNote != null && (
            <div style={{ display: "flex", flexDirection: "row", alignItems: "center" }}>
              <OutlineIconBadge><DollarGlyph /></OutlineIconBadge>
              <div style={{ display: "flex", flexDirection: "column", marginLeft: 12 }}>
                <span style={{ fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{data.prediction.marketNote.replace("Market: ", "")}</span>
                <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, letterSpacing: 0.6, color: "rgba(245,240,230,0.65)" }}>MARKET</span>
              </div>
            </div>
          )}
        </div>
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
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "5px 40px", backgroundColor: CREAM }}>
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
    <div style={{ display: "flex", flexDirection: "column", width: CANVAS_WIDTH, backgroundColor: CREAM, fontFamily: "Inter", border: `1px solid ${LINE}` }}>
      {/* Maize appears only as tiny accents -- this seal line, one divider above THE BOTTOM LINE, one under the field-position edge badge, and the wordmark image. */}
      <div style={{ display: "flex", width: "100%", height: 3, backgroundColor: MAIZE }} />

      <Header data={data} />

      <div style={{ display: "flex", flexDirection: "column", padding: "3px 40px 0" }}>
        <TeamSnapshotZone data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "4px 0" }} />

        <div style={{ display: "flex", flexDirection: "row", gap: PANEL_GAP }}>
          <MatchupPanel phase={data.whenMichiganHasBall} opponentAbbr={oppAbbr} />
          <MatchupPanel phase={data.whenOpponentHasBall} opponentAbbr={oppAbbr} />
        </div>
      </div>

      <PredictionOutlookZone data={data} />
      <Footer />
    </div>
  );
}

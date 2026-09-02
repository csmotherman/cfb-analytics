// PRESENTATION layer: pure JSX -- a real Server Component now, not a
// Satori/next-og image tree. There is deliberately no team name,
// statistic, edge score, or sentence hardcoded anywhere in this file.
// Every word on the graphic comes from `data`, `teamAbbreviation`/
// `teamColors` (lib/team-colors.ts, keyed by teamId), or `teamLogoUrl`
// (lib/team-assets.ts, keyed by teamId) -- swap the gameId this is built
// from and the whole graphic becomes a different team's story with zero
// JSX changes.
//
// Rendered inside FitToScreen (app/matchup-graphic/[gameId]/
// FitToScreen.tsx), which scales this component's natural size to fill
// the viewport with no page scrolling. That's what freed this rewrite
// from the old fixed-900px-tall-canvas budget: there's no hard height
// ceiling to fit under anymore, just a natural width (1600px, "wide
// layout") and whatever height the content actually needs.
//
// Every zone is still built on one strict grid, symmetric around the
// canvas's own center, using real CSS Grid now instead of flexbox
// standing in for it. The two "mirrored" halves of the graphic (Michigan
// panel/opponent panel, left team/right team, left/right prediction
// blocks) are never two independently-styled JSX blocks -- each pair is
// ONE component (TeamSummary, MatchupPanel) rendered twice with only a
// side/data prop differing, so the two halves are geometrically
// identical by construction and can't drift out of alignment with each
// other as opponents change.
//
// Color system: mostly warm cream/off-white, not navy -- navy is
// reserved for Michigan identity and emphasis (the header's logo block,
// "when Michigan has the ball," the MFF projection card), maize is a
// tiny accent only. One restrained, dark accent color per opponent
// (their real brand primary, already hand-picked in team-colors.ts)
// shows up in a few identity-carrying spots -- the title, the run bar,
// "when [opponent] has the ball," slider markers/edge chips favoring
// them -- never as a wholesale panel recolor. That one dynamic value is
// set as a CSS custom property on the root canvas element and read by
// the stylesheet wherever it's needed, rather than threaded through
// inline styles on every element that uses it.
import type { CSSProperties } from "react";
import { Barlow_Condensed, Inter } from "next/font/google";
import { teamLogoUrl } from "../team-assets";
import { teamAbbreviation, teamColors } from "../team-colors";
import type { MatchupGraphicData, PhaseEdgeRow, PossessionPhase } from "./types";
import styles from "./presentation.module.css";

const displayFont = Barlow_Condensed({ subsets: ["latin"], weight: "700", variable: "--mg-display", display: "swap" });
const bodyFont = Inter({ subsets: ["latin"], weight: ["600", "700", "800"], variable: "--mg-body", display: "swap" });

// Uses the real team abbreviation (e.g. "WMU", "OU") rather than a
// generic "OPP" -- an edge label must always explicitly name a team.
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
      <path d="M1.5 11.5 L6 6.5 L9 9 L14.5 2.5" stroke="#00274C" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <path d="M10.5 2.5 L14.5 2.5 L14.5 6.5" stroke="#00274C" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    </svg>
  );
}
function DollarGlyph() {
  return <span style={{ fontFamily: "var(--mg-body)", fontSize: 15, fontWeight: 800, color: "#00274C" }}>$</span>;
}

function OutlineIconBadge({ children }: { children: React.ReactNode }) {
  return <div className={styles.iconBadge}>{children}</div>;
}

// ---- header (zone 1) ----

const MICH_LOGO_SIZE = 92;
const OPP_LOGO_SIZE = 100;

function Header({ data, opponentAccent }: { data: MatchupGraphicData; opponentAccent: string }) {
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "long", month: "long", day: "numeric", year: "numeric" });
  return (
    <div className={styles.header}>
      {/* Decorative only -- angled Michigan-navy block behind the
          Michigan logo. Absolutely positioned so it never affects the
          title's own centering below. */}
      <div className={styles.headerBlock} />
      <img className={`${styles.headerLogo} ${styles.headerLogoMich}`} src={teamLogoUrl(data.michigan.teamId, 256)} width={MICH_LOGO_SIZE} height={MICH_LOGO_SIZE} alt="Michigan logo" />
      <img className={`${styles.headerLogo} ${styles.headerLogoOpp}`} src={teamLogoUrl(data.opponent.teamId, 256)} width={OPP_LOGO_SIZE} height={OPP_LOGO_SIZE} alt={`${data.opponent.name} logo`} />
      <div className={styles.headerTitleWrap}>
        <div className={styles.headerTitle}>
          <span className={styles.headerTitleMich}>MICHIGAN</span>
          <span className={styles.headerTitleVs}>vs</span>
          <span className={styles.headerTitleOpp}>{data.opponent.name.toUpperCase()}</span>
        </div>
        <div className={styles.headerSubtitle}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
    </div>
  );
}

// One consistent size and style everywhere a rank appears -- the team
// snapshot and the matchup rows should read as the same typographic
// scale.
function RankChip({ rank }: { rank: number }) {
  return (
    <div className={styles.rankChip}>
      <span>{`#${rank}`}</span>
    </div>
  );
}

// ---- zone 2: team snapshot ----

// ONE component for both sides of the top section. The 426px column
// width is a real CSS Grid track (see .snapshot), not something this
// component sizes itself -- `side` and `runColor` are the only things
// that differ between the two call sites. `runColor` is the one place
// team identity shows up here: navy for Michigan's run bar, the
// opponent's own restrained accent for theirs -- everything else in
// this card (names, rank numbers) stays navy on both sides.
function TeamSummary({ name, quality, runPct, side, runColor }: { name: string; quality: MatchupGraphicData["michigan"]["quality"]; runPct: number; side: "left" | "right"; runColor: "mich" | "opp" }) {
  const passPct = 100 - runPct;
  return (
    <div className={`${styles.teamSummary} ${side === "left" ? styles.teamSummaryLeft : styles.teamSummaryRight}`}>
      <span className={styles.teamName}>{name.toUpperCase()}</span>
      <div className={styles.teamOverallRow}>
        <span className={styles.teamOverallRank}>{`#${quality.overall.rank}`}</span>
        <span className={styles.teamOverallLabel}>OVERALL</span>
      </div>
      <div className={styles.teamUnitsRow}>
        <div className={styles.teamUnit}>
          <RankChip rank={quality.offense.rank} />
          <span className={styles.teamUnitLabel}>OFFENSE</span>
        </div>
        <div className={styles.teamUnit}>
          <RankChip rank={quality.defense.rank} />
          <span className={styles.teamUnitLabel}>DEFENSE</span>
        </div>
      </div>
      <div className={styles.teamSplitRow}>
        <span className={styles.teamSplitPrimary}>{`${runPct}% RUN`}</span>
        <span className={styles.teamSplitSecondary}>{`${passPct}% PASS`}</span>
      </div>
      <div className={styles.teamBar}>
        <div className={runColor === "mich" ? styles.teamBarRun : styles.teamBarRunOpp} style={{ width: `${runPct}%` }} />
        <div className={styles.teamBarPass} style={{ width: `${passPct}%` }} />
      </div>
    </div>
  );
}

// Dot is the positioned root (fixed height, always on the track); the
// label is a normal-flow child below it, so a taller `lift` margin can
// never disturb the dot's own position.
function FieldPositionMarker({ abbr, leftPct, lift, mich }: { abbr: string; leftPct: number; lift: boolean; mich: boolean }) {
  return (
    <div className={styles.fieldPositionMarker} style={{ left: `${leftPct}%` }}>
      <div className={`${styles.fieldPositionDot} ${mich ? styles.fieldPositionDotMich : styles.fieldPositionDotOpp}`} />
      {lift && <div className={styles.fieldPositionLift} />}
      <span className={`${styles.fieldPositionLabel} ${lift ? styles.fieldPositionLabelLift : ""}`}>{abbr}</span>
    </div>
  );
}

// Every sub-element (title, ticks, track, readout, edge badge) is an
// explicit fixed width, and every one is centered via the parent's own
// alignItems:center -- so they all share the same horizontal center
// axis regardless of their own differing widths. This whole block sits
// inside the 614px center grid column (see .fieldPositionCell), which
// is what lands it on the canvas's true center.
function FieldPositionMini({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  const pct = (yardLine: number) => Math.max(3, Math.min(97, (yardLine / 50) * 100));
  const rawMichPct = mich ? pct(mich.ownYardLine) : null;
  const rawOppPct = opp ? pct(opp.ownYardLine) : null;
  const [michPct, oppPct] = rawMichPct != null && rawOppPct != null ? declutter(rawMichPct, rawOppPct, 8) : [rawMichPct, rawOppPct];
  const closeMarkers = michPct != null && oppPct != null && Math.abs(michPct - oppPct) < 11;
  return (
    <div className={styles.fieldPosition}>
      <span className={styles.fieldPositionTitle}>AVERAGE STARTING FIELD POSITION</span>
      <div className={styles.fieldPositionTicks}>
        {["20", "30", "40", "50"].map((t) => <span key={t}>{t}</span>)}
      </div>
      <div className={styles.fieldPositionTrack}>
        {[0, 33.3, 66.6, 100].map((t) => (
          <div key={t} className={styles.fieldPositionTrackTick} style={{ left: `${t}%` }} />
        ))}
        {mich && michPct != null && <FieldPositionMarker abbr={michAbbr} leftPct={michPct} lift={false} mich />}
        {opp && oppPct != null && <FieldPositionMarker abbr={oppAbbr} leftPct={oppPct} lift={closeMarkers} mich={false} />}
      </div>
      <div className={styles.fieldPositionReadout}>
        <div className={styles.fieldPositionReadoutSide}>
          <span className={styles.fieldPositionReadoutAbbr}>{michAbbr}</span>
          <span className={styles.fieldPositionReadoutValue}>{mich ? `OWN ${mich.ownYardLine.toFixed(1)}` : "—"}</span>
        </div>
        <div className={styles.fieldPositionDivider} />
        <div className={styles.fieldPositionReadoutSide}>
          <span className={styles.fieldPositionReadoutAbbr}>{oppAbbr}</span>
          <span className={styles.fieldPositionReadoutValue}>{opp ? `OWN ${opp.ownYardLine.toFixed(1)}` : "—"}</span>
        </div>
      </div>
      <div className={styles.fieldPositionEdge}>
        <div className={styles.fieldPositionEdgeBadge}>
          <span>{fieldPositionEdgeLabel(mich, opp, michAbbr, oppAbbr)}</span>
        </div>
        <div className={styles.fieldPositionEdgeUnderline} />
      </div>
    </div>
  );
}

// Real CSS Grid: TEAM | FIELD POSITION | TEAM, 426/614/426 with 27px
// gaps (see .snapshot) -- a grid fact, not something flex has to be
// coaxed into. The center cell's own left/right border is the divider,
// falling exactly on the gap boundary by construction.
function TeamSnapshotZone({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  return (
    <div className={styles.snapshot}>
      <TeamSummary name={data.michigan.name} quality={data.michigan.quality} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} side="left" runColor="mich" />
      <div className={styles.fieldPositionCell}>
        <FieldPositionMini data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />
      </div>
      <TeamSummary name={data.opponent.name} quality={data.opponent.quality} runPct={Math.round(data.opponent.tendencies.rushDecisionRate * 100)} side="right" runColor="opp" />
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
// column," matching the rank chip beside it. This is independent of
// `direction`'s own color (which team the row favors) -- flip only ever
// moves the marker left/right, direction only ever colors it.
function MatchupRow({ row, opponentAbbr, flip }: { row: PhaseEdgeRow; opponentAbbr: string; flip: boolean }) {
  const hasData = row.tier !== "insufficient";
  const rawMarkerPct = 50 - (row.score ?? 0) / 2;
  const markerPct = flip ? 100 - rawMarkerPct : rawMarkerPct;
  const markerClass = row.direction === "even" ? styles.markerEven : row.direction === "michigan" ? styles.markerMich : styles.markerOpp;
  const edgeClass = row.direction === "even" ? styles.edgeEven : row.direction === "michigan" ? styles.edgeMich : styles.edgeOpp;
  return (
    <div className={styles.row}>
      <div className={styles.rowRankCol}><RankChip rank={row.offense.rank} /></div>
      <div className={styles.rowMetric}>
        <span className={styles.rowMetricLabel}>{row.label}</span>
        <div className={styles.rowSlider}>
          <div className={styles.rowSliderTrack} />
          <div className={styles.rowSliderTick} />
          {hasData && <div className={`${styles.rowSliderMarker} ${markerClass}`} style={{ left: `${markerPct}%` }} />}
        </div>
      </div>
      <div className={styles.rowRankCol}><RankChip rank={row.defense.rank} /></div>
      <div className={`${styles.edgeChip} ${edgeClass}`}>
        <span>{hasData ? shortVerdict(row.tier, row.direction, opponentAbbr) : "NO DATA"}</span>
      </div>
    </div>
  );
}

// ONE component for both possession panels. Everything -- which real
// team is "offense," the panel title, the owner labels, the legend, the
// slider flip, and the header color -- is derived from `phase` (plus the
// one opponentAccent color read from the CSS custom property), so the
// two call sites differ only in which phase object they pass. Width,
// padding, header height, row height, and column widths are identical
// by construction, not by two copies happening to agree. The header
// itself is navy for "Michigan has the ball" and the opponent's own
// restrained accent for "the opponent has the ball" -- the one place a
// whole block, rather than a line of text or a chip, carries team color;
// the panel body stays cream either way.
function MatchupPanel({ phase, opponentAbbr }: { phase: PossessionPhase; opponentAbbr: string }) {
  const flip = phase.defenseTeamName === "Michigan";
  const leftOwnerLabel = `${phase.offenseTeamName.toUpperCase()} OFFENSE`;
  const rightOwnerLabel = `${phase.defenseTeamName.toUpperCase()} DEFENSE`;
  const legendLeft = flip ? opponentAbbr : "MICH";
  const legendRight = flip ? "MICH" : opponentAbbr;
  const title = `WHEN ${phase.offenseTeamName.toUpperCase()} HAS THE BALL`;
  return (
    <div className={styles.panel}>
      <div className={`${styles.panelHeader} ${flip ? styles.panelHeaderOpp : styles.panelHeaderMich}`}>
        <span>{title}</span>
      </div>
      <div className={styles.panelBody}>
        <div className={styles.ownerRow}>
          <span className={`${styles.ownerLabel} ${styles.ownerLabelOffense}`}>{leftOwnerLabel}</span>
          <span className={`${styles.ownerLabel} ${styles.ownerLabelDefense}`}>{rightOwnerLabel}</span>
        </div>
        <div className={styles.legendRow}>
          <div className={styles.legend}>
            <span className={styles.legendTeam}>{legendLeft}</span>
            <span className={styles.legendArrow}>&larr;</span>
            <span className={styles.legendEven}>EVEN</span>
            <span className={styles.legendArrow}>&rarr;</span>
            <span className={styles.legendTeam}>{legendRight}</span>
          </div>
        </div>
        {phase.rows.map((row) => <MatchupRow key={row.id} row={row} opponentAbbr={opponentAbbr} flip={flip} />)}
        <div className={styles.readBox}>
          <span className={styles.readLabel}>THE READ</span>
          <span className={styles.readText}>{phase.whatItMeans}</span>
        </div>
      </div>
    </div>
  );
}

// ---- zone 4: prediction ----

// Three literal equal-width (1fr) grid columns -- win probability / MFF
// projection / market. With a symmetric 40px outer padding and three
// equal columns, column 2's own center is a grid fact regardless of what
// it contains. The MFF projection lives in its own navy card nested
// inside column 2, rather than the whole strip being one navy band --
// that's what makes it read as the centerpiece instead of just more of
// the same background as everything around it.
function PredictionOutlookZone({ data }: { data: MatchupGraphicData }) {
  return (
    <>
      <div className={styles.predictionRow}>
        <div className={styles.predictionSide}>
          {data.prediction.type === "model" && data.prediction.winProbabilityPct != null && (
            <div className={styles.predictionBlock}>
              <OutlineIconBadge><TrendGlyph /></OutlineIconBadge>
              <div className={styles.predictionText}>
                <div className={styles.predictionValue}>{`${data.prediction.winProbabilityPct}%`}</div>
                <div className={styles.predictionLabel}>WIN PROBABILITY</div>
              </div>
            </div>
          )}
        </div>
        <div className={styles.predictionCenter}>
          <div className={styles.predictionCard}>
            {data.prediction.type === "model" && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <span className={styles.predictionCardEyebrow}>MFF PROJECTION</span>
                <span className={styles.predictionCardValue}>{data.prediction.marginLabel}</span>
              </div>
            )}
            {data.prediction.type === "market" && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <span className={styles.predictionCardMarket}>MARKET EXPECTATION</span>
                <span className={styles.predictionCardValue} style={{ marginTop: 2 }}>{data.prediction.spreadLabel}</span>
                <span className={styles.predictionCardMeta}>{data.prediction.book}</span>
              </div>
            )}
            {data.prediction.type === "unavailable" && <span className={styles.predictionUnavailable}>PREDICTION NOT AVAILABLE</span>}
          </div>
        </div>
        <div className={styles.predictionSide}>
          {data.prediction.type === "model" && data.prediction.marketNote != null && (
            <div className={styles.predictionBlock}>
              <OutlineIconBadge><DollarGlyph /></OutlineIconBadge>
              <div className={styles.predictionText}>
                <div className={styles.predictionValue} style={{ fontSize: 32 }}>{data.prediction.marketNote.replace("Market: ", "")}</div>
                <div className={styles.predictionLabel}>MARKET</div>
              </div>
            </div>
          )}
        </div>
      </div>
      {/* Full-bleed dark neutral strip, deliberately not navy -- distinct
          from every other dark surface on the graphic so it reads as a
          closing statement rather than another data block. */}
      <div className={styles.bottomLine}>
        <span className={styles.bottomLineLabel}>THE BOTTOM LINE</span>
        <span className={styles.bottomLineText}>{data.bottomLine}</span>
      </div>
    </>
  );
}

function Footer() {
  return (
    <div className={styles.footer}>
      <span className={styles.footerText}>2025 OPPONENT-ADJUSTED METRICS · FBS RANKS · MFF MODEL · MARKET LABELED SEPARATELY</span>
      <div className={styles.footerBrand}>
        <img src="https://michiganfootballfocus.com/brand/michigan-football-focus.png" width={54} height={18} alt="" />
        <span>MICHIGANFOOTBALLFOCUS.COM</span>
      </div>
    </div>
  );
}

// ---- root ----

export function MatchupGraphic({ data }: { data: MatchupGraphicData }) {
  const oppAbbr = teamAbbreviation(data.opponent.teamId, data.opponent.name);
  const michAbbr = "MICH";
  // The one restrained, dark accent used for opponent identity throughout
  // the template -- their real hand-picked brand primary from
  // team-colors.ts (falls back to a neutral gray for any team not in
  // that map), set once here and read everywhere via var(--mg-opponent-accent).
  const opponentAccent = teamColors(data.opponent.teamId).primary;
  const cssVars = { "--mg-opponent-accent": opponentAccent } as CSSProperties;

  return (
    <div className={`${styles.canvas} ${displayFont.variable} ${bodyFont.variable}`} style={cssVars}>
      <div className={styles.seal} />
      <Header data={data} opponentAccent={opponentAccent} />
      <TeamSnapshotZone data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />
      <div className={styles.panelRow}>
        <MatchupPanel phase={data.whenMichiganHasBall} opponentAbbr={oppAbbr} />
        <MatchupPanel phase={data.whenOpponentHasBall} opponentAbbr={oppAbbr} />
      </div>
      <PredictionOutlookZone data={data} />
      <Footer />
    </div>
  );
}

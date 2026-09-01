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
// Color system: cream page, Michigan navy for essentially all text and
// structure, maize used only as tiny accents (a seal line, one divider,
// the wordmark). Deliberately neutral otherwise -- no opponent-specific
// color anywhere in the base template (see git log: an earlier round
// gave the opponent a fixed warm-brown family, which read well for one
// matchup but wasn't actually template-neutral -- a team with no natural
// "warm" association would make the choice look arbitrary). Opponent
// identity comes from the real logo and the team name text, not paint.
// No quality-based rank coloring either.
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

// Logos are wrapped in equal-width boxes (the wider of the two real
// logo widths) so the title block sits at the true center of the
// 1600px canvas regardless of the two teams' logos having different
// natural widths -- a plain space-between row would visually shift the
// title toward whichever side has the narrower logo.
const HEADER_LOGO_SLOT = 120;

function Header({ data }: { data: MatchupGraphicData }) {
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "long", month: "long", day: "numeric", year: "numeric" });
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", backgroundColor: NAVY, padding: "3px 40px" }}>
      <div style={{ display: "flex", width: HEADER_LOGO_SLOT, justifyContent: "flex-start" }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={teamLogoUrl(data.michigan.teamId, 256)} width={92} height={92} alt="" />
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 58, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>
          MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 28, fontWeight: 600, color: "rgba(245,240,230,0.55)", margin: "0 16px" }}>vs</span>{data.opponent.name.toUpperCase()}
        </div>
        <div style={{ display: "flex", fontFamily: "Inter", fontSize: 18, fontWeight: 700, color: "rgba(245,240,230,0.8)", letterSpacing: 1.2, marginTop: 6 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
      <div style={{ display: "flex", width: HEADER_LOGO_SLOT, justifyContent: "flex-end" }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={teamLogoUrl(data.opponent.teamId, 256)} width={100} height={100} alt="" />
      </div>
    </div>
  );
}

// One consistent size and style everywhere a rank appears -- the team
// snapshot and the matchup rows should read as the same typographic
// scale.
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

// Identical background, identical run/pass colors, identical padding
// for both teams -- the only variable between the two call sites is
// which data and which side text aligns to.
function TeamColumn({ name, quality, runPct, align }: { name: string; quality: MatchupGraphicData["michigan"]["quality"]; runPct: number; align: "left" | "right" }) {
  const passPct = 100 - runPct;
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, alignItems: align === "left" ? "flex-start" : "flex-end", justifyContent: "center", backgroundColor: CARD_CREAM, padding: "4px 22px" }}>
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
// axis regardless of their own differing widths.
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

// Both TeamColumns are flex:1 (equal width by construction) with
// identical divider spacing on each side of the center column, so the
// field-position block is centered in the true middle third of the row.
function TeamSnapshotZone({ data, michAbbr, oppAbbr }: { data: MatchupGraphicData; michAbbr: string; oppAbbr: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "stretch", justifyContent: "space-between" }}>
      <TeamColumn name={data.michigan.name} quality={data.michigan.quality} runPct={Math.round(data.michigan.tendencies.rushDecisionRate * 100)} align="left" />
      <div style={{ display: "flex", alignItems: "center", padding: "0 26px" }}><VDivider height={150} /></div>
      <div style={{ display: "flex", alignItems: "center" }}><FieldPositionMini data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} /></div>
      <div style={{ display: "flex", alignItems: "center", padding: "0 26px" }}><VDivider height={150} /></div>
      <TeamColumn name={data.opponent.name} quality={data.opponent.quality} runPct={Math.round(data.opponent.tendencies.rushDecisionRate * 100)} align="right" />
    </div>
  );
}

// ---- zone 3: possession panels ----
//
// Inside each panel, offense always renders left and defense always
// renders right (row.offense / row.defense, never a "michigan"/
// "opponent" pair) -- that's what makes the two panels' internal layout
// identical while the teams occupying each side flip between them.
//
// The four column widths below (96 / flex:1 / 96 / 168) are shared by
// PhaseRow AND the ownership-header row in PhasePanel, so a rank chip
// and the label naming who owns it sit on the exact same center axis.
// The owner labels use the same MICH/{abbr} short form as the legend
// and edge chips rather than "MICHIGAN OFFENSE" -- Satori doesn't
// symmetrically center a flex child wider than its box (confirmed by
// measuring rendered pixels), it anchors at the box's own start edge,
// so a label much wider than this 96px column would read as
// left-shifted relative to the rank chip actually centered in it.
const RANK_COL = 96;
const EDGE_COL = 168;
const ROW_GAP = 14;

// `flip` mirrors the marker's position (row.score is always
// Michigan-centric, but which side is "offense" flips between panels)
// so "left side of the slider" always means "the team in the offense
// column," matching the rank chip beside it. This is an alignment fact,
// not a color one -- the track itself is a single neutral color now.
function PhaseRow({ row, opponentAbbr, flip }: { row: PhaseEdgeRow; opponentAbbr: string; flip: boolean }) {
  const hasData = row.tier !== "insufficient";
  const rawMarkerPct = 50 - (row.score ?? 0) / 2;
  const markerPct = flip ? 100 - rawMarkerPct : rawMarkerPct;
  const markerColor = row.direction === "even" ? NEUTRAL_DARK : NAVY;
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: ROW_GAP, padding: "4px 0", borderTop: `1px solid ${LINE}` }}>
      <div style={{ display: "flex", width: RANK_COL, justifyContent: "center" }}>
        <RankChip rank={row.offense.rank} />
      </div>
      <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: NAVY, letterSpacing: 0.2 }}>{row.label}</span>
        <div style={{ display: "flex", position: "relative", height: 4, marginTop: 5 }}>
          <div style={{ display: "flex", width: "100%", height: "100%", borderRadius: 2, backgroundColor: NEUTRAL_TRACK }} />
          <div style={{ display: "flex", position: "absolute", left: "50%", top: -4.5, width: 1, height: 13, backgroundColor: NEUTRAL_DARK }} />
          {hasData && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -5.5, width: 15, height: 15, borderRadius: 7.5, backgroundColor: markerColor, marginLeft: -7.5, border: `2px solid ${CARD_CREAM}` }} />}
        </div>
      </div>
      <div style={{ display: "flex", width: RANK_COL, justifyContent: "center" }}>
        <RankChip rank={row.defense.rank} />
      </div>
      <div style={{ display: "flex", width: EDGE_COL, justifyContent: "center", backgroundColor: OFFWHITE, border: `1.5px solid ${CHIP_BORDER}`, borderRadius: 5, padding: "6px 8px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, letterSpacing: 0.2, color: NAVY, textAlign: "center" }}>{hasData ? shortVerdict(row.tier, row.direction, opponentAbbr) : "NO DATA"}</span>
      </div>
    </div>
  );
}

// `orientation` is the one piece of panel-role data everything else in
// this component derives from -- which real team sits in the offense
// column (left) here is the only thing that differs between the two
// panels, so column labels, the legend, and the slider's flip all read
// off this one flag rather than being written twice by hand.
function PhasePanel({ phase, title, opponentAbbr, orientation }: { phase: PossessionPhase; title: string; opponentAbbr: string; orientation: "michigan-left" | "opponent-left" }) {
  const flip = orientation === "opponent-left";
  const leftOwnerLabel = flip ? `${opponentAbbr} OFFENSE` : "MICH OFFENSE";
  const rightOwnerLabel = flip ? "MICH DEFENSE" : `${opponentAbbr} DEFENSE`;
  const legendLeft = flip ? opponentAbbr : "MICH";
  const legendRight = flip ? "MICH" : opponentAbbr;
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, border: `1px solid ${CHIP_BORDER}`, borderRadius: 8, overflow: "hidden", backgroundColor: CARD_CREAM }}>
      <div style={{ display: "flex", backgroundColor: NAVY, padding: "8px 20px", justifyContent: "center" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 25, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{title}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", padding: "6px 22px 6px" }}>
        {/* Same 4-column widths as PhaseRow below, so each owner label's
            center lands exactly on its rank column's center. Text is
            allowed to overflow its 96px anchor symmetrically (no
            overflow:hidden) rather than being confined to it -- "MICHIGAN
            OFFENSE" is wider than 96px, but its *center* still matches
            the rank chip's center, which is the actual goal. */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: ROW_GAP }}>
          <div style={{ display: "flex", width: RANK_COL, justifyContent: "center" }}>
            <span style={{ fontFamily: "Inter", fontSize: 12.5, fontWeight: 800, letterSpacing: 0.4, color: NAVY, whiteSpace: "nowrap" }}>{leftOwnerLabel}</span>
          </div>
          <div style={{ display: "flex", flex: 1 }} />
          <div style={{ display: "flex", width: RANK_COL, justifyContent: "center" }}>
            <span style={{ fontFamily: "Inter", fontSize: 12.5, fontWeight: 800, letterSpacing: 0.4, color: NAVY, whiteSpace: "nowrap" }}>{rightOwnerLabel}</span>
          </div>
          <div style={{ display: "flex", width: EDGE_COL }} />
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "baseline", justifyContent: "center", gap: 10, marginTop: 3 }}>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 0.4, color: SLATE }}>{legendLeft}</span>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: SLATE }}>&larr;</span>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, letterSpacing: 0.6, color: SLATE }}>EVEN</span>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: SLATE }}>&rarr;</span>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 0.4, color: SLATE }}>{legendRight}</span>
        </div>
        {phase.rows.map((row) => <PhaseRow key={row.id} row={row} opponentAbbr={opponentAbbr} flip={flip} />)}
        {/* Fixed minHeight so both panels' READ boxes match exactly --
            the two sentences are genuinely different lengths (one
            regularly wraps to two lines, one doesn't), so equal padding
            alone doesn't guarantee equal height. */}
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", minHeight: 74, marginTop: 4, padding: "6px 16px", borderRadius: 6, backgroundColor: NEUTRAL_SURFACE }}>
          <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1, color: NAVY }}>THE READ</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: NAVY, marginTop: 2, lineHeight: 1.15 }}>{phase.whatItMeans}</span>
        </div>
      </div>
    </div>
  );
}

// ---- zone 4: prediction ----

// Left and right blocks live in equal-width flex:1 regions (content
// justified toward the center, so each block visually hugs the
// projection in the middle) -- this guarantees the MFF projection sits
// at the strip's true horizontal center regardless of how wide the win
// probability and market blocks are, the same fix as the header logos.
function PredictionOutlookZone({ data }: { data: MatchupGraphicData }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", backgroundColor: NAVY, padding: "10px 40px 8px" }}>
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", width: "100%" }}>
        <div style={{ display: "flex", flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "flex-end" }}>
          {data.prediction.type === "model" && data.prediction.winProbabilityPct != null && (
            <div style={{ display: "flex", flexDirection: "row", alignItems: "center" }}>
              <OutlineIconBadge><TrendGlyph /></OutlineIconBadge>
              <div style={{ display: "flex", flexDirection: "column", marginLeft: 12 }}>
                <span style={{ fontFamily: "Barlow Condensed", fontSize: 40, fontWeight: 700, color: CREAM_TEXT, lineHeight: 1 }}>{`${data.prediction.winProbabilityPct}%`}</span>
                <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, letterSpacing: 0.6, color: "rgba(245,240,230,0.65)" }}>WIN PROBABILITY</span>
              </div>
              <div style={{ display: "flex", width: 1, height: 46, backgroundColor: "rgba(245,240,230,0.25)", marginLeft: 40 }} />
            </div>
          )}
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
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
        <div style={{ display: "flex", flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "flex-start" }}>
          {data.prediction.type === "model" && data.prediction.marketNote != null && (
            <div style={{ display: "flex", flexDirection: "row", alignItems: "center" }}>
              <div style={{ display: "flex", width: 1, height: 46, backgroundColor: "rgba(245,240,230,0.25)", marginRight: 40 }} />
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

      <div style={{ display: "flex", flexDirection: "column", padding: "3px 40px 0" }}>
        <TeamSnapshotZone data={data} michAbbr={michAbbr} oppAbbr={oppAbbr} />

        <div style={{ display: "flex", width: "100%", height: 2, backgroundColor: NAVY, margin: "6px 0" }} />

        <div style={{ display: "flex", flexDirection: "row", gap: 28 }}>
          <PhasePanel
            phase={data.whenMichiganHasBall}
            title="WHEN MICHIGAN HAS THE BALL"
            orientation="michigan-left"
            opponentAbbr={oppAbbr}
          />
          <PhasePanel
            phase={data.whenOpponentHasBall}
            title={`WHEN ${data.opponent.name.toUpperCase()} HAS THE BALL`}
            orientation="opponent-left"
            opponentAbbr={oppAbbr}
          />
        </div>
      </div>

      <PredictionOutlookZone data={data} />
      <Footer />
    </div>
  );
}

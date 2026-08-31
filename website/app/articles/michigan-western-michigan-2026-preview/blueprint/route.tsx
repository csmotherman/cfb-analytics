import { ImageResponse } from "next/og";
import { teamLogoUrl } from "../../../../lib/team-assets";
import { michiganWesternMichigan2026 as data } from "../../../../lib/michigan/matchup-preview-data";
import type { CompareRow, CompareValue } from "../../../../lib/michigan/matchup-preview-data";

export const runtime = "edge";

const BG = "#071421";
const BG_2 = "#0a1c2c";
const PANEL = "#0c2033";
const LINE = "rgba(255,255,255,0.09)";
const MAIZE = "#ffcb05";
const MAIZE_SOFT = "rgba(255,203,5,0.28)";
// Derived from Western Michigan's own CFBD-sourced brand colors
// (lib/team-colors.ts: #532E1F brown, #F1C500 gold), warmed toward orange
// and lightened: the raw brown is too dark to read as text on this
// near-black background, and an even blend sits too close to MAIZE's own
// hue to stay visually distinct next to it.
const BRONZE = "#d9843f";
const WHITE = "#f5f7fa";
const DIM = "#9aa9b8";
const FAINT = "#6f8192";
const GOOD_A = "#3fae72";
const GOOD_B = "#5b9c72";
const NEUTRAL_A = "#3f6b6b";
const NEUTRAL_B = "#2e4054";
const BAD_A = "#8c5158";
const BAD_B = "#c0463f";

const RANK_BANDS: { max: number; bg: string; fg: string }[] = [
  { max: 10, bg: GOOD_A, fg: "#06170f" },
  { max: 25, bg: GOOD_B, fg: "#0a1a10" },
  { max: 50, bg: NEUTRAL_A, fg: "#eaf3f2" },
  { max: 80, bg: NEUTRAL_B, fg: "#dbe4ee" },
  { max: 100, bg: BAD_A, fg: "#f7e9ea" },
  { max: Infinity, bg: BAD_B, fg: "#fdecea" },
];
function rankBand(rank: number) {
  return RANK_BANDS.find((b) => rank <= b.max) ?? RANK_BANDS[RANK_BANDS.length - 1];
}

async function loadGoogleFont(family: string, weight: number): Promise<ArrayBuffer | null> {
  try {
    const css = await (await fetch(`https://fonts.googleapis.com/css2?family=${encodeURIComponent(family)}:wght@${weight}`)).text();
    const match = css.match(/src: url\(([^)]+)\) format\('(?:opentype|truetype)'\)/);
    if (!match) return null;
    const res = await fetch(match[1]);
    return res.status === 200 ? await res.arrayBuffer() : null;
  } catch {
    return null;
  }
}

function CornerMark({ top, left }: { top: boolean; left: boolean }) {
  const legLen = 16;
  const thick = 2;
  const vSide: Record<string, number> = top ? { top: 0 } : { bottom: 0 };
  const hSide: Record<string, number> = left ? { left: 0 } : { right: 0 };
  return (
    <div style={{ display: "flex", position: "absolute", ...vSide, ...hSide, width: legLen, height: legLen }}>
      <div style={{ display: "flex", position: "absolute", ...vSide, ...hSide, width: legLen, height: thick, backgroundColor: MAIZE, opacity: 0.65 }} />
      <div style={{ display: "flex", position: "absolute", ...vSide, ...hSide, width: thick, height: legLen, backgroundColor: MAIZE, opacity: 0.65 }} />
    </div>
  );
}

// Rank badges are the ONLY quality-heatmap encoding left on this graphic
// (no per-row bar anymore -- one signal, not three).
function RankBadge({ rank, big = false }: { rank: number; big?: boolean }) {
  const band = rankBand(rank);
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minWidth: big ? 44 : 40, height: big ? 26 : 24, padding: "0 6px", borderRadius: 5, backgroundColor: band.bg }}>
      <span style={{ fontFamily: "Inter", fontSize: big ? 13 : 12, fontWeight: 700, color: band.fg }}>{`#${rank}`}</span>
    </div>
  );
}

function ValueRank({ v, align, dim }: { v: CompareValue; align: "left" | "right"; dim?: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 9, width: 226, justifyContent: align === "left" ? "flex-start" : "flex-end" }}>
      <span style={{ fontFamily: "Inter", fontSize: dim ? 14 : 16, fontWeight: 700, color: dim ? DIM : WHITE, width: 66, textAlign: align }}>{v.value}</span>
      <RankBadge rank={v.rank} big={!dim} />
    </div>
  );
}

// The metric-name column gets its own faint background band across every
// row so the five-column structure (MICH VALUE | RANK | METRIC | RANK |
// WMU VALUE) reads as real table columns instead of floating text.
function TableRow({ row, primary }: { row: CompareRow; primary: boolean }) {
  const research = !primary;
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", height: primary ? 29 : 20, borderBottom: `1px solid ${LINE}`, opacity: research ? 0.72 : 1 }}>
      <ValueRank v={row.michigan} align="left" dim={research} />
      <div style={{ display: "flex", flex: 1, alignItems: "center", justifyContent: "center", gap: 6, height: "100%", backgroundColor: "rgba(255,255,255,0.032)" }}>
        <span style={{ fontFamily: "Inter", fontSize: primary ? 13 : 11, fontWeight: 700, color: research ? DIM : WHITE, letterSpacing: 0.4, textTransform: "uppercase" }}>{row.metric}</span>
        {research && <span style={{ display: "flex", fontFamily: "Inter", fontSize: 8.5, fontWeight: 800, color: FAINT, border: `1px solid ${LINE}`, borderRadius: 3, padding: "1px 4px" }}>R</span>}
      </div>
      <ValueRank v={row.opponent} align="right" dim={research} />
    </div>
  );
}

function MatchupBanner({ leftTeam, leftColor, rightTeam, rightColor, side }: { leftTeam: string; leftColor: string; rightTeam: string; rightColor: string; side: "OFFENSE" | "DEFENSE" }) {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 12, padding: "4px 0", marginTop: 6 }}>
      <div style={{ display: "flex", flex: 1, height: 1, backgroundImage: `linear-gradient(90deg, transparent, ${LINE})` }} />
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: leftColor, whiteSpace: "nowrap" }}>{`${leftTeam} ${side}`}</span>
      <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: FAINT }}>vs</span>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: rightColor, whiteSpace: "nowrap" }}>{`${rightTeam} ${side === "OFFENSE" ? "DEFENSE" : "OFFENSE"}`}</span>
      <div style={{ display: "flex", flex: 1, height: 1, backgroundImage: `linear-gradient(90deg, ${LINE}, transparent)` }} />
    </div>
  );
}

function TableBlock({ leftTeam, leftColor, rightTeam, rightColor, side, rows }: { leftTeam: string; leftColor: string; rightTeam: string; rightColor: string; side: "OFFENSE" | "DEFENSE"; rows: CompareRow[] }) {
  const primaryRows = rows.filter((r) => r.tier !== "research");
  const researchRows = rows.filter((r) => r.tier === "research");
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
      <MatchupBanner leftTeam={leftTeam} leftColor={leftColor} rightTeam={rightTeam} rightColor={rightColor} side={side} />
      {primaryRows.map((r) => <TableRow row={r} key={r.metric} primary />)}
      <div style={{ display: "flex", height: 4 }} />
      {researchRows.map((r) => <TableRow row={r} key={r.metric} primary={false} />)}
    </div>
  );
}

// Rank is the focal number (casual-reader friendly); the /100 score is
// secondary support, stacked underneath at a fraction of the size.
function RankStat({ label, rank, score }: { label: string; rank: number; score: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", padding: "8px 0", borderTop: `1px solid ${LINE}` }}>
      <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, letterSpacing: 0.7, color: DIM }}>{label}</span>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 32, fontWeight: 700, color: WHITE, marginTop: 1 }}>{`#${rank}`}</span>
      <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: FAINT }}>{score}</span>
    </div>
  );
}

function ContinuitySplit({ offense, defense }: { offense: number; defense: number }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", padding: "8px 0", borderTop: `1px solid ${LINE}` }}>
      <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, letterSpacing: 0.5, color: DIM }}>ROSTER CONTINUITY</span>
      <span style={{ fontFamily: "Inter", fontSize: 9, fontWeight: 600, color: FAINT }}>MFF headcount audit</span>
      <div style={{ display: "flex", flexDirection: "row", gap: 22, marginTop: 5 }}>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 24, fontWeight: 700, color: WHITE }}>{`${offense.toFixed(0)}%`}</span>
          <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, color: DIM }}>OFFENSE</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 24, fontWeight: 700, color: WHITE }}>{`${defense.toFixed(0)}%`}</span>
          <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, color: DIM }}>DEFENSE</span>
        </div>
      </div>
    </div>
  );
}

function StyleStat({ pct, accent }: { pct: number; accent: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", padding: "8px 0", borderTop: `1px solid ${LINE}` }}>
      <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, letterSpacing: 0.7, color: DIM }}>STYLE</span>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 1 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: accent }}>{`${pct.toFixed(1)}%`}</span>
        <span style={{ display: "flex", fontFamily: "Inter", fontSize: 10, fontWeight: 800, color: accent, border: `1px solid ${accent}`, borderRadius: 4, padding: "1px 6px" }}>RUN</span>
      </div>
      <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 600, color: FAINT }}>rush decision rate</span>
    </div>
  );
}

function Rail({ name, teamColor, record, season }: { name: string; teamColor: string; record: string; season: typeof data.blueprint.michiganSeason }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: 248, borderRadius: 8, border: `1px solid ${LINE}`, backgroundColor: PANEL, overflow: "hidden" }}>
      <div style={{ display: "flex", width: "100%", height: 3, backgroundColor: teamColor }} />
      <div style={{ display: "flex", flexDirection: "column", padding: "10px 16px 4px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 23, fontWeight: 700, color: teamColor, letterSpacing: 0.2 }}>{name.toUpperCase()}</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: DIM, marginTop: 1 }}>{`2025: ${record}`}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", padding: "0 16px 12px" }}>
        <RankStat label="OFFENSE" rank={season.offense.rank} score={season.offense.value} />
        <RankStat label="DEFENSE" rank={season.defense.rank} score={season.defense.value} />
        <RankStat label="OVERALL" rank={season.overall.rank} score={season.overall.value} />
        <ContinuitySplit offense={season.offenseContinuityPct} defense={season.defenseContinuityPct} />
        <StyleStat pct={season.rushDecisionRatePct} accent={teamColor} />
      </div>
    </div>
  );
}

function FrontSevenChip({ label, pct }: { label: string; pct: number }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", width: 96, height: 58 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 30, fontWeight: 700, color: "#e2897f" }}>{`${pct}%`}</span>
      <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, letterSpacing: 0.4, color: DIM }}>{label}</span>
    </div>
  );
}

function ModelCell({ label, value, sub, accentTop, big }: { label: string; value: string; sub: string; accentTop: string; big?: boolean }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, alignItems: "center" }}>
      <div style={{ display: "flex", width: "60%", height: 2, backgroundColor: accentTop, borderRadius: 1, marginBottom: 8 }} />
      <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, letterSpacing: 0.9, color: DIM }}>{label}</span>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: big ? 43 : 38, fontWeight: 700, color: WHITE, marginTop: 3 }}>{value}</span>
      <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 600, color: DIM, marginTop: 2, textAlign: "center" }}>{sub}</span>
    </div>
  );
}

export async function GET() {
  const b = data.blueprint;
  const [barlowBold, interRegular, interSemibold, interBold] = await Promise.all([
    loadGoogleFont("Barlow Condensed", 700),
    loadGoogleFont("Inter", 400),
    loadGoogleFont("Inter", 600),
    loadGoogleFont("Inter", 700),
  ]);
  const fonts = [
    barlowBold && { name: "Barlow Condensed", data: barlowBold, weight: 700 as const, style: "normal" as const },
    interRegular && { name: "Inter", data: interRegular, weight: 400 as const, style: "normal" as const },
    interSemibold && { name: "Inter", data: interSemibold, weight: 600 as const, style: "normal" as const },
    interBold && { name: "Inter", data: interBold, weight: 700 as const, style: "normal" as const },
  ].filter((f): f is NonNullable<typeof f> => Boolean(f));

  const ext = data.continuity.opponentExternal;
  const dl = ext.defensePositions.find((p) => p.group === "DL")?.pct ?? 0;
  const lb = ext.defensePositions.find((p) => p.group === "LB")?.pct ?? 0;
  const db = ext.defensePositions.find((p) => p.group === "DB")?.pct ?? 0;

  return new ImageResponse(
    (
      <div style={{ display: "flex", position: "relative", flexDirection: "column", width: 1600, height: 990, backgroundImage: `linear-gradient(165deg, ${BG_2} 0%, ${BG} 55%)`, fontFamily: "Inter", border: `1px solid ${MAIZE_SOFT}` }}>
        <div style={{ display: "flex", width: "100%", height: 3, backgroundColor: MAIZE }} />
        <CornerMark top left /><CornerMark top left={false} /><CornerMark top={false} left /><CornerMark top={false} left={false} />

        {/* ZONE 1 -- header */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "8px 60px 4px" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={teamLogoUrl(data.michiganTeamId, 256)} width={98} height={98} alt="" />
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 54, fontWeight: 700, color: WHITE }}>MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 26, fontWeight: 600, color: FAINT, margin: "0 16px" }}>vs</span>WESTERN MICHIGAN</div>
            <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: MAIZE, letterSpacing: 2.6, marginTop: 6 }}>WEEK 1 · SATURDAY, SEPT. 5, 2026 · MICHIGAN STADIUM</div>
          </div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={teamLogoUrl(data.opponentTeamId, 256)} width={138} height={138} alt="" />
        </div>

        {/* ZONE 2 -- model strip */}
        <div style={{ display: "flex", flexDirection: "row", margin: "2px 60px 0", borderRadius: 8, border: `1px solid ${LINE}`, backgroundColor: PANEL, padding: "8px 8px 6px" }}>
          <ModelCell label="MFF WIN PROBABILITY" value={`${b.winProbMichiganPct}%`} sub="Michigan · 50,000-run sim" accentTop={MAIZE} />
          <ModelCell label="PROJECTED MARGIN" value={`MICH +${b.projectedMargin.split("by ")[1] ?? b.projectedMargin}`} sub={b.projectedMarginRange.replace("range: Michigan by ", "range +").replace(" to ", " to +")} accentTop={MAIZE} big />
          <ModelCell label="MARKET · BETMGM" value={data.market ? data.market.spread.replace("Michigan ", "MICH ") : "—"} sub={data.market ? `${data.market.winChance} implied · not our model` : ""} accentTop={FAINT} />
          <ModelCell label="COMPOSITE EDGE" value={data.compositeComparison.overallEdge} sub={`#${b.michiganSeason.overall.rank} Michigan vs #${b.opponentSeason.overall.rank} Western`} accentTop={MAIZE} />
        </div>

        {/* ZONE 3 + 4 -- rails + tables */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "flex-start", padding: "12px 60px 0", justifyContent: "space-between" }}>
          <Rail name="Michigan" teamColor={MAIZE} record={b.michiganRecord2025} season={b.michiganSeason} />
          <div style={{ display: "flex", flexDirection: "column", width: 954, padding: "0 18px" }}>
            <TableBlock leftTeam="MICHIGAN" leftColor={MAIZE} rightTeam="WESTERN MICHIGAN" rightColor={BRONZE} side="OFFENSE" rows={b.michiganOffenseVsOpponentDefense} />
            <TableBlock leftTeam="MICHIGAN" leftColor={MAIZE} rightTeam="WESTERN MICHIGAN" rightColor={BRONZE} side="DEFENSE" rows={b.opponentOffenseVsMichiganDefense} />
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 3 }}>
              <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 600, color: FAINT }}>R = research-tier opponent-adjusted metric (same model, not yet fully validated)</span>
            </div>
          </div>
          <Rail name="Western Michigan" teamColor={BRONZE} record={b.opponentRecord2025} season={b.opponentSeason} />
        </div>

        {/* ZONE 5 -- returning snap story, directly under the tables */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", margin: "10px 60px 0", padding: "10px 22px", borderRadius: 8, border: `1px solid ${BAD_B}55`, backgroundColor: PANEL }}>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 30, fontWeight: 700, color: WHITE }}>WESTERN&apos;S BIGGEST 2026 QUESTION</span>
            <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: DIM, marginTop: 2 }}>Western Michigan defensive continuity · CBS Sports, snap-weighted</span>
          </div>
          <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 22 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: WHITE }}>{`${ext.offenseOverallPct}%`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, color: DIM }}>OFFENSE</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: WHITE }}>{`${ext.defenseOverallPct}%`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, color: DIM }}>DEFENSE</span>
            </div>
            <div style={{ display: "flex", width: 1, height: 50, backgroundColor: LINE }} />
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "6px 12px", borderRadius: 8, border: `1px solid ${BAD_B}`, backgroundColor: "rgba(192,70,63,0.12)" }}>
              <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 800, letterSpacing: 0.6, color: "#e2897f", marginBottom: 2 }}>FRONT SEVEN</span>
              <div style={{ display: "flex", flexDirection: "row" }}>
                <FrontSevenChip label="DL" pct={dl} />
                <FrontSevenChip label="LB" pct={lb} />
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "6px 14px", borderRadius: 8, border: `1px solid ${GOOD_A}`, backgroundColor: "rgba(63,174,114,0.12)" }}>
              <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 800, letterSpacing: 0.6, color: GOOD_A, marginBottom: 2 }}>SECONDARY</span>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", width: 96, height: 58 }}>
                <span style={{ fontFamily: "Barlow Condensed", fontSize: 30, fontWeight: 700, color: GOOD_A }}>{`${db}%`}</span>
                <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, letterSpacing: 0.4, color: DIM }}>DB</span>
              </div>
            </div>
          </div>
        </div>

        {/* CTA + footer */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", margin: "10px 60px 0", padding: "12px 0 0", borderTop: `1px solid ${LINE}` }}>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 600, color: FAINT }}>2025 opponent-adjusted metrics · FBS ranks · MFF model · CBS returning snaps · Market: BetMGM</span>
          </div>
          <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 16 }}>
            <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 700, letterSpacing: 0.6, color: DIM }}>FULL WEEK 1 BREAKDOWN →</span>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: MAIZE }}>MICHIGANFOOTBALLFOCUS.COM</span>
          </div>
        </div>
        <div style={{ display: "flex", height: 14 }} />
      </div>
    ),
    { width: 1600, height: 990, fonts }
  );
}

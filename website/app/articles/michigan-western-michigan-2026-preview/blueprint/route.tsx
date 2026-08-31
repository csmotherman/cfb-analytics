import { ImageResponse } from "next/og";
import { teamLogoUrl } from "../../../../lib/team-assets";
import { michiganWesternMichigan2026 as data } from "../../../../lib/michigan/matchup-preview-data";
import type { CompareRow, CompareValue } from "../../../../lib/michigan/matchup-preview-data";

export const runtime = "edge";

const BG = "#071421";
const BG_2 = "#0a1c2c";
const PANEL = "#0b1e30";
const LINE = "rgba(255,255,255,0.09)";
const MAIZE = "#ffcb05";
// Derived from Western Michigan's own CFBD-sourced brand colors
// (lib/team-colors.ts: #532E1F brown, #F1C500 gold) -- a 50/50 blend of the
// two, not an invented hue, chosen because the raw brown is too dark to
// read as text on this near-black background.
const BRONZE = "#a2790f";
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

function RankBadge({ rank }: { rank: number }) {
  const band = rankBand(rank);
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minWidth: 36, height: 21, padding: "0 5px", borderRadius: 4, backgroundColor: band.bg }}>
      <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, color: band.fg }}>{`#${rank}`}</span>
    </div>
  );
}

function ValueRank({ v, align }: { v: CompareValue; align: "left" | "right" }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, width: 230, justifyContent: align === "left" ? "flex-start" : "flex-end" }}>
      <span style={{ fontFamily: "Inter", fontSize: 15, fontWeight: 700, color: WHITE, width: 68, textAlign: align }}>{v.value}</span>
      <RankBadge rank={v.rank} />
    </div>
  );
}

function TableRow({ row }: { row: CompareRow }) {
  const research = row.tier === "research";
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", height: 27, borderBottom: `1px solid ${LINE}`, opacity: research ? 0.74 : 1 }}>
      <ValueRank v={row.michigan} align="left" />
      <div style={{ display: "flex", flex: 1, alignItems: "center", justifyContent: "center", gap: 6 }}>
        <span style={{ fontFamily: "Inter", fontSize: 12.5, fontWeight: 700, color: research ? DIM : WHITE, letterSpacing: 0.4, textTransform: "uppercase" }}>{row.metric}</span>
        {research && <span style={{ display: "flex", fontFamily: "Inter", fontSize: 9, fontWeight: 800, color: FAINT, border: `1px solid ${LINE}`, borderRadius: 3, padding: "1px 4px" }}>R</span>}
      </div>
      <ValueRank v={row.opponent} align="right" />
    </div>
  );
}

function TableBlock({ leftTeam, leftColor, rightTeam, rightColor, side, rows }: { leftTeam: string; leftColor: string; rightTeam: string; rightColor: string; side: "OFFENSE" | "DEFENSE"; rows: CompareRow[] }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "center", gap: 8, padding: "5px 0", marginTop: 8, marginBottom: 1, borderTop: `1px solid ${LINE}`, borderBottom: `1px solid ${LINE}` }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: leftColor }}>{`${leftTeam} ${side === "OFFENSE" ? "OFFENSE" : "DEFENSE"}`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: FAINT }}>vs</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: rightColor }}>{`${rightTeam} ${side === "OFFENSE" ? "DEFENSE" : "OFFENSE"}`}</span>
      </div>
      {rows.map((r) => <TableRow row={r} key={r.metric} />)}
    </div>
  );
}

function RailRow({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", padding: "10px 0", borderTop: `1px solid ${LINE}` }}>
      <div style={{ display: "flex", fontFamily: "Inter", fontSize: 11, fontWeight: 700, letterSpacing: 0.8, color: DIM }}>{label}</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 3 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: WHITE }}>{value}</span>
        {sub && <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: DIM }}>{sub}</span>}
      </div>
    </div>
  );
}

function Rail({ name, teamColor, record, season }: { name: string; teamColor: string; record: string; season: typeof data.blueprint.michiganSeason }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: 250 }}>
      <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 25, fontWeight: 700, color: teamColor, letterSpacing: 0.3 }}>{name.toUpperCase()}</div>
      <div style={{ display: "flex", fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: DIM, marginTop: 2 }}>{`2025: ${record}`}</div>
      <RailRow label="OFFENSE RANK" value={`#${season.offense.rank}`} sub={season.offense.value} />
      <RailRow label="DEFENSE RANK" value={`#${season.defense.rank}`} sub={season.defense.value} />
      <RailRow label="OVERALL RANK" value={`#${season.overall.rank}`} sub={season.overall.value} />
      <RailRow label="ROSTER CONTINUITY · MFF HEADCOUNT AUDIT" value={`${season.offenseContinuityPct.toFixed(0)}% OFF`} sub={`${season.defenseContinuityPct.toFixed(0)}% DEF`} />
      <RailRow label="RUSH DECISION RATE" value={`${season.rushDecisionRatePct.toFixed(1)}%`} />
    </div>
  );
}

function SnapChip({ label, pct, tone }: { label: string; pct: number; tone: "good" | "bad" }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", width: 118, height: 64, borderRadius: 8, border: `1px solid ${tone === "good" ? GOOD_A : BAD_B}`, backgroundColor: tone === "good" ? "rgba(63,174,114,0.12)" : "rgba(192,70,63,0.12)" }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: tone === "good" ? GOOD_A : "#e08079" }}>{`${pct}%`}</span>
      <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 700, letterSpacing: 0.6, color: DIM, marginTop: 1 }}>{label}</span>
    </div>
  );
}

function ModelCell({ label, value, sub, accent }: { label: string; value: string; sub: string; accent?: boolean }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, alignItems: "center", padding: "12px 8px", borderRight: `1px solid ${LINE}` }}>
      <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, letterSpacing: 0.9, color: DIM }}>{label}</span>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: accent ? MAIZE : WHITE, marginTop: 4 }}>{value}</span>
      <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 600, color: DIM, marginTop: 2 }}>{sub}</span>
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
      <div style={{ display: "flex", flexDirection: "column", width: 1600, height: 1067, backgroundImage: `linear-gradient(165deg, ${BG_2} 0%, ${BG} 55%)`, fontFamily: "Inter" }}>
        <div style={{ display: "flex", width: "100%", height: 4, backgroundColor: MAIZE }} />

        {/* ZONE 1 -- header */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "22px 56px 16px" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={teamLogoUrl(data.michiganTeamId, 256)} width={96} height={96} alt="" />
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 46, fontWeight: 700, color: WHITE }}>MICHIGAN <span style={{ color: DIM, margin: "0 12px" }}>vs</span> WESTERN MICHIGAN</div>
            <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: MAIZE, letterSpacing: 2.4, marginTop: 6 }}>WEEK 1 · SATURDAY, SEPT. 5, 2026 · MICHIGAN STADIUM</div>
          </div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={teamLogoUrl(data.opponentTeamId, 256)} width={96} height={96} alt="" />
        </div>

        {/* ZONE 2 -- model strip */}
        <div style={{ display: "flex", flexDirection: "row", margin: "0 56px", borderRadius: 8, border: `1px solid ${LINE}`, backgroundColor: PANEL, overflow: "hidden" }}>
          <ModelCell label="MFF WIN PROBABILITY" value={`${b.winProbMichiganPct}%`} sub="Michigan · 50,000-run sim" accent />
          <ModelCell label="PROJECTED MARGIN" value={`MICH +${b.projectedMargin.split("by ")[1] ?? b.projectedMargin}`} sub={b.projectedMarginRange.replace("range: Michigan by ", "Model range: +").replace(" to ", " to +")} />
          <ModelCell label="MARKET · BETMGM" value={data.market ? data.market.spread.replace("Michigan ", "MICH ") : "—"} sub={data.market ? `${data.market.winChance} implied · not our model` : ""} />
          <div style={{ display: "flex", flexDirection: "column", flex: 1, alignItems: "center", padding: "12px 8px" }}>
            <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, letterSpacing: 0.9, color: DIM }}>COMPOSITE EDGE</span>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: MAIZE, marginTop: 4 }}>{data.compositeComparison.overallEdge}</span>
            <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 600, color: DIM, marginTop: 2 }}>{`#${b.michiganSeason.overall.rank} Michigan vs #${b.opponentSeason.overall.rank} Western`}</span>
          </div>
        </div>

        {/* ZONE 3 + 4 -- rails + tables */}
        <div style={{ display: "flex", flexDirection: "row", flex: 1, padding: "18px 56px 0", justifyContent: "space-between" }}>
          <Rail name="Michigan" teamColor={MAIZE} record={b.michiganRecord2025} season={b.michiganSeason} />
          <div style={{ display: "flex", flexDirection: "column", width: 960, padding: "0 20px" }}>
            <TableBlock leftTeam="MICHIGAN" leftColor={MAIZE} rightTeam="WESTERN MICHIGAN" rightColor={BRONZE} side="OFFENSE" rows={b.michiganOffenseVsOpponentDefense} />
            <TableBlock leftTeam="MICHIGAN" leftColor={MAIZE} rightTeam="WESTERN MICHIGAN" rightColor={BRONZE} side="DEFENSE" rows={b.opponentOffenseVsMichiganDefense} />
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 6 }}>
              <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 600, color: FAINT }}>R = research-tier opponent-adjusted metric (same model, not yet through full historical validation)</span>
            </div>
          </div>
          <Rail name="Western Michigan" teamColor={BRONZE} record={b.opponentRecord2025} season={b.opponentSeason} />
        </div>

        {/* ZONE 5 -- returning snap story */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", margin: "14px 56px 0", padding: "14px 22px", borderRadius: 8, border: `1px solid ${LINE}`, backgroundColor: PANEL }}>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, color: WHITE }}>WESTERN MICHIGAN RETURNING SNAP CONTINUITY</span>
            <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: DIM, marginTop: 2 }}>CBS Sports · snap-weighted, not our headcount audit</span>
          </div>
          <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 26 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 30, fontWeight: 700, color: WHITE }}>{`${ext.offenseOverallPct}%`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 700, color: DIM }}>OFFENSE</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 30, fontWeight: 700, color: WHITE }}>{`${ext.defenseOverallPct}%`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 700, color: DIM }}>DEFENSE</span>
            </div>
            <div style={{ display: "flex", width: 1, height: 44, backgroundColor: LINE }} />
            <SnapChip label="DEFENSIVE LINE" pct={dl} tone="bad" />
            <SnapChip label="LINEBACKER" pct={lb} tone="bad" />
            <SnapChip label="DEFENSIVE BACK" pct={db} tone="good" />
          </div>
        </div>

        {/* CTA + footer */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "16px 56px 20px" }}>
          <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 500, color: FAINT, maxWidth: 900 }}>Opponent-adjusted 2025 metrics · FBS national ranks · MFF roster continuity = official-roster headcount audit · Returning snaps via CBS Sports · Win probability &amp; margin = MFF preseason model · Market line is not our projection</span>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
            <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, letterSpacing: 1, color: DIM }}>FULL BREAKDOWN &amp; ANALYSIS</span>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: MAIZE }}>MICHIGANFOOTBALLFOCUS.COM</span>
          </div>
        </div>
      </div>
    ),
    { width: 1600, height: 1067, fonts }
  );
}

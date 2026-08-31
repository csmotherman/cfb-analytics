import { ImageResponse } from "next/og";
import { teamLogoUrl } from "../../../../lib/team-assets";
import { michiganWesternMichigan2026 as data } from "../../../../lib/michigan/matchup-preview-data";
import type { CompareRow, CompareValue } from "../../../../lib/michigan/matchup-preview-data";

export const runtime = "edge";

const BG_TOP = "#0c1c30";
const BG_BOTTOM = "#040a13";
const PANEL_LINE = "rgba(255,255,255,0.09)";
const MAIZE = "#ffcb05";
const WHITE = "#f4f7fb";
const DIM = "#8ea0b3";
const FAINT = "rgba(255,255,255,0.5)";
const GOOD = [114, 214, 163]; // --positive
const BAD = [255, 124, 134]; // --negative
const NEUTRAL = [26, 40, 56];

// Vercel/Next's documented pattern for pulling a real TTF out of Google
// Fonts server-side: requesting without a browser-like Accept header
// returns woff-free legacy font files that Satori (next/og's renderer) can
// actually embed, instead of the woff2 a normal browser would get.
async function loadGoogleFont(family: string, weight: number): Promise<ArrayBuffer | null> {
  try {
    const css = await (await fetch(`https://fonts.googleapis.com/css2?family=${encodeURIComponent(family)}:wght@${weight}`)).text();
    const match = css.match(/src: url\(([^)]+)\) format\('(?:opentype|truetype)'\)/);
    if (!match) return null;
    const res = await fetch(match[1]);
    if (res.status !== 200) return null;
    return await res.arrayBuffer();
  } catch {
    return null;
  }
}

function rankColor(rank: number): string {
  const t = Math.max(0, Math.min(1, (rank - 1) / 135));
  const lerp = (a: number, b: number, x: number) => Math.round(a + (b - a) * x);
  const [from, to, x] = t <= 0.5 ? [GOOD, NEUTRAL, t / 0.5] : [NEUTRAL, BAD, (t - 0.5) / 0.5];
  const rgb = [lerp(from[0], to[0], x), lerp(from[1], to[1], x), lerp(from[2], to[2], x)];
  return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
}

function Pill({ v }: { v: CompareValue }) {
  return (
    <div style={{ display: "flex", alignItems: "baseline", justifyContent: "center", gap: 7, width: 176, height: 42, borderRadius: 21, backgroundColor: rankColor(v.rank) }}>
      <span style={{ fontFamily: "Inter", fontSize: 19, fontWeight: 700, color: WHITE }}>{v.value}</span>
      <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: "rgba(244,247,251,0.72)" }}>{`#${v.rank}`}</span>
    </div>
  );
}

function CompareBlock({ heading, rows }: { heading: string; rows: CompareRow[] }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 22, marginBottom: 8 }}>
        <div style={{ display: "flex", width: 5, height: 5, borderRadius: 3, backgroundColor: MAIZE }} />
        <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, letterSpacing: 1.5, color: MAIZE }}>{heading.toUpperCase()}</div>
      </div>
      {rows.map((r) => (
        <div key={r.metric} style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "6px 0", borderBottom: `1px solid ${PANEL_LINE}` }}>
          <Pill v={r.michigan} />
          <div style={{ display: "flex", alignItems: "center", gap: 8, width: 300, justifyContent: "center" }}>
            <span style={{ fontFamily: "Inter", fontSize: 16, fontWeight: 600, color: r.tier === "research" ? DIM : WHITE }}>{r.metric}</span>
            {r.tier === "research" && <span style={{ display: "flex", fontFamily: "Inter", fontSize: 10, fontWeight: 700, color: FAINT, border: `1px solid ${PANEL_LINE}`, borderRadius: 4, padding: "2px 5px" }}>R</span>}
          </div>
          <Pill v={r.opponent} />
        </div>
      ))}
    </div>
  );
}

function SeasonRow({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", width: "100%", padding: "11px 0", borderTop: `1px solid ${PANEL_LINE}` }}>
      <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 700, letterSpacing: 0.5, color: DIM }}>{label}</div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
        <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 24, fontWeight: 700, color: WHITE }}>{value}</div>
        {sub && <div style={{ display: "flex", fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: DIM }}>{sub}</div>}
      </div>
    </div>
  );
}

function SeasonColumn({ name, teamId, season, record }: { name: string; teamId: number; season: typeof data.blueprint.michiganSeason; record: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: 268, alignItems: "center" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 108, height: 108, borderRadius: 54, backgroundColor: "rgba(255,255,255,0.04)", border: `1px solid ${PANEL_LINE}` }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={teamLogoUrl(teamId, 128)} width={72} height={72} alt="" />
      </div>
      <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: WHITE, marginTop: 12, letterSpacing: 0.5 }}>{name.toUpperCase()}</div>
      <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: DIM, marginBottom: 4 }}>{`2025: ${record}`}</div>
      <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
        <SeasonRow label="OFFENSE" value={`#${season.offense.rank}`} sub={season.offense.value} />
        <SeasonRow label="DEFENSE" value={`#${season.defense.rank}`} sub={season.defense.value} />
        <SeasonRow label="OVERALL" value={`#${season.overall.rank}`} sub={season.overall.value} />
        <SeasonRow label="ROSTER CONTINUITY" value={`${season.offenseContinuityPct.toFixed(0)}% / ${season.defenseContinuityPct.toFixed(0)}%`} sub="OFF / DEF" />
        <SeasonRow label="RUSH DECISION RATE" value={`${season.rushDecisionRatePct.toFixed(1)}%`} />
      </div>
    </div>
  );
}

function SummaryBlock({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "0 30px", borderLeft: `1px solid ${PANEL_LINE}` }}>
      <div style={{ display: "flex", fontFamily: "Inter", fontSize: 12, fontWeight: 700, letterSpacing: 1.3, color: DIM, marginBottom: 8 }}>{label.toUpperCase()}</div>
      {children}
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

  return new ImageResponse(
    (
      <div style={{ display: "flex", flexDirection: "column", width: 1600, height: 1470, backgroundImage: `linear-gradient(160deg, ${BG_TOP} 0%, ${BG_BOTTOM} 62%)`, fontFamily: "Inter" }}>
        <div style={{ display: "flex", width: "100%", height: 5, backgroundImage: `linear-gradient(90deg, ${MAIZE}, #b88a00)` }} />

        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "40px 64px 8px" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={teamLogoUrl(data.michiganTeamId, 256)} width={124} height={124} alt="" />
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 60, fontWeight: 700, color: WHITE, letterSpacing: 0 }}>MICHIGAN <span style={{ color: DIM, margin: "0 14px" }}>vs</span> WESTERN MICHIGAN</div>
            <div style={{ display: "flex", fontFamily: "Inter", fontSize: 16, fontWeight: 700, color: MAIZE, letterSpacing: 3, marginTop: 10 }}>WEEK 1 · SEPT. 5, 2026 · MICHIGAN STADIUM</div>
          </div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={teamLogoUrl(data.opponentTeamId, 256)} width={124} height={124} alt="" />
        </div>

        <div style={{ display: "flex", flexDirection: "row", alignItems: "flex-start", justifyContent: "center", padding: "24px 0 28px" }}>
          <SummaryBlock label="2025 record">
            <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: WHITE }}>{`${b.michiganRecord2025} — ${b.opponentRecord2025}`}</div>
          </SummaryBlock>
          <SummaryBlock label="Win probability · our model">
            <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: WHITE }}>{`${b.winProbMichiganPct}% — ${b.winProbOpponentPct}%`}</div>
          </SummaryBlock>
          <SummaryBlock label="Projected margin · our model">
            <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: WHITE }}>{b.projectedMargin}</div>
            <div style={{ display: "flex", fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: DIM, marginTop: 3 }}>{b.projectedMarginRange}</div>
          </SummaryBlock>
          <SummaryBlock label="Market · BetMGM, not our model">
            <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: WHITE }}>{data.market ? data.market.spread : "—"}</div>
            <div style={{ display: "flex", fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: DIM, marginTop: 3 }}>{data.market ? `${data.market.winChance} implied` : ""}</div>
          </SummaryBlock>
          <SummaryBlock label="Composite edge · validated model">
            <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 34, fontWeight: 700, color: MAIZE }}>{data.compositeComparison.overallEdge}</div>
            <div style={{ display: "flex", fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: DIM, marginTop: 3 }}>{`#${b.michiganSeason.overall.rank} vs #${b.opponentSeason.overall.rank} overall`}</div>
          </SummaryBlock>
        </div>

        <div style={{ display: "flex", width: "100%", height: 1, backgroundColor: PANEL_LINE }} />

        <div style={{ display: "flex", flexDirection: "row", padding: "0 56px", justifyContent: "space-between", flex: 1 }}>
          <SeasonColumn name="Michigan" teamId={data.michiganTeamId} season={b.michiganSeason} record={b.michiganRecord2025} />
          <div style={{ display: "flex", flexDirection: "column", width: 990, padding: "0 24px" }}>
            <CompareBlock heading="Michigan offense vs. Western defense" rows={b.michiganOffenseVsOpponentDefense} />
            <CompareBlock heading="Western offense vs. Michigan defense" rows={b.opponentOffenseVsMichiganDefense} />
          </div>
          <SeasonColumn name="Western Michigan" teamId={data.opponentTeamId} season={b.opponentSeason} record={b.opponentRecord2025} />
        </div>

        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "22px 64px 30px", borderTop: `1px solid ${PANEL_LINE}` }}>
          <div style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 18, fontWeight: 700, letterSpacing: 1, color: WHITE }}>MICHIGANFOOTBALLFOCUS.COM</div>
          <div style={{ display: "flex", fontFamily: "Inter", fontSize: 12, fontWeight: 500, color: DIM }}>Validated + research-only (marked R) opponent-adjusted metrics, schedule-adjusted model. Roster continuity is our own audit. Win prob / margin is a separate calibrated simulation.</div>
        </div>
      </div>
    ),
    { width: 1600, height: 1470, fonts }
  );
}

import { ImageResponse } from "next/og";
import { teamLogoUrl } from "../../../../lib/team-assets";
import { michiganWesternMichigan2026 as data } from "../../../../lib/michigan/matchup-preview-data";
import type { CompareRow } from "../../../../lib/michigan/matchup-preview-data";

export const runtime = "edge";

const NAVY = "#050c16";
const PANEL = "#0b1a2b";
const BORDER = "#22384d";
const MAIZE = "#ffcb05";
const WHITE = "#f4f7fb";
const DIM = "#8298ab";
const GOOD = "#3fae72";
const BAD = "#d9534f";

function rankColor(rank: number): string {
  // 1 = best (green) ... 136 = worst (red), interpolated through a neutral
  // panel-matching midpoint so an average rank doesn't read as "bad."
  const t = Math.max(0, Math.min(1, (rank - 1) / 135));
  const lerp = (a: number, b: number, x: number) => Math.round(a + (b - a) * x);
  if (t <= 0.5) {
    const x = t / 0.5;
    const from = [63, 174, 114]; // GOOD
    const to = [30, 42, 58]; // PANEL-ish neutral
    return `rgb(${lerp(from[0], to[0], x)},${lerp(from[1], to[1], x)},${lerp(from[2], to[2], x)})`;
  }
  const x = (t - 0.5) / 0.5;
  const from = [30, 42, 58];
  const to = [217, 83, 79]; // BAD
  return `rgb(${lerp(from[0], to[0], x)},${lerp(from[1], to[1], x)},${lerp(from[2], to[2], x)})`;
}

function Cell({ v }: { v: { value: string; rank: number } }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", width: 190, height: 56, borderRadius: 8, backgroundColor: rankColor(v.rank) }}>
      <div style={{ display: "flex", fontSize: 22, fontWeight: 700, color: WHITE }}>{v.value}</div>
      <div style={{ display: "flex", fontSize: 13, fontWeight: 600, color: "rgba(244,247,251,0.75)" }}>{`#${v.rank}`}</div>
    </div>
  );
}

function CompareBlock({ heading, rows }: { heading: string; rows: CompareRow[] }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
      <div style={{ display: "flex", fontSize: 17, fontWeight: 800, letterSpacing: 1, color: MAIZE, marginBottom: 10, marginTop: 18 }}>{heading.toUpperCase()}</div>
      {rows.map((r) => (
        <div key={r.metric} style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "7px 0", borderBottom: `1px solid ${BORDER}` }}>
          <Cell v={r.michigan} />
          <div style={{ display: "flex", fontSize: 17, fontWeight: 600, color: WHITE, textAlign: "center", width: 280, justifyContent: "center" }}>{r.metric}</div>
          <Cell v={r.opponent} />
        </div>
      ))}
    </div>
  );
}

function SeasonColumn({ name, teamId, season, record }: { name: string; teamId: number; season: typeof data.blueprint.michiganSeason; record: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: 250, alignItems: "center" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(teamId, 128)} width={84} height={84} alt="" />
      <div style={{ display: "flex", fontSize: 22, fontWeight: 800, color: WHITE, marginTop: 10 }}>{name.toUpperCase()}</div>
      <div style={{ display: "flex", fontSize: 15, fontWeight: 600, color: DIM, marginBottom: 14 }}>{`2025: ${record}`}</div>
      {[
        ["OFFENSE", season.offense],
        ["DEFENSE", season.defense],
        ["OVERALL", season.overall],
      ].map(([label, v]) => (
        <div key={label as string} style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%", padding: "9px 0", borderTop: `1px solid ${BORDER}` }}>
          <div style={{ display: "flex", fontSize: 12, fontWeight: 700, letterSpacing: 1, color: DIM }}>{label as string}</div>
          <div style={{ display: "flex", fontSize: 22, fontWeight: 800, color: WHITE, marginTop: 4 }}>{`#${(v as {value:string;rank:number}).rank}`}</div>
          <div style={{ display: "flex", fontSize: 13, fontWeight: 600, color: DIM }}>{(v as {value:string;rank:number}).value}</div>
        </div>
      ))}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%", padding: "9px 0", borderTop: `1px solid ${BORDER}` }}>
        <div style={{ display: "flex", fontSize: 12, fontWeight: 700, letterSpacing: 1, color: DIM }}>ROSTER CONTINUITY</div>
        <div style={{ display: "flex", fontSize: 16, fontWeight: 700, color: WHITE, marginTop: 6 }}>{`OFF ${season.offenseContinuityPct.toFixed(0)}%  ·  DEF ${season.defenseContinuityPct.toFixed(0)}%`}</div>
      </div>
    </div>
  );
}

function SummaryBlock({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "0 34px" }}>
      <div style={{ display: "flex", fontSize: 13, fontWeight: 800, letterSpacing: 1.5, color: DIM, marginBottom: 8 }}>{label.toUpperCase()}</div>
      {children}
    </div>
  );
}

export async function GET() {
  const b = data.blueprint;
  return new ImageResponse(
    (
      <div style={{ display: "flex", flexDirection: "column", width: 1600, height: 1260, backgroundColor: NAVY, fontFamily: "sans-serif" }}>
        <div style={{ display: "flex", width: "100%", height: 6, backgroundColor: MAIZE }} />

        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "34px 60px 20px" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={teamLogoUrl(data.michiganTeamId, 256)} width={130} height={130} alt="" />
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ display: "flex", fontSize: 50, fontWeight: 800, color: WHITE, letterSpacing: -1 }}>MICHIGAN vs WESTERN MICHIGAN</div>
            <div style={{ display: "flex", fontSize: 19, fontWeight: 700, color: MAIZE, letterSpacing: 2, marginTop: 8 }}>WEEK 1 · SEPT. 5, 2026 · MICHIGAN STADIUM</div>
          </div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={teamLogoUrl(data.opponentTeamId, 256)} width={130} height={130} alt="" />
        </div>

        <div style={{ display: "flex", flexDirection: "row", alignItems: "flex-start", justifyContent: "center", padding: "10px 0 26px", borderBottom: `1px solid ${BORDER}` }}>
          <SummaryBlock label="2025 record">
            <div style={{ display: "flex", fontSize: 30, fontWeight: 800, color: WHITE }}>{`${b.michiganRecord2025}  —  ${b.opponentRecord2025}`}</div>
          </SummaryBlock>
          <SummaryBlock label="Win probability (our model)">
            <div style={{ display: "flex", fontSize: 30, fontWeight: 800, color: WHITE }}>{`${b.winProbMichiganPct}%  —  ${b.winProbOpponentPct}%`}</div>
          </SummaryBlock>
          <SummaryBlock label="Projected margin (our model)">
            <div style={{ display: "flex", fontSize: 30, fontWeight: 800, color: WHITE }}>{b.projectedMargin}</div>
            <div style={{ display: "flex", fontSize: 12, fontWeight: 600, color: DIM, marginTop: 4 }}>{b.projectedMarginRange}</div>
          </SummaryBlock>
          <SummaryBlock label="Market (BetMGM, not our model)">
            <div style={{ display: "flex", fontSize: 30, fontWeight: 800, color: WHITE }}>{data.market ? data.market.spread : "—"}</div>
            <div style={{ display: "flex", fontSize: 12, fontWeight: 600, color: DIM, marginTop: 4 }}>{data.market ? `${data.market.winChance} implied` : ""}</div>
          </SummaryBlock>
          <SummaryBlock label="Composite edge">
            <div style={{ display: "flex", fontSize: 30, fontWeight: 800, color: MAIZE }}>{b.michiganSeason.overall.value.split("/")[0]} vs {b.opponentSeason.overall.value.split("/")[0]}</div>
            <div style={{ display: "flex", fontSize: 12, fontWeight: 600, color: DIM, marginTop: 4 }}>{`#${b.michiganSeason.overall.rank} vs #${b.opponentSeason.overall.rank} overall`}</div>
          </SummaryBlock>
        </div>

        <div style={{ display: "flex", flexDirection: "row", padding: "22px 50px 0", justifyContent: "space-between" }}>
          <SeasonColumn name="Michigan" teamId={data.michiganTeamId} season={b.michiganSeason} record={b.michiganRecord2025} />
          <div style={{ display: "flex", flexDirection: "column", width: 1030, padding: "0 20px" }}>
            <CompareBlock heading="Michigan offense vs. Western defense" rows={b.michiganOffenseVsOpponentDefense} />
            <CompareBlock heading="Western offense vs. Michigan defense" rows={b.opponentOffenseVsMichiganDefense} />
          </div>
          <SeasonColumn name="Western Michigan" teamId={data.opponentTeamId} season={b.opponentSeason} record={b.opponentRecord2025} />
        </div>

        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "22px 60px", marginTop: "auto", borderTop: `1px solid ${BORDER}` }}>
          <div style={{ display: "flex", fontSize: 15, fontWeight: 800, letterSpacing: 1, color: WHITE }}>MICHIGANFOOTBALLFOCUS.COM</div>
          <div style={{ display: "flex", fontSize: 13, fontWeight: 500, color: DIM }}>2025 opponent-adjusted model (validated-five, schedule-adjusted) + our own roster-continuity audit. Win prob / margin from a separate calibrated simulation, labeled above.</div>
        </div>
      </div>
    ),
    { width: 1600, height: 1260 }
  );
}

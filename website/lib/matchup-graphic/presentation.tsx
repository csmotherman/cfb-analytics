// PRESENTATION layer: pure JSX. Takes a fully-analyzed MatchupGraphicData
// and renders it -- there is deliberately no team name, statistic, edge
// score, or sentence hardcoded anywhere in this file. Every word on the
// graphic comes from `data`, `michiganColors`/`opponentColors`
// (lib/team-colors.ts, keyed by teamId), or `teamLogoUrl`
// (lib/team-assets.ts, keyed by teamId) -- swap the gameId this is built
// from and the whole graphic becomes a different team's story with zero
// JSX changes.
import { teamLogoUrl } from "../team-assets";
import { accentColor, teamColors } from "../team-colors";
import type { MatchupGraphicData, MatchupEdge, PossessionCard } from "./types";

const BG = "#071421";
const BG_2 = "#0a1c2c";
const PANEL = "#0c2033";
const LINE = "rgba(255,255,255,0.09)";
const MAIZE = "#ffcb05";
const WHITE = "#f5f7fa";
const DIM = "#9aa9b8";
const FAINT = "#6f8192";

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

function SectionTitle({ children }: { children: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, margin: "26px 0 16px" }}>
      <div style={{ display: "flex", flex: 1, height: 1, backgroundColor: LINE }} />
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 26, fontWeight: 700, color: WHITE, letterSpacing: 1 }}>{children}</span>
      <div style={{ display: "flex", flex: 1, height: 1, backgroundColor: LINE }} />
    </div>
  );
}

function QualityColumn({ name, color, quality, align }: { name: string; color: string; quality: MatchupGraphicData["michigan"]["quality"]; align: "left" | "right" }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: align === "left" ? "flex-start" : "flex-end", width: 460 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color, letterSpacing: 0.5 }}>{name.toUpperCase()}</span>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 56, fontWeight: 700, color: WHITE, lineHeight: 1 }}>{`#${quality.overall.rank}`}</span>
      <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 700, color: DIM, letterSpacing: 0.6, marginTop: 2 }}>OVERALL</span>
      <div style={{ display: "flex", gap: 18, marginTop: 10 }}>
        <span style={{ fontFamily: "Inter", fontSize: 14, fontWeight: 700, color: WHITE }}>{`#${quality.offense.rank} `}<span style={{ color: DIM, fontWeight: 600 }}>OFFENSE</span></span>
        <span style={{ fontFamily: "Inter", fontSize: 14, fontWeight: 700, color: WHITE }}>{`#${quality.defense.rank} `}<span style={{ color: DIM, fontWeight: 600 }}>DEFENSE</span></span>
      </div>
    </div>
  );
}

function PlayCallBar({ name, color, runPct, passPct }: { name: string; color: string; runPct: number; passPct: number }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color, letterSpacing: 0.5 }}>{name.toUpperCase()}</span>
        <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: WHITE }}>{`${runPct}% RUN`}<span style={{ color: DIM, fontWeight: 600 }}>{` · ${passPct}% PASS`}</span></span>
      </div>
      <div style={{ display: "flex", width: "100%", height: 16, borderRadius: 3, overflow: "hidden", backgroundColor: "rgba(255,255,255,0.08)" }}>
        <div style={{ display: "flex", width: `${runPct}%`, height: "100%", backgroundColor: color }} />
        <div style={{ display: "flex", width: `${passPct}%`, height: "100%", backgroundColor: "#44586b" }} />
      </div>
    </div>
  );
}

function FieldPositionRow({ michiganColor, opponentColor, data }: { michiganColor: string; opponentColor: string; data: MatchupGraphicData }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  // Field runs goal line (0) to midfield (50) -- teams start possessions in their own territory.
  const pct = (yardLine: number) => Math.max(2, Math.min(98, (yardLine / 50) * 100));
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, color: DIM }}>OWN GOAL</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, color: DIM }}>50</span>
      </div>
      <div style={{ display: "flex", position: "relative", width: "100%", height: 6, borderRadius: 3, backgroundColor: "rgba(255,255,255,0.1)" }}>
        {mich && <div style={{ display: "flex", position: "absolute", left: `${pct(mich.ownYardLine)}%`, top: -7, width: 3, height: 20, backgroundColor: michiganColor, borderRadius: 2 }} />}
        {opp && <div style={{ display: "flex", position: "absolute", left: `${pct(opp.ownYardLine)}%`, top: -7, width: 3, height: 20, backgroundColor: opponentColor, borderRadius: 2 }} />}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 22 }}>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: michiganColor }}>{mich ? `OWN ${mich.ownYardLine.toFixed(1)}` : "—"}</span>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: FAINT }}>{data.michigan.name.toUpperCase()}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: opponentColor }}>{opp ? `OWN ${opp.ownYardLine.toFixed(1)}` : "—"}</span>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: FAINT }}>{data.opponent.name.toUpperCase()}</span>
        </div>
      </div>
    </div>
  );
}

function EdgeRow({ edge, michiganColor, opponentColor, opponentName }: { edge: MatchupEdge; michiganColor: string; opponentColor: string; opponentName: string }) {
  const score = edge.score ?? 0;
  // Michigan's label sits at the LEFT (0%), the opponent's at the RIGHT
  // (100%) -- so a positive (Michigan-favoring) score must move the
  // marker toward 0%, i.e. SUBTRACT from center, not add.
  const markerPct = 50 - score / 2;
  const verdictColor = edge.direction === "michigan" ? michiganColor : edge.direction === "opponent" ? opponentColor : DIM;
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", padding: "12px 0", borderTop: `1px solid ${LINE}` }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: WHITE, letterSpacing: 0.4 }}>{edge.label}</span>
        <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 800, color: verdictColor, letterSpacing: 0.3 }}>{edge.verdictLabel}</span>
      </div>
      <div style={{ display: "flex", position: "relative", width: "100%", height: 8, borderRadius: 4, backgroundImage: `linear-gradient(90deg, ${michiganColor}55, rgba(255,255,255,0.08) 48%, rgba(255,255,255,0.08) 52%, ${opponentColor}55)` }}>
        <div style={{ display: "flex", position: "absolute", left: "50%", top: -4, width: 1, height: 16, backgroundColor: LINE }} />
        {edge.score != null && (
          <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -6, width: 12, height: 12, borderRadius: 6, backgroundColor: WHITE, border: `2px solid ${verdictColor}`, marginLeft: -6 }} />
        )}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: FAINT }}>{`${(edge.michigan.value * 100).toFixed(1)}% · #${edge.michigan.rank}`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: FAINT }}>{`${opponentName.toUpperCase()} #${edge.opponent.rank} · ${(edge.opponent.value * 100).toFixed(1)}%`}</span>
      </div>
    </div>
  );
}

function PossessionCardView({ card, headingColor, defenseColor }: { card: PossessionCard; headingColor: string; defenseColor: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, minWidth: 0, borderRadius: 8, border: `1px solid ${LINE}`, backgroundColor: PANEL, padding: "18px 20px", overflow: "hidden" }}>
      <div style={{ display: "flex", width: "40%", height: 3, backgroundColor: headingColor, borderRadius: 2, marginBottom: 12 }} />
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 24, fontWeight: 700, color: WHITE }}>{`WHEN ${card.offenseTeamName.toUpperCase()} HAS THE BALL`}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: headingColor }}>{`${card.playCalling.runPct}% RUN`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: DIM }}>•</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: DIM }}>{`${card.playCalling.passPct}% PASS`}</span>
      </div>

      {card.bestEdge && (
        <div style={{ display: "flex", flexDirection: "column", marginTop: 16, paddingTop: 14, borderTop: `1px solid ${LINE}` }}>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 1, color: headingColor }}>{`BEST EDGE: ${card.bestEdge.label}`}</span>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: FAINT, marginTop: 3 }}>{`${card.offenseTeamName} #${card.bestEdge.attacker.rank} · ${card.defenseTeamName} #${card.bestEdge.defender.rank} allowed`}</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 18, fontWeight: 700, color: WHITE, marginTop: 6, lineHeight: 1.15 }}>{card.bestEdge.sentence}</span>
        </div>
      )}

      {card.resistance && (
        <div style={{ display: "flex", flexDirection: "column", marginTop: 14, paddingTop: 14, borderTop: `1px solid ${LINE}` }}>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 800, letterSpacing: 1, color: defenseColor }}>{`WATCH: ${card.resistance.label}`}</span>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: FAINT, marginTop: 3 }}>{`${card.defenseTeamName} #${card.resistance.rank}`}</span>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: DIM, marginTop: 6, lineHeight: 1.15 }}>{card.resistance.sentence}</span>
        </div>
      )}
    </div>
  );
}

export function MatchupGraphic({ data }: { data: MatchupGraphicData }) {
  const michiganColors = teamColors(data.michigan.teamId);
  const opponentColors = teamColors(data.opponent.teamId);
  const michiganAccent = accentColor(michiganColors);
  const opponentAccent = accentColor(opponentColors);
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "long", month: "long", day: "numeric", year: "numeric" });

  return (
    <div style={{ display: "flex", position: "relative", flexDirection: "column", width: 1600, backgroundImage: `linear-gradient(165deg, ${BG_2} 0%, ${BG} 55%)`, fontFamily: "Inter", border: "1px solid rgba(255,203,5,0.28)" }}>
      <div style={{ display: "flex", width: "100%", height: 3, backgroundColor: MAIZE }} />
      <CornerMark top left /><CornerMark top left={false} /><CornerMark top={false} left /><CornerMark top={false} left={false} />

      {/* Header */}
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "30px 64px 10px" }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={teamLogoUrl(data.michigan.teamId, 256)} width={110} height={110} alt="" />
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 56, fontWeight: 700, color: WHITE }}>
            MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 26, fontWeight: 600, color: FAINT, margin: "0 16px" }}>vs</span>{data.opponent.name.toUpperCase()}
          </div>
          <div style={{ display: "flex", fontFamily: "Inter", fontSize: 13, fontWeight: 700, color: MAIZE, letterSpacing: 2.6, marginTop: 6 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
        </div>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={teamLogoUrl(data.opponent.teamId, 256)} width={140} height={140} alt="" />
      </div>

      <div style={{ display: "flex", flexDirection: "column", padding: "6px 64px 0" }}>
        {/* Top quality strip */}
        <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", padding: "18px 0", borderTop: `1px solid ${LINE}`, borderBottom: `1px solid ${LINE}` }}>
          <QualityColumn name={data.michigan.name} color={michiganAccent} quality={data.michigan.quality} align="left" />
          <QualityColumn name={data.opponent.name} color={opponentAccent} quality={data.opponent.quality} align="right" />
        </div>

        {/* Play-call split + field position */}
        <div style={{ display: "flex", flexDirection: "row", gap: 40, marginTop: 22 }}>
          <div style={{ display: "flex", flexDirection: "column", width: 760 }}>
            <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1.2, color: DIM, marginBottom: 10 }}>PLAY-CALL SPLIT</span>
            <PlayCallBar name={data.michigan.name} color={michiganAccent} runPct={data.whenMichiganHasBall.playCalling.runPct} passPct={data.whenMichiganHasBall.playCalling.passPct} />
            <PlayCallBar name={data.opponent.name} color={opponentAccent} runPct={data.whenOpponentHasBall.playCalling.runPct} passPct={data.whenOpponentHasBall.playCalling.passPct} />
          </div>
          <div style={{ display: "flex", flexDirection: "column", flex: 1, borderLeft: `1px solid ${LINE}`, paddingLeft: 40 }}>
            <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1.2, color: DIM, marginBottom: 14 }}>AVERAGE STARTING FIELD POSITION</span>
            <FieldPositionRow michiganColor={michiganAccent} opponentColor={opponentAccent} data={data} />
          </div>
        </div>

        {/* Where's the edge */}
        <SectionTitle>WHERE&apos;S THE EDGE?</SectionTitle>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 2 }}>
          <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, letterSpacing: 0.8, color: michiganAccent }}>MICHIGAN ADVANTAGE</span>
          <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, letterSpacing: 0.8, color: opponentAccent }}>{`${data.opponent.name.toUpperCase()} ADVANTAGE`}</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          {data.edges.map((edge) => <EdgeRow key={edge.id} edge={edge} michiganColor={michiganAccent} opponentColor={opponentAccent} opponentName={data.opponent.name} />)}
        </div>

        {/* When each team has the ball */}
        <SectionTitle>THE TWO PHASES OF THE GAME</SectionTitle>
        <div style={{ display: "flex", flexDirection: "row", gap: 20 }}>
          <PossessionCardView card={data.whenMichiganHasBall} headingColor={michiganAccent} defenseColor={opponentAccent} />
          <PossessionCardView card={data.whenOpponentHasBall} headingColor={opponentAccent} defenseColor={michiganAccent} />
        </div>

        {/* Verdict */}
        <SectionTitle>MFF MATCHUP VERDICT</SectionTitle>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center", padding: "18px 0 26px" }}>
          {data.prediction.type === "model" && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 48, fontWeight: 700, color: WHITE }}>{data.prediction.marginLabel}</span>
              <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 8 }}>
                <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 700, color: DIM, letterSpacing: 0.6 }}>{data.prediction.label}</span>
                {data.prediction.winProbabilityPct != null && <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 700, color: MAIZE }}>{`${data.prediction.winProbabilityPct}% WIN PROBABILITY`}</span>}
                {data.prediction.marketNote && <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: FAINT }}>{data.prediction.marketNote}</span>}
              </div>
            </div>
          )}
          {data.prediction.type === "market" && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 48, fontWeight: 700, color: WHITE }}>{data.prediction.spreadLabel}</span>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8 }}>
                <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 700, color: DIM, letterSpacing: 0.6 }}>{data.prediction.label}</span>
                <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: FAINT }}>{data.prediction.book}</span>
              </div>
            </div>
          )}
          {data.prediction.type === "unavailable" && <span style={{ fontFamily: "Barlow Condensed", fontSize: 30, fontWeight: 700, color: DIM }}>PREDICTION NOT AVAILABLE</span>}
        </div>

        {/* Footer */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "14px 0 24px", borderTop: `1px solid ${LINE}` }}>
          <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 600, color: DIM }}>2025 opponent-adjusted metrics · FBS ranks · MFF model · Market line labeled separately</span>
          <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 14 }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="https://michiganfootballfocus.com/brand/michigan-football-focus.png" width={90} height={30} alt="" />
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 24, fontWeight: 700, color: MAIZE }}>MICHIGANFOOTBALLFOCUS.COM</span>
          </div>
        </div>
      </div>
    </div>
  );
}

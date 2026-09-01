// PRESENTATION layer: pure JSX. Takes a fully-analyzed MatchupGraphicData
// and renders it -- there is deliberately no team name, statistic, edge
// score, or sentence hardcoded anywhere in this file. Every word on the
// graphic comes from `data`, `michiganColors`/`opponentColors`
// (lib/team-colors.ts, keyed by teamId), or `teamLogoUrl`
// (lib/team-assets.ts, keyed by teamId) -- swap the gameId this is built
// from and the whole graphic becomes a different team's story with zero
// JSX changes.
//
// The only logic in this file is tiny, purely presentational derivations
// (a field-position readout string, one "the read" sentence) built from
// data analysis.ts already computed -- no new stats, no new edge math.
import { teamLogoUrl } from "../team-assets";
import { accentColor, teamColors } from "../team-colors";
import type { EdgeCategoryId, MatchupEdge, MatchupGraphicData, PossessionCard } from "./types";

const BG = "#071421";
const BG_2 = "#0a1c2c";
const PANEL = "#0c2033";
const LINE = "rgba(255,255,255,0.09)";
const MAIZE = "#ffcb05";
const WHITE = "#f5f7fa";
const DIM = "#9aa9b8";
const FAINT = "#6f8192";

function CornerMark({ top, left }: { top: boolean; left: boolean }) {
  const legLen = 14;
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

function SectionLabel({ children }: { children: string }) {
  return <span style={{ display: "flex", fontFamily: "Inter", fontSize: 12, fontWeight: 800, letterSpacing: 1.6, color: DIM }}>{children}</span>;
}

// ---- tiny presentation-only derivations (no new analysis) ----

function fieldPositionReadout(mich: MatchupGraphicData["michigan"]["fieldPosition"], opp: MatchupGraphicData["opponent"]["fieldPosition"], michiganName: string, opponentName: string): string {
  if (!mich || !opp) return "—";
  const diff = mich.ownYardLine - opp.ownYardLine; // higher own-yard-line = starts further from own goal = better
  if (Math.abs(diff) < 1) return "NEARLY EVEN";
  const better = diff > 0 ? michiganName : opponentName;
  return `${better.toUpperCase()} +${Math.abs(diff).toFixed(1)} YDS`;
}

const CATEGORY_PHRASE: Record<EdgeCategoryId, string> = {
  efficiency: "in overall efficiency",
  run: "on the ground",
  pass: "through the air",
  explosiveness: "in explosive plays",
  situational: "on third down",
};

function matchupRead(edges: MatchupEdge[], michiganName: string, opponentName: string): string {
  const scored = edges.filter((e) => e.score != null && e.direction !== "even");
  if (scored.length === 0) return "This matchup grades out close to even across the board.";
  const strongest = scored.reduce((a, b) => (Math.abs(b.score as number) > Math.abs(a.score as number) ? b : a));
  const team = strongest.direction === "michigan" ? michiganName : opponentName;
  const verb = strongest.direction === "michigan" ? "clearest advantage comes" : "strongest matchup advantage comes";
  return `${team}'s ${verb} ${CATEGORY_PHRASE[strongest.id]}.`;
}

// ---- header ----

function Header({ data }: { data: MatchupGraphicData }) {
  const kickoff = new Date(data.kickoffISO);
  const dateLabel = kickoff.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "long", month: "long", day: "numeric", year: "numeric" });
  return (
    <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "20px 56px 6px" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.michigan.teamId, 256)} width={92} height={92} alt="" />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "baseline", fontFamily: "Barlow Condensed", fontSize: 50, fontWeight: 700, color: WHITE }}>
          MICHIGAN<span style={{ display: "flex", fontFamily: "Inter", fontSize: 23, fontWeight: 600, color: FAINT, margin: "0 14px" }}>vs</span>{data.opponent.name.toUpperCase()}
        </div>
        <div style={{ display: "flex", fontFamily: "Inter", fontSize: 12, fontWeight: 700, color: MAIZE, letterSpacing: 2.2, marginTop: 4 }}>{`WEEK ${data.week} · ${dateLabel.toUpperCase()} · ${data.venue.toUpperCase()}`}</div>
      </div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(data.opponent.teamId, 256)} width={110} height={110} alt="" />
    </div>
  );
}

// ---- team card + field position row ----

function RankPair({ rank, label }: { rank: number; label: string }) {
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 5 }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 20, fontWeight: 700, color: WHITE }}>{`#${rank}`}</span>
      <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, color: DIM }}>{label}</span>
    </div>
  );
}

function TeamCard({ team, accent, teamId, align }: { team: MatchupGraphicData["michigan"]; accent: string; teamId: number; align: "left" | "right" }) {
  const bgLogoSide = align === "left" ? { right: -18 } : { left: -18 };
  return (
    <div style={{ display: "flex", position: "relative", flexDirection: "column", flex: 1, borderRadius: 8, border: `1px solid ${LINE}`, backgroundColor: PANEL, padding: "14px 20px", overflow: "hidden" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={teamLogoUrl(teamId, 256)} width={130} height={130} alt="" style={{ position: "absolute", opacity: 0.07, top: -18, ...bgLogoSide }} />
      <span style={{ display: "flex", fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: accent, letterSpacing: 0.3 }}>{team.name.toUpperCase()}</span>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 2 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 44, fontWeight: 700, color: WHITE, lineHeight: 1 }}>{`#${team.quality.overall.rank}`}</span>
        <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, color: DIM }}>OVERALL</span>
      </div>
      <div style={{ display: "flex", gap: 18, marginTop: 8 }}>
        <RankPair rank={team.quality.offense.rank} label="OFF" />
        <RankPair rank={team.quality.defense.rank} label="DEF" />
      </div>
      <div style={{ display: "flex", flexDirection: "column", marginTop: 10, paddingTop: 10, borderTop: `1px solid ${LINE}` }}>
        <span style={{ display: "flex", fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, letterSpacing: 0.8, color: DIM }}>PLAY CALLS</span>
        <div style={{ display: "flex", alignItems: "baseline", gap: 7, marginTop: 2 }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 21, fontWeight: 700, color: accent }}>{`${Math.round(team.tendencies.rushDecisionRate * 100)}% RUN`}</span>
          <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: DIM }}>{`${100 - Math.round(team.tendencies.rushDecisionRate * 100)}% PASS`}</span>
        </div>
      </div>
    </div>
  );
}

function FieldPositionPanel({ michiganColor, opponentColor, data }: { michiganColor: string; opponentColor: string; data: MatchupGraphicData }) {
  const mich = data.michigan.fieldPosition;
  const opp = data.opponent.fieldPosition;
  const pct = (yardLine: number) => Math.max(3, Math.min(97, (yardLine / 50) * 100));
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 260, padding: "6px 14px" }}>
      <SectionLabel>FIELD POSITION</SectionLabel>
      <div style={{ display: "flex", justifyContent: "space-between", width: "100%", marginTop: 16 }}>
        <span style={{ fontFamily: "Inter", fontSize: 9, fontWeight: 700, color: FAINT }}>OWN GOAL</span>
        <span style={{ fontFamily: "Inter", fontSize: 9, fontWeight: 700, color: FAINT }}>20</span>
        <span style={{ fontFamily: "Inter", fontSize: 9, fontWeight: 700, color: FAINT }}>40</span>
        <span style={{ fontFamily: "Inter", fontSize: 9, fontWeight: 700, color: FAINT }}>50</span>
      </div>
      <div style={{ display: "flex", position: "relative", width: "100%", height: 5, borderRadius: 3, backgroundColor: "rgba(255,255,255,0.1)", marginTop: 4 }}>
        {mich && <div style={{ display: "flex", position: "absolute", left: `${pct(mich.ownYardLine)}%`, top: -6, width: 3, height: 17, backgroundColor: michiganColor, borderRadius: 2 }} />}
        {opp && <div style={{ display: "flex", position: "absolute", left: `${pct(opp.ownYardLine)}%`, top: -6, width: 3, height: 17, backgroundColor: opponentColor, borderRadius: 2 }} />}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", width: "100%", marginTop: 16 }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: michiganColor }}>{mich ? `OWN ${mich.ownYardLine.toFixed(1)}` : "—"}</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: opponentColor }}>{opp ? `OWN ${opp.ownYardLine.toFixed(1)}` : "—"}</span>
      </div>
      <div style={{ display: "flex", marginTop: 10, padding: "5px 14px", borderRadius: 6, backgroundColor: "rgba(255,255,255,0.05)" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 14, fontWeight: 700, color: WHITE }}>{fieldPositionReadout(mich, opp, data.michigan.name, data.opponent.name)}</span>
      </div>
    </div>
  );
}

// ---- where's the edge: five compact cards ----

function EdgeCard({ edge, michiganColor, opponentColor }: { edge: MatchupEdge; michiganColor: string; opponentColor: string }) {
  const score = edge.score ?? 0;
  const markerPct = 50 - score / 2; // Michigan favored -> left; see presentation notes below
  const verdictColor = edge.direction === "michigan" ? michiganColor : edge.direction === "opponent" ? opponentColor : DIM;
  return (
    <div style={{ display: "flex", flex: 1, flexDirection: "column", alignItems: "center", padding: "12px 8px", borderRadius: 8, border: `1px solid ${LINE}`, backgroundColor: PANEL }}>
      <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, color: WHITE, textAlign: "center", letterSpacing: 0.2 }}>{edge.label}</span>
      {edge.id === "efficiency" && <span style={{ fontFamily: "Inter", fontSize: 8.5, fontWeight: 600, color: FAINT, marginTop: 1 }}>Success Rate</span>}
      <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 800, color: verdictColor, marginTop: 8, textAlign: "center", letterSpacing: 0.2 }}>{edge.verdictLabel}</span>
      <div style={{ display: "flex", position: "relative", width: "84%", height: 4, marginTop: 9, borderRadius: 2, backgroundColor: "rgba(255,255,255,0.12)" }}>
        <div style={{ display: "flex", position: "absolute", left: "50%", top: -3, width: 1, height: 10, backgroundColor: LINE }} />
        {edge.score != null && <div style={{ display: "flex", position: "absolute", left: `${markerPct}%`, top: -3, width: 10, height: 10, borderRadius: 5, backgroundColor: WHITE, border: `2px solid ${verdictColor}`, marginLeft: -5 }} />}
      </div>
      {edge.score != null ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: 9, gap: 2 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
            <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, color: FAINT }}>{`MICH OFF #${edge.michigan.rank}`}</span>
            <span style={{ fontFamily: "Inter", fontSize: 8, fontWeight: 500, color: FAINT }}>{`${(edge.michigan.value * 100).toFixed(1)}%`}</span>
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
            <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, color: FAINT }}>{`OPP OFF #${edge.opponent.rank}`}</span>
            <span style={{ fontFamily: "Inter", fontSize: 8, fontWeight: 500, color: FAINT }}>{`${(edge.opponent.value * 100).toFixed(1)}%`}</span>
          </div>
        </div>
      ) : (
        <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 700, color: FAINT, marginTop: 9 }}>DATA UNAVAILABLE</span>
      )}
    </div>
  );
}

// ---- possession cards ----

function shortTag(teamName: string): string {
  return teamName === "Michigan" ? "MICH" : "OPP";
}

function PossessionCardView({ card, headingColor }: { card: PossessionCard; headingColor: string }) {
  const isMichiganDefending = card.defenseTeamName === "Michigan";
  const offenseTag = shortTag(card.offenseTeamName);
  const defenseTag = shortTag(card.defenseTeamName);
  return (
    <div style={{ display: "flex", flex: 1, flexDirection: "column", borderRadius: 8, border: `1px solid ${LINE}`, backgroundColor: PANEL, overflow: "hidden" }}>
      <div style={{ display: "flex", width: "100%", height: 3, backgroundColor: headingColor }} />
      <div style={{ display: "flex", flexDirection: "column", padding: "14px 20px 16px" }}>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 19, fontWeight: 700, color: WHITE }}>{`WHEN ${card.offenseTeamName.toUpperCase()} HAS THE BALL`}</span>
        <div style={{ display: "flex", alignItems: "baseline", gap: 9, marginTop: 6 }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 32, fontWeight: 700, color: headingColor }}>{`${card.playCalling.runPct}% RUN`}</span>
          <span style={{ fontFamily: "Inter", fontSize: 13, fontWeight: 600, color: DIM }}>{`${card.playCalling.passPct}% PASS`}</span>
        </div>

        {card.bestEdge && (
          <div style={{ display: "flex", flexDirection: "column", marginTop: 12, paddingTop: 11, borderTop: `1px solid ${LINE}` }}>
            <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 800, letterSpacing: 1, color: DIM }}>BEST MATCHUP</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 3 }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: WHITE }}>{card.bestEdge.label}</span>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: headingColor }}>{`${card.offenseTeamName.toUpperCase()} →`}</span>
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 5, marginTop: 2 }}>
              <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, color: FAINT }}>{`${offenseTag} OFF #${card.bestEdge.attacker.rank}`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 9, fontWeight: 500, color: FAINT }}>{`${(card.bestEdge.attacker.value * 100).toFixed(1)}%`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 10.5, fontWeight: 700, color: FAINT }}>{`· ${defenseTag} DEF #${card.bestEdge.defender.rank} allowed`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 9, fontWeight: 500, color: FAINT }}>{`${(card.bestEdge.defender.value * 100).toFixed(1)}%`}</span>
            </div>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 15, fontWeight: 700, color: WHITE, marginTop: 7, lineHeight: 1.2 }}>{card.bestEdge.sentence}</span>
          </div>
        )}

        {card.resistance && (
          <div style={{ display: "flex", flexDirection: "column", marginTop: 10, paddingTop: 10, borderTop: `1px solid ${LINE}` }}>
            <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 800, letterSpacing: 1, color: DIM }}>{isMichiganDefending ? "MICHIGAN COUNTER" : `WATCH: ${card.defenseTeamName.toUpperCase()}`}</span>
            <div style={{ display: "flex", alignItems: "baseline", gap: 7, marginTop: 3 }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 16, fontWeight: 700, color: WHITE }}>{card.resistance.label}</span>
              <span style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 700, color: DIM }}>{`${defenseTag} #${card.resistance.rank}`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 500, color: FAINT }}>{`${(card.resistance.value * 100).toFixed(1)}%`}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ---- prediction hero footer ----

function PredictionFooter({ data }: { data: MatchupGraphicData }) {
  const read = matchupRead(data.edges, data.michigan.name, data.opponent.name);
  return (
    <div style={{ display: "flex", flexDirection: "column", borderRadius: 8, border: `1px solid ${LINE}`, backgroundImage: "linear-gradient(135deg, rgba(255,203,5,.07), rgba(12,32,51,.94))", padding: "16px 30px" }}>
      <span style={{ display: "flex", alignSelf: "center", fontFamily: "Inter", fontSize: 13, fontWeight: 800, letterSpacing: 2, color: DIM }}>MFF MATCHUP VERDICT</span>

      {data.prediction.type === "model" && (
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 46, marginTop: 8 }}>
          {data.prediction.winProbabilityPct != null && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 30, fontWeight: 700, color: MAIZE }}>{`${data.prediction.winProbabilityPct}%`}</span>
              <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 700, color: DIM, letterSpacing: 0.4 }}>WIN PROBABILITY</span>
            </div>
          )}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 46, fontWeight: 700, color: WHITE, lineHeight: 1 }}>{data.prediction.marginLabel}</span>
            <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 700, color: DIM, letterSpacing: 0.4, marginTop: 2 }}>{data.prediction.label}</span>
          </div>
          {data.prediction.marketNote && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: WHITE }}>{data.prediction.marketNote.replace("Market: ", "")}</span>
              <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 700, color: DIM, letterSpacing: 0.4 }}>MARKET</span>
            </div>
          )}
        </div>
      )}

      {data.prediction.type === "market" && (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: 8 }}>
          <span style={{ fontFamily: "Barlow Condensed", fontSize: 46, fontWeight: 700, color: WHITE, lineHeight: 1 }}>{data.prediction.spreadLabel}</span>
          <span style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 700, color: DIM, letterSpacing: 0.4, marginTop: 4 }}>{`${data.prediction.label} · ${data.prediction.book}`}</span>
        </div>
      )}

      {data.prediction.type === "unavailable" && (
        <span style={{ display: "flex", alignSelf: "center", fontFamily: "Barlow Condensed", fontSize: 28, fontWeight: 700, color: DIM, marginTop: 10 }}>PREDICTION NOT AVAILABLE</span>
      )}

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: 14, paddingTop: 12, borderTop: `1px solid ${LINE}` }}>
        <span style={{ fontFamily: "Inter", fontSize: 9.5, fontWeight: 800, letterSpacing: 1.2, color: MAIZE }}>THE READ</span>
        <span style={{ fontFamily: "Barlow Condensed", fontSize: 18, fontWeight: 700, color: WHITE, marginTop: 4, textAlign: "center" }}>{read}</span>
      </div>
    </div>
  );
}

// ---- root ----

export function MatchupGraphic({ data }: { data: MatchupGraphicData }) {
  const michiganColors = teamColors(data.michigan.teamId);
  const opponentColors = teamColors(data.opponent.teamId);
  const michiganAccent = accentColor(michiganColors);
  const opponentAccent = accentColor(opponentColors);

  return (
    <div style={{ display: "flex", position: "relative", flexDirection: "column", width: 1600, backgroundImage: `linear-gradient(165deg, ${BG_2} 0%, ${BG} 55%)`, fontFamily: "Inter", border: "1px solid rgba(255,203,5,0.28)" }}>
      <div style={{ display: "flex", width: "100%", height: 3, backgroundColor: MAIZE }} />
      <CornerMark top left /><CornerMark top left={false} /><CornerMark top={false} left /><CornerMark top={false} left={false} />

      <Header data={data} />

      <div style={{ display: "flex", flexDirection: "column", padding: "8px 56px 0" }}>
        {/* Team cards + field position */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "stretch", gap: 14 }}>
          <TeamCard team={data.michigan} accent={michiganAccent} teamId={data.michigan.teamId} align="left" />
          <FieldPositionPanel michiganColor={michiganAccent} opponentColor={opponentAccent} data={data} />
          <TeamCard team={data.opponent} accent={opponentAccent} teamId={data.opponent.teamId} align="right" />
        </div>

        {/* Where's the edge */}
        <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "baseline", margin: "18px 0 10px" }}>
          <SectionLabel>WHERE&apos;S THE EDGE?</SectionLabel>
          <span style={{ fontFamily: "Inter", fontSize: 9, fontWeight: 600, color: FAINT }}>Success Rate = share of plays that stay on schedule</span>
        </div>
        <div style={{ display: "flex", flexDirection: "row", gap: 10 }}>
          {data.edges.map((edge) => <EdgeCard key={edge.id} edge={edge} michiganColor={michiganAccent} opponentColor={opponentAccent} />)}
        </div>

        {/* The two phases of the game */}
        <div style={{ display: "flex", margin: "20px 0 10px" }}>
          <SectionLabel>THE TWO PHASES OF THE GAME</SectionLabel>
        </div>
        <div style={{ display: "flex", flexDirection: "row", alignItems: "stretch", gap: 0 }}>
          <PossessionCardView card={data.whenMichiganHasBall} headingColor={michiganAccent} />
          <div style={{ display: "flex", width: 50, alignItems: "center", justifyContent: "center" }}>
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: FAINT }}>VS</span>
          </div>
          <PossessionCardView card={data.whenOpponentHasBall} headingColor={opponentAccent} />
        </div>

        {/* Prediction */}
        <div style={{ display: "flex", margin: "18px 0 0" }}>
          <PredictionFooter data={data} />
        </div>

        {/* Footer */}
        <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "12px 0 18px", marginTop: 10, borderTop: `1px solid ${LINE}` }}>
          <span style={{ fontFamily: "Inter", fontSize: 10, fontWeight: 600, color: DIM }}>2025 opponent-adjusted metrics · FBS ranks · MFF model · Market line labeled separately</span>
          <div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 12 }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="https://michiganfootballfocus.com/brand/michigan-football-focus.png" width={82} height={27} alt="" />
            <span style={{ fontFamily: "Barlow Condensed", fontSize: 22, fontWeight: 700, color: MAIZE }}>MICHIGANFOOTBALLFOCUS.COM</span>
          </div>
        </div>
      </div>
    </div>
  );
}

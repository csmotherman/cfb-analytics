import type { FourthDownDecision } from "../../lib/michigan/big-game-decisions-data";

const LABEL: Record<string, string> = { go: "WENT FOR IT", fieldGoal: "KICKED FG", punt: "PUNTED" };
const RANKED_OPPONENTS = new Set(["Oklahoma", "Ohio State", "Texas"]);

function clockLabel(period: number, clock: { minutes: number; seconds: number }): string {
  const q = period <= 4 ? `Q${period}` : "OT";
  return `${q} ${clock.minutes}:${String(clock.seconds).padStart(2, "0")}`;
}

export function FourthDownBoard({ decisions }: { decisions: FourthDownDecision[] }) {
  const ordered = [...decisions].sort((a, b) => (a.seasonType !== b.seasonType ? (a.seasonType === "regular" ? -1 : 1) : a.week - b.week));

  return (
    <div className="fd-board">
      {ordered.map((d, i) => {
        const correct = d.actual === d.recommended;
        const evLost = d.evLost ?? 0;
        const marquee = RANKED_OPPONENTS.has(d.opponent);
        return (
          <div className={`fd-card ${correct ? "fd-correct" : "fd-incorrect"} ${marquee ? "fd-marquee" : ""}`} key={i}>
            <div className="fd-card-top">
              <span className="fd-opp">{d.opponent}{marquee ? <b className="fd-badge">MARQUEE</b> : null}</span>
              <span className="fd-clock">{d.seasonType === "postseason" ? "CFP" : `WK ${d.week}`} · {clockLabel(d.period, d.clock)}</span>
            </div>
            <div className="fd-situation">4th &amp; {d.distance.toFixed(0)} at {d.yardsToGoal <= 50 ? `opp ${d.yardsToGoal.toFixed(0)}` : `own ${(100 - d.yardsToGoal).toFixed(0)}`}</div>
            <div className="fd-verdict">
              <div className="fd-choice">
                <span>ACTUAL</span>
                <strong>{LABEL[d.actual]}</strong>
              </div>
              <div className={`fd-outcome ${correct ? "fd-outcome-good" : "fd-outcome-bad"}`}>
                {correct ? "OPTIMAL CALL" : `SHOULD HAVE ${LABEL[d.recommended]}`}
              </div>
              <div className="fd-choice fd-choice-right">
                <span>EV LOST</span>
                <strong>{correct ? "0.00" : `-${evLost.toFixed(2)}`}</strong>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

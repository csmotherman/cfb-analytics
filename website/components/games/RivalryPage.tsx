import { EmptyState } from "../ui/EmptyState";
import { TeamLogo } from "../ui/TeamLogo";

type Props = {
  opponent: string;
  opponentId: number;
  eyebrow: string;
  headline: string;
};

export function RivalryPage({ opponent, opponentId, eyebrow, headline }: Props) {
  return (
    <div className="page-stack page-pad">
      <section className="game-hub-hero">
        <span className="eyebrow">{eyebrow} · SINCE 2010</span>
        <div className="game-matchup">
          <div><TeamLogo teamId={130} name="Michigan" size={256} /><strong>MICHIGAN</strong></div>
          <em>VS</em>
          <div><TeamLogo teamId={opponentId} name={opponent} size={256} /><strong>{opponent.toUpperCase()}</strong></div>
        </div>
        <h1>{headline}</h1>
      </section>
      <EmptyState eyebrow="RIVALRY HISTORY" title="More rivalry numbers coming soon.">
        Recent results, top performances and matchup trends.
      </EmptyState>
    </div>
  );
}

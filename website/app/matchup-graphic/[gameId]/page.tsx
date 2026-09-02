import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { buildMatchupGraphicData } from "../../../lib/matchup-graphic/build-matchup";
import { MatchupGraphic } from "../../../lib/matchup-graphic/presentation";
import { FitToScreen } from "./FitToScreen";

type Props = { params: Promise<{ gameId: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { gameId } = await params;
  const data = buildMatchupGraphicData(gameId);
  if (!data) return {};
  return {
    title: `Michigan vs. ${data.opponent.name} Matchup Graphic`,
    description: `Team quality ranks, play-calling identity, offense-vs-defense matchup edges, and the MFF verdict for Michigan vs. ${data.opponent.name}.`,
  };
}

export default async function MatchupGraphicPage({ params }: Props) {
  const { gameId } = await params;
  const data = buildMatchupGraphicData(gameId);
  if (!data) notFound();

  return (
    <FitToScreen>
      <MatchupGraphic data={data} />
    </FitToScreen>
  );
}

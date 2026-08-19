import type { MichiganPlayer } from "../../lib/michigan/types";
import { classLabel, formatHeight } from "../../lib/michigan/format";
import { TeamLogo } from "../ui/TeamLogo";
import { GradeBadge } from "../ui/GradeBadge";
export function PlayerHero({ player }: { player: MichiganPlayer }) {
  return <section className="player-hero"><div className="player-hero-copy"><span>2026 MICHIGAN ROSTER · PRESEASON</span><b>#{player.jersey ?? "—"}</b><h1>{player.firstName}<br />{player.lastName}</h1><h2>{player.position ?? "Position unavailable"}</h2><p>{formatHeight(player.height)} · {player.weight ? `${player.weight} lbs` : "—"} · {classLabel(player.year)}<br />{[player.homeCity, player.homeState].filter(Boolean).join(", ") || "Hometown unavailable"}</p></div><div className="player-fallback"><TeamLogo teamId={130} name="Michigan" size={256} /><strong>{player.jersey ?? "M"}</strong><span>MICHIGAN PLAYER PROFILE</span></div><div className="player-grade-row"><GradeBadge label="Performance" valueType="ACTUAL" grade={player.performanceGrade} /><GradeBadge label="Prospect" valueType="BENCHMARK" grade={player.prospectGrade} /><GradeBadge label="Potential" valueType="PROJECTED" grade={player.potentialGrade} /></div></section>;
}

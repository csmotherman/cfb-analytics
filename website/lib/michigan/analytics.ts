import { michiganSeason, rank } from "../michigan";
export function latestActualProfile() {
  const team = michiganSeason(2025);
  return team ? { season: 2025, team, offensiveRank: rank(team, "successRate"), defensiveRank: rank(team, "successRateAllowed") } : null;
}

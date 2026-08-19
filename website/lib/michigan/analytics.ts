import { michiganSeason, rank } from "../michigan";
import { readJson } from "../server-data";
export function latestActualProfile() {
  const team = michiganSeason(2025);
  return team ? { season: 2025, team, offensiveRank: rank(team, "successRate"), defensiveRank: rank(team, "successRateAllowed") } : null;
}

export type AnalyticsStoryTeam = {team:string;rushAttempts:number;dropbacks:number;designedBalanceRushShare:number;rushSuccessRate:number;rushYardsPerAttempt:number;rushExplosivePlayRate:number;successRate:number;successRateNationalRank:number;thirdDownConversionRate:number;fourthDownConversionRate:number;pointsPerOpportunity:number;pointsPerOpportunityNationalRank:number;pointsPerResolvedPossession:number;pointsPerResolvedPossessionNationalRank:number};
export type AnalyticsStory = {season:number;valueType:"ACTUAL";comparisonType:"STAFF_CONTEXT";teams:{michigan:AnalyticsStoryTeam;utah:AnalyticsStoryTeam};michiganDefense:{explosivePlayRateAllowed:number;explosivePlayRateAllowedNationalRank:number;yardsPerSuccessfulPlayAllowed:number;yardsPerSuccessfulPlayAllowedNationalRank:number;pointsPerResolvedPossessionAllowed:number;pointsPerResolvedPossessionAllowedNationalRank:number};interpretation:{michigan:string;utah:string;boundary:string}};
export function analyticsStory(){return readJson<AnalyticsStory>("data","published","2026","michigan","analytics-story.json")}

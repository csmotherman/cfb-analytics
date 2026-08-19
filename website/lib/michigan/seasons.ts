import { siteConfig } from "../site-config";
export const supportedSeasons = Array.from({ length: siteConfig.currentSeason - siteConfig.historyStart + 1 }, (_, index) => siteConfig.currentSeason - index);
export function seasonValueType(season: number) { return season === siteConfig.currentSeason ? "PRESEASON" as const : "ACTUAL" as const; }

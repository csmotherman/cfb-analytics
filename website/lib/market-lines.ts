import { readJson } from "./server-data";
export type MarketLine={gameId:string;opponent:string;sportsbook:string;teamSpread:number;marketWinChance:number;valueType:"MARKET";asOf:string;source:{name:string;url:string};probabilityMethod:string};
type Publication={season:number;team:string;valueType:"MARKET";games:MarketLine[]};
export function marketLines(){return readJson<Publication>("data","published","2026","michigan","market-lines.json")?.games??[]}
export function marketLineFor(gameId:number|string){return marketLines().find(line=>line.gameId===String(gameId))??null}
export function formatMichiganSpread(spread:number){return `Michigan ${spread>0?"+":""}${spread}`}

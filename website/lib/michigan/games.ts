import { readJson } from "../server-data";
import type { MichiganScheduleGame } from "./types";

export function currentSchedule(): MichiganScheduleGame[] {
  return (readJson<MichiganScheduleGame[]>("data", "published", "2026", "michigan", "schedule.json") ?? [])
    .sort((a, b) => a.week - b.week);
}

export function gameById(id: string): MichiganScheduleGame | null {
  return currentSchedule().find((game) => String(game.id) === id) ?? null;
}

export function nextGame(): MichiganScheduleGame | null {
  return currentSchedule().find((game) => !game.completed) ?? null;
}

export function opponent(game: MichiganScheduleGame) {
  return game.homeId === 130
    ? { id: game.awayId, name: game.awayTeam }
    : { id: game.homeId, name: game.homeTeam };
}

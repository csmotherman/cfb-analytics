// Hand-populated primary/secondary brand colors, keyed by CFBD numeric team
// id -- only Michigan plus its realistic 2025/2026 opponents, not all ~136
// FBS teams. Unmapped teams fall back to a neutral gray rather than
// guessing a color, per the same "don't invent data" discipline applied
// everywhere else in this repo.
export type TeamColorPair = { primary: string; secondary: string };

const FALLBACK: TeamColorPair = { primary: "#6b7280", secondary: "#9ca3af" };

export const TEAM_COLORS: Record<number, TeamColorPair> = {
  130: { primary: "#00274C", secondary: "#FFCB05" }, // Michigan
  2711: { primary: "#532E1F", secondary: "#F1C500" }, // Western Michigan
  167: { primary: "#BA0C2F", secondary: "#A7A8AA" }, // New Mexico
  251: { primary: "#BF5700", secondary: "#333F48" }, // Texas
  201: { primary: "#841617", secondary: "#FDF9D8" }, // Oklahoma
  2117: { primary: "#6C1D45", secondary: "#EAAA00" }, // Central Michigan
  158: { primary: "#E41C38", secondary: "#F8F1E9" }, // Nebraska
  275: { primary: "#C5050C", secondary: "#DADFE1" }, // Wisconsin
  30: { primary: "#990000", secondary: "#FFC72C" }, // USC
  264: { primary: "#4B2E83", secondary: "#B7A57A" }, // Washington
  127: { primary: "#18453B", secondary: "#FFFFFF" }, // Michigan State
  2509: { primary: "#CEB888", secondary: "#000000" }, // Purdue
  77: { primary: "#4E2A84", secondary: "#FFFFFF" }, // Northwestern
  120: { primary: "#E21833", secondary: "#FFD200" }, // Maryland
  194: { primary: "#BB0000", secondary: "#666666" }, // Ohio State
};

export function teamColors(teamId: number | null | undefined): TeamColorPair {
  if (teamId == null) return FALLBACK;
  return TEAM_COLORS[teamId] ?? FALLBACK;
}

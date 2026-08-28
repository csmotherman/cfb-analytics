import { TeamLogo } from "../../ui/TeamLogo";
import { teamColors } from "../../../lib/team-colors";
import type { DriveResult } from "../../../lib/creator-hub/game-story";
import { Visual16x9Frame } from "./Visual16x9Frame";

const RESULT_LABEL: Record<string, string> = {
  TOUCHDOWN: "TD", FIELD_GOAL: "FG", PUNT: "Punt", INTERCEPTION: "INT",
  FUMBLE: "Fumble", TURNOVER_ON_DOWNS: "Downs", MISSED_FIELD_GOAL: "Missed FG",
  TURNOVER_SCORE: "Pick-6 / Fumble TD", SAFETY: "Safety",
  END_OF_HALF: "End of half", END_OF_GAME: "End of game", UNKNOWN: "--",
};
const SCORING_RESULTS = new Set(["TOUCHDOWN", "FIELD_GOAL"]);

export function DriveMap({
  drives,
  michiganTeamId,
  opponentTeamId,
  opponentName,
}: {
  drives: DriveResult[];
  michiganTeamId: number | null;
  opponentTeamId: number | null;
  opponentName: string;
}) {
  const shown = drives.filter((d) => d.result !== "END_OF_HALF" && d.result !== "END_OF_GAME");
  return (
    <Visual16x9Frame title="Drive-by-drive" source="SOAR Analytics · drive-result-inferred-v1">
      <div className="ch-drivemap">
        {shown.map((drive) => {
          const isMichigan = drive.offense === "Michigan";
          const teamId = isMichigan ? michiganTeamId : opponentTeamId;
          const colors = teamColors(teamId);
          const scored = SCORING_RESULTS.has(drive.result);
          return (
            <div key={drive.driveNumber} className={`ch-drivemap-row${scored ? " scored" : ""}`} style={{ borderColor: colors.primary }}>
              {teamId != null && <TeamLogo teamId={teamId} name={isMichigan ? "Michigan" : opponentName} size={64} className="ch-drivemap-logo" />}
              <span className="ch-drivemap-start">Own {drive.startYardsToGoal != null ? 100 - drive.startYardsToGoal : "?"}</span>
              <div className="ch-drivemap-bar" style={{ background: colors.primary, width: `${Math.min(((drive.yardsGained ?? 0) / 90) * 100, 100)}%` }} />
              <span className="ch-drivemap-yards">{drive.yardsGained ?? "?"} yds</span>
              <span className={`ch-drivemap-result${scored ? " scored" : ""}`}>{RESULT_LABEL[drive.result] ?? drive.result}</span>
            </div>
          );
        })}
      </div>
    </Visual16x9Frame>
  );
}

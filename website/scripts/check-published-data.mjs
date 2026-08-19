import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const repositoryRoot = path.resolve(process.cwd(), "..");
const requiredArtifacts = [
  "data/published/2026/michigan/roster.json",
  "data/published/2026/michigan/schedule.json",
  "data/published/2026/michigan/recruiting.json",
  "data/published/2026/michigan/projected-lineup.json",
  "data/published/2026/michigan/game-predictions.json",
  "data/published/2026/michigan/outlook.json",
  "data/published/2026/recruiting/players.json",
  "data/published/2026/recruiting/teams.json",
];

const failures = [];
const parsedArtifacts = new Map();
for (const relativePath of requiredArtifacts) {
  const file = path.join(repositoryRoot, relativePath);
  if (!fs.existsSync(file)) {
    failures.push(`${relativePath}: missing`);
    continue;
  }
  try {
    parsedArtifacts.set(relativePath, JSON.parse(fs.readFileSync(file, "utf8")));
  } catch (error) {
    failures.push(`${relativePath}: invalid JSON (${error instanceof Error ? error.message : String(error)})`);
  }
}

const requireArray = (relativePath) => {
  const value = parsedArtifacts.get(relativePath);
  if (!Array.isArray(value) || value.length === 0) failures.push(`${relativePath}: expected a non-empty JSON array`);
  return Array.isArray(value) ? value : [];
};
const roster = requireArray("data/published/2026/michigan/roster.json");
requireArray("data/published/2026/michigan/schedule.json");
requireArray("data/published/2026/recruiting/players.json");
requireArray("data/published/2026/recruiting/teams.json");
const recruiting = parsedArtifacts.get("data/published/2026/michigan/recruiting.json");
if (!recruiting || recruiting.valueType !== "BENCHMARK" || !Array.isArray(recruiting.recruits)) {
  failures.push("data/published/2026/michigan/recruiting.json: invalid BENCHMARK recruiting contract");
}

const lineup = parsedArtifacts.get("data/published/2026/michigan/projected-lineup.json");
const rosterIds = new Set(roster.map((player) => String(player.id)));
if (!lineup || lineup.version !== "michigan-preseason-lineup-v1" || lineup.valueType !== "PROJECTED") {
  failures.push("data/published/2026/michigan/projected-lineup.json: invalid version or valueType");
} else {
  const offense = Array.isArray(lineup.offense) ? lineup.offense : [];
  const defense = Array.isArray(lineup.defense) ? lineup.defense : [];
  const playerIds = [...offense, ...defense].map((slot) => String(slot.playerId));
  if (offense.length !== 11 || defense.length !== 11) failures.push("data/published/2026/michigan/projected-lineup.json: expected 11 offense and 11 defense slots");
  if (new Set(playerIds).size !== playerIds.length) failures.push("data/published/2026/michigan/projected-lineup.json: duplicate projected player IDs");
  const missingPlayers = playerIds.filter((playerId) => !rosterIds.has(playerId));
  if (missingPlayers.length) failures.push(`data/published/2026/michigan/projected-lineup.json: player IDs absent from roster (${missingPlayers.join(", ")})`);
}

const predictions = parsedArtifacts.get("data/published/2026/michigan/game-predictions.json");
if (!predictions || predictions.valueType !== "PROJECTED" || predictions.probabilityStatus !== "NOT_CALIBRATED" || !Array.isArray(predictions.games)) {
  failures.push("data/published/2026/michigan/game-predictions.json: invalid projected prediction contract");
} else if (predictions.games.some((game) => game.winProbability !== null || !Number.isFinite(game.predictedHomeMargin))) {
  failures.push("data/published/2026/michigan/game-predictions.json: invalid margin or invented win probability");
}
const outlook = parsedArtifacts.get("data/published/2026/michigan/outlook.json");
if (!outlook || outlook.valueType !== "BENCHMARK" || !Number.isFinite(outlook.cfp?.noVigImpliedProbability) || outlook.cfp.noVigImpliedProbability < 0 || outlook.cfp.noVigImpliedProbability > 1) {
  failures.push("data/published/2026/michigan/outlook.json: invalid market benchmark contract");
}

for (const manifestName of ["manifest.json", "recruiting-manifest.json"]) {
  const manifestPath = path.join(repositoryRoot, "data", "published", "2026", "michigan", manifestName);
  if (!fs.existsSync(manifestPath)) {
    failures.push(`data/published/2026/michigan/${manifestName}: missing`);
    continue;
  }
  try {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    for (const [artifactName, expectedHash] of Object.entries(manifest.artifacts ?? {})) {
      const artifactPath = path.join(path.dirname(manifestPath), artifactName);
      if (!fs.existsSync(artifactPath)) {
        failures.push(`data/published/2026/michigan/${manifestName}: missing declared artifact ${artifactName}`);
        continue;
      }
      const actualHash = crypto.createHash("sha256").update(fs.readFileSync(artifactPath)).digest("hex");
      if (actualHash !== expectedHash) failures.push(`data/published/2026/michigan/${manifestName}: hash mismatch for ${artifactName}`);
    }
  } catch (error) {
    failures.push(`data/published/2026/michigan/${manifestName}: invalid manifest (${error instanceof Error ? error.message : String(error)})`);
  }
}

if (failures.length) {
  process.stderr.write(`Published-data verification failed:\n${failures.map((failure) => `- ${failure}`).join("\n")}\n`);
  process.exitCode = 1;
} else {
  process.stdout.write(`Verified ${requiredArtifacts.length} required published artifacts.\n`);
}

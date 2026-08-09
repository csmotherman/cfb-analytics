# Raw CFBD Source Field Catalog

This catalog is based on the validated raw corpus structure observed during Phase 1. The `cfb-raw census` command is the authoritative way to detect field/value drift across all seasons.

## Games

Observed fields:

`id, season, week, seasonType, startDate, startTimeTBD, completed, neutralSite, conferenceGame, attendance, venueId, venue, homeId, homeTeam, homeClassification, homeConference, homePoints, homeLineScores, homePostgameWinProbability, homePregameElo, homePostgameElo, awayId, awayTeam, awayClassification, awayConference, awayPoints, awayLineScores, awayPostgameWinProbability, awayPregameElo, awayPostgameElo, excitementIndex, highlights, notes, playoff`

Primary source key: `id`.

## Drives

Observed fields:

`id, gameId, offense, offenseConference, defense, defenseConference, driveNumber, scoring, startPeriod, startYardline, startYardsToGoal, startTime, endPeriod, endYardline, endYardsToGoal, endTime, elapsed, plays, yards, driveResult, isHomeOffense, startOffenseScore, startDefenseScore, endOffenseScore, endDefenseScore`

Primary source key: `id`.
Foreign key: `gameId -> games.id`.

`driveResult` is a source category. We must census every historical value before designing canonical enums or derived drive-outcome logic.

## Plays

Observed fields:

`gameId, driveId, id, driveNumber, playNumber, offense, offenseConference, offenseScore, defense, defenseConference, defenseScore, home, away, period, clock, offenseTimeouts, defenseTimeouts, yardline, yardsToGoal, down, distance, yardsGained, scoring, playType, playText, ppa, wallclock`

Primary source key: `id`.
Foreign keys: `gameId -> games.id`, `driveId -> drives.id`.

`playType` is a source category, not our final football classification. We must preserve it and profile every value before deciding how events map to competitive snaps, runs, passes, penalties, special teams, or administrative events.

## Important principle

A source field being present does not mean it is always semantically reliable for every historical season. Phase 2 must examine distributions, nulls, ranges, and cross-field consistency before any field becomes authoritative for a derived football concept.

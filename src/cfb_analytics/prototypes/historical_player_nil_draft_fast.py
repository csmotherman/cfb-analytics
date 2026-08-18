"""Efficient real-data runner for the player/NIL challenge.

The statistical contract lives in :mod:`historical_player_nil_draft`. This runner
keeps acquisition bounded by fetching player stats for the top historical teams in
each season and uses a two-stage matchup calibration:

1. seven-player roster power -> historical team SRS using team-seasons with complete
   player lineups;
2. historical SRS difference -> actual FBS game margin using the full completed-game
   sample.

Because only roster-power *differences* enter the final matchup, the intercept from
stage one cancels. A user roster with the same player power as 2019 LSU is exactly
50% on a neutral field; stronger player power always improves the expected margin.
"""
from __future__ import annotations

import math
from typing import Any

from cfb_analytics.prototypes import historical_player_nil_draft as base
from cfb_analytics.sources.cfbd.client import CfbdClient

TOP_TEAMS_PER_SEASON = 10


def efficient_best_unique_lineup(candidates: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]] | None:
    lineup: dict[str, dict[str, Any]] = {}
    for slot in ("QB", "DL", "LB", "DB"):
        options = sorted(candidates.get(slot, []), key=lambda p: float(p["powerZ"]), reverse=True)
        if not options:
            return None
        lineup[slot] = options[0]

    rb = sorted(candidates.get("RB", []), key=lambda p: float(p["powerZ"]), reverse=True)[:12]
    wr = sorted(candidates.get("WR", []), key=lambda p: float(p["powerZ"]), reverse=True)[:12]
    flex = sorted(candidates.get("FLEX", []), key=lambda p: float(p["powerZ"]), reverse=True)[:16]
    if not rb or not wr or not flex:
        return None

    best_score = -float("inf")
    best_skill: tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None = None
    for rb_player in rb:
        rb_id = str(rb_player["playerSeasonId"])
        for wr_player in wr:
            wr_id = str(wr_player["playerSeasonId"])
            if wr_id == rb_id:
                continue
            for flex_player in flex:
                flex_id = str(flex_player["playerSeasonId"])
                if flex_id in {rb_id, wr_id}:
                    continue
                score = (
                    base.SLOT_WEIGHTS["RB"] * float(rb_player["powerZ"])
                    + base.SLOT_WEIGHTS["WR"] * float(wr_player["powerZ"])
                    + base.SLOT_WEIGHTS["FLEX"] * float(flex_player["powerZ"])
                )
                if score > best_score:
                    best_score = score
                    best_skill = (rb_player, wr_player, flex_player)
    if best_skill is None:
        return None
    lineup["RB"], lineup["WR"], lineup["FLEX"] = best_skill
    return lineup


def _srs_for_season(client: CfbdClient, season: int, metadata: dict[str, dict[str, Any]]) -> tuple[list[str], dict[str, float]]:
    payload = client.get_json("/ratings/srs", {"year": season}).payload
    ratings: list[tuple[float, str]] = []
    if isinstance(payload, list):
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            team = str(raw.get("team") or "").strip()
            rating = base._number(raw.get("rating"))
            if team and rating is not None and team in metadata:
                ratings.append((float(rating), team))
    ratings.sort(reverse=True)
    top = [team for _, team in ratings[:TOP_TEAMS_PER_SEASON]]
    if season == base.TARGET_SEASON and base.TARGET_TEAM not in top:
        top = top[:-1] + [base.TARGET_TEAM]
    return top, {team: rating for rating, team in ratings}


def fit_two_stage_margin_calibration(
    team_lineups: dict[str, dict[str, Any]],
    srs_by_key: dict[str, float],
    games: list[dict[str, Any]],
) -> dict[str, Any]:
    pairs: list[tuple[float, float]] = []
    for key, record in team_lineups.items():
        srs = srs_by_key.get(key)
        if srs is not None:
            pairs.append((float(record["composite"]), float(srs)))
    if len(pairs) < 60:
        raise ValueError(f"Not enough player-lineup team-seasons for roster-power calibration: {len(pairs)}")

    mx = sum(x for x, _ in pairs) / len(pairs)
    my = sum(y for _, y in pairs) / len(pairs)
    var = sum((x - mx) ** 2 for x, _ in pairs)
    cov = sum((x - mx) * (y - my) for x, y in pairs)
    power_to_srs = cov / var if var > 0 else 0.0
    if power_to_srs <= 0:
        raise ValueError(f"Player roster power must positively map to SRS, got {power_to_srs}")
    intercept = my - power_to_srs * mx
    srs_errors = [y - (intercept + power_to_srs * x) for x, y in pairs]
    srs_rmse = math.sqrt(sum(e * e for e in srs_errors) / len(srs_errors))
    ss_tot = sum((y - my) ** 2 for _, y in pairs)
    ss_res = sum(e * e for e in srs_errors)
    srs_r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    margin_rows: list[tuple[float, float, float]] = []
    for game in games:
        if not isinstance(game, dict) or not game.get("completed"):
            continue
        if str(game.get("homeClassification") or "").casefold() != "fbs" or str(game.get("awayClassification") or "").casefold() != "fbs":
            continue
        season = game.get("season")
        home = game.get("homeTeam")
        away = game.get("awayTeam")
        hp = base._number(game.get("homePoints"))
        ap = base._number(game.get("awayPoints"))
        if season is None or not home or not away or hp is None or ap is None:
            continue
        hs = srs_by_key.get(f"{int(season)}::{home}")
        aws = srs_by_key.get(f"{int(season)}::{away}")
        if hs is None or aws is None:
            continue
        margin_rows.append((float(hs) - float(aws), 0.0 if bool(game.get("neutralSite")) else 1.0, hp - ap))
    if len(margin_rows) < 1000:
        raise ValueError(f"Not enough SRS-backed completed FBS games: {len(margin_rows)}")

    a11 = sum(x1 * x1 for x1, _, _ in margin_rows)
    a12 = sum(x1 * x2 for x1, x2, _ in margin_rows)
    a22 = sum(x2 * x2 for _, x2, _ in margin_rows)
    b1 = sum(x1 * y for x1, _, y in margin_rows)
    b2 = sum(x2 * y for _, x2, y in margin_rows)
    solved = base._solve_2x2(a11, a12, a22, b1, b2)
    if solved is None:
        raise ValueError("SRS-to-margin calibration is singular")
    srs_to_margin, hfa = solved
    if srs_to_margin <= 0:
        raise ValueError(f"SRS-to-margin scale must be positive, got {srs_to_margin}")
    residuals = [y - (srs_to_margin * x1 + hfa * x2) for x1, x2, y in margin_rows]
    residual_sd = math.sqrt(sum(e * e for e in residuals) / len(residuals))

    return {
        "version": "historical-player-roster-srs-margin-v2",
        "games": len(margin_rows),
        "playerTeamSeasons": len(pairs),
        "rosterPowerToSrsScale": power_to_srs,
        "rosterPowerToSrsIntercept": intercept,
        "rosterPowerToSrsRmse": srs_rmse,
        "rosterPowerToSrsR2": srs_r2,
        "srsToMarginScale": srs_to_margin,
        "homeFieldPoints": hfa,
        "rosterPowerToMargin": power_to_srs * srs_to_margin,
        "residualSd": residual_sd,
        "neutralFieldRule": "expected margin = rosterPowerToMargin * (challengerRosterPower - LSU2019RosterPower)",
    }


def targeted_build_dataset(
    client: CfbdClient,
    *,
    seasons: tuple[int, ...] = base.DEFAULT_SEASONS,
    simulations: int = 5000,
    seed: int = 2019,
) -> dict[str, Any]:
    metadata = base._team_metadata(client.teams().payload)
    all_players: list[dict[str, Any]] = []
    all_games: list[dict[str, Any]] = []
    srs_by_key: dict[str, float] = {}
    source_status: dict[str, Any] = {}

    for season in seasons:
        teams, srs_map = _srs_for_season(client, season, metadata)
        srs_by_key.update({f"{season}::{team}": rating for team, rating in srs_map.items()})
        season_players: list[dict[str, Any]] = []
        raw_rows = 0
        for team in teams:
            player_payload = client.get_json(
                "/stats/player/season",
                {"year": season, "team": team, "seasonType": "both"},
            ).payload
            if isinstance(player_payload, list):
                raw_rows += len(player_payload)
            season_players.extend(base.aggregate_player_stats(season, player_payload, metadata))

        games_payload = base._fetch_optional(client, "/games", {"year": season, "seasonType": "both", "classification": "fbs"})
        all_players.extend(season_players)
        if isinstance(games_payload, list):
            all_games.extend(game for game in games_payload if isinstance(game, dict))
        source_status[str(season)] = {
            "teamsFetched": teams,
            "teamCount": len(teams),
            "playerStatRows": raw_rows,
            "playerSeasons": len(season_players),
            "srsTeams": len(srs_map),
            "games": len(games_payload) if isinstance(games_payload, list) else 0,
        }
        print(f"season={season} teams={len(teams)} playerRows={raw_rows} players={len(season_players)}", flush=True)

    base.score_players(all_players)
    base.assign_nil_prices(all_players)
    slot_pools = base.build_slot_pools(all_players)
    team_lineups = base.build_team_lineups(all_players)
    boss_record = team_lineups.get(f"{base.TARGET_SEASON}::{base.TARGET_TEAM}")
    if not boss_record:
        raise ValueError("Could not construct complete 2019 LSU seven-player boss roster")
    boss_lineup = boss_record["lineup"]
    calibration = fit_two_stage_margin_calibration(team_lineups, srs_by_key, all_games)
    difficulty = base.benchmark_budgets(slot_pools, boss_lineup, calibration, simulations=simulations, seed=seed)
    budget = float(difficulty["selectedBudgetMillions"])

    return {
        "schemaVersion": 1,
        "challengeVersion": base.CHALLENGE_VERSION,
        "status": "data-prototype-playable",
        "title": f"Can ${budget:g}M in NIL Beat the 2019 LSU Tigers?",
        "subtitle": "Seven historical stars. One fictional SOAR NIL budget. Beat Burrow's Tigers.",
        "seasons": list(seasons),
        "excludedSeasons": list(base.EXCLUDED_SEASONS),
        "target": {
            "season": base.TARGET_SEASON,
            "team": base.TARGET_TEAM,
            "rosterPower": boss_record["composite"],
            "lineup": {slot: {**boss_lineup[slot], "bossSlot": slot} for slot in base.SLOT_ORDER},
            "logo": metadata.get(base.TARGET_TEAM, {}).get("logo"),
            "conference": metadata.get(base.TARGET_TEAM, {}).get("conference"),
        },
        "rules": {
            "budgetMillions": budget,
            "requiredPlayers": len(base.SLOT_ORDER),
            "slots": list(base.SLOT_ORDER),
            "slotWeights": base.SLOT_WEIGHTS,
            "offersPerSlot": base.OFFERS_PER_SLOT,
            "maxOffers": base.OFFERS_PER_SLOT * len(base.SLOT_ORDER),
            "passRule": "Each roster slot can pass its first portal offer once; the second offer for that slot is final.",
            "winThreshold": base.WIN_THRESHOLD,
            "site": "neutral",
            "nilDisclaimer": "SOAR NIL asks are fictional game values derived from historical production and position scarcity. They are not real or historical NIL valuations.",
        },
        "grading": {
            "version": "era-adjusted-player-percentile-v1",
            "description": "Player metrics are ranked against same-season peers at the offered roster slot, combined by fixed position-specific weights, then converted to a cross-season percentile and 1-99 SOAR grade.",
            "metricWeights": base.METRIC_WEIGHTS,
        },
        "nilPricing": {
            "version": "soar-fictional-nil-ask-v1",
            "priceBandsMillions": base.NIL_PRICE_BANDS,
            "description": "Price blends player grade, position premium, and raw star-volume percentile to create strategic bargains; values are fictional gameplay currency.",
        },
        "matchupCalibration": calibration,
        "difficultyBenchmark": difficulty,
        "slotPools": slot_pools,
        "sourceStatus": source_status,
        "dataNotes": [
            "Only completed historical season production is used.",
            "The portal pool is sourced from the top 10 SRS FBS teams in each supported season to keep offers star-focused and acquisition bounded.",
            "Player roster power is first calibrated to team SRS; SRS differences are then calibrated to the full completed FBS game-margin sample.",
            "2020 is excluded to match the existing SOAR historical support policy.",
            "Defensive grades are production-based statistical ratings, not film/scouting grades.",
            "The game is separate from Prediction-v2 and does not alter any prospective model artifact.",
            "Difficulty is calibrated by pre-user simulation only; user outcomes are not used to tune the budget.",
        ],
    }


base._best_unique_lineup = efficient_best_unique_lineup
base.build_dataset = targeted_build_dataset


if __name__ == "__main__":
    base.main()

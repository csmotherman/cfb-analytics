"""Efficient real-data runner for the player/NIL challenge.

The statistical contract lives in :mod:`historical_player_nil_draft`. This runner
changes only acquisition/assignment mechanics for the one-time historical build:

* fetch player stats for the top 12 SRS FBS teams in each supported season instead
  of one enormous unfiltered player-season payload;
* solve the only overlapping lineup slots (RB/WR/FLEX) exactly while selecting
  QB/DL/LB/DB independently.

The public grades, NIL pricing, matchup calibration and difficulty rules remain the
same as the base module.
"""
from __future__ import annotations

from typing import Any

from cfb_analytics.prototypes import historical_player_nil_draft as base
from cfb_analytics.sources.cfbd.client import CfbdClient

TOP_TEAMS_PER_SEASON = 12


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


def _top_srs_teams(client: CfbdClient, season: int, metadata: dict[str, dict[str, Any]]) -> list[str]:
    payload = client.get_json("/ratings/srs", {"year": season}).payload
    ranked: list[tuple[float, str]] = []
    if isinstance(payload, list):
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            team = str(raw.get("team") or "").strip()
            rating = base._number(raw.get("rating"))
            if team and rating is not None and team in metadata:
                ranked.append((rating, team))
    ranked.sort(reverse=True)
    teams = [team for _, team in ranked[:TOP_TEAMS_PER_SEASON]]
    if season == base.TARGET_SEASON and base.TARGET_TEAM not in teams:
        teams = teams[:-1] + [base.TARGET_TEAM]
    return teams


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
    source_status: dict[str, Any] = {}

    for season in seasons:
        teams = _top_srs_teams(client, season, metadata)
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

        games_payload = base._fetch_optional(
            client,
            "/games",
            {"year": season, "seasonType": "both", "classification": "fbs"},
        )
        all_players.extend(season_players)
        if isinstance(games_payload, list):
            all_games.extend(game for game in games_payload if isinstance(game, dict))
        source_status[str(season)] = {
            "teamsFetched": teams,
            "teamCount": len(teams),
            "playerStatRows": raw_rows,
            "playerSeasons": len(season_players),
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
    calibration = base.fit_margin_calibration(all_games, team_lineups)
    difficulty = base.benchmark_budgets(
        slot_pools,
        boss_lineup,
        calibration,
        simulations=simulations,
        seed=seed,
    )
    budget = float(difficulty["selectedBudgetMillions"])

    boss_compact = {
        slot: {**boss_lineup[slot], "bossSlot": slot}
        for slot in base.SLOT_ORDER
    }
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
            "lineup": boss_compact,
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
            "The player pool is sourced from the top 12 SRS FBS teams in each supported season to keep the wheel star-focused and the data build bounded.",
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

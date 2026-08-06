"""CollegeFootballData play-by-play functions."""

from __future__ import annotations

from typing import Any

from src.api.client import get_json


def get_game_pbp(game_id: str | int) -> dict[str, Any]:
    """Download CFBD game, drive, and play records for one game."""

    game_id_text = str(game_id).strip()
    if not game_id_text:
        raise ValueError("game_id cannot be empty")

    game_id_value = int(game_id_text)

    games = get_json("games", params={"id": game_id_value})
    drives = get_json("drives", params={"gameId": game_id_value})
    plays = get_json("plays", params={"gameId": game_id_value})

    if not isinstance(games, list):
        raise TypeError("CFBD /games response must be a JSON array")
    if not isinstance(drives, list):
        raise TypeError("CFBD /drives response must be a JSON array")
    if not isinstance(plays, list):
        raise TypeError("CFBD /plays response must be a JSON array")

    if len(games) != 1:
        raise ValueError(
            f"Expected one CFBD game for {game_id_value}, received {len(games)}"
        )

    return {
        "id": game_id_value,
        "game": games[0],
        "drives": drives,
        "plays": plays,
    }

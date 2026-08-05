"""SportRadar play-by-play functions."""

from __future__ import annotations

from typing import Any

from src.api.client import get_json


def get_game_pbp(game_id: str) -> dict[str, Any]:
    """Download the complete play-by-play JSON for one game."""

    if not game_id or not game_id.strip():
        raise ValueError("game_id cannot be empty")

    return get_json(
        f"games/{game_id.strip()}/pbp.json"
    )
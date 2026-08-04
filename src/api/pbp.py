from src.api.client import get


def get_game_pbp(game_id: str):
    """
    Download one game's play-by-play JSON.
    """

    return get(
        f"games/{game_id}/pbp.json"
    )
"""DuckDB table metadata."""

from __future__ import annotations

TABLE_PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "games": ("game_id",),
    "periods": ("period_id",),
    "drives": ("drive_id",),
    "plays": ("play_id",),
    "play_statistics": (
        "play_id",
        "statistic_index",
    ),
    "play_events": ("event_id",),
    "event_players": (
        "event_id",
        "event_player_index",
    ),
}

TABLE_ORDER = (
    "games",
    "periods",
    "drives",
    "plays",
    "play_statistics",
    "play_events",
    "event_players",
)


def quoted_identifier(value: str) -> str:
    """Safely quote a DuckDB table or column identifier."""

    return '"' + value.replace('"', '""') + '"'
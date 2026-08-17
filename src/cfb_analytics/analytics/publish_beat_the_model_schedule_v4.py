"""Beat the Model live scheduler v4 team presentation metadata.

This layer keeps the v3 market-aware slate and adds FBS team identity fields from
CFBD /teams. Ranking order, slate selection, and Prediction-v2 are unchanged.
Logos and brand metadata are presentation-only and may fail open without blocking
the weekly contest.
"""
from __future__ import annotations

from typing import Any

from cfb_analytics.analytics import publish_beat_the_model_schedule as base
from cfb_analytics.analytics import publish_beat_the_model_schedule_v3 as market_v3  # noqa: F401
from cfb_analytics.sources.cfbd.client import CfbdError

LIVE_SCHEDULE_VERSION = "beat-the-model-live-schedule-v4"
TEAM_METADATA_SOURCE_VERSION = "cfbd-teams-v1"

TEAM_METADATA_FIELDS = (
    "teamId",
    "abbreviation",
    "conference",
    "color",
    "alternateColor",
    "logo",
)

_original_build_week_rankings = base.build_week_rankings
_original_select_slate = base.select_slate


def team_metadata_from_payload(payload: Any) -> dict[str, dict[str, Any]]:
    """Normalize CFBD TeamsApi rows and retain FBS teams only."""
    if not isinstance(payload, list):
        raise ValueError("Unexpected CFBD teams payload")

    out: dict[str, dict[str, Any]] = {}
    for raw in payload:
        if not isinstance(raw, dict):
            continue
        if str(raw.get("classification") or "").lower() != "fbs":
            continue
        school = raw.get("school")
        if not isinstance(school, str) or not school.strip():
            continue

        logos = raw.get("logos")
        logo = None
        if isinstance(logos, list):
            logo = next(
                (value.strip() for value in logos if isinstance(value, str) and value.strip()),
                None,
            )

        out[school.strip()] = {
            "teamId": raw.get("id"),
            "abbreviation": raw.get("abbreviation"),
            "conference": raw.get("conference"),
            "color": raw.get("color"),
            "alternateColor": raw.get("alternateColor", raw.get("alternate_color")),
            "logo": logo,
        }
    return out


def fetch_team_metadata(client: Any) -> dict[str, dict[str, Any]]:
    method = getattr(client, "teams", None)
    if not callable(method):
        return {}
    response = method()
    return team_metadata_from_payload(response.payload)


def enrich_rankings(
    rankings: dict[str, Any],
    team_metadata: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Attach presentation metadata without changing rank or power rating."""
    payload = dict(rankings)
    rows: list[dict[str, Any]] = []
    for raw in rankings.get("teams", []):
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        metadata = team_metadata.get(str(row.get("team")), {})
        for field in TEAM_METADATA_FIELDS:
            value = metadata.get(field)
            if value is not None:
                row[field] = value
        rows.append(row)
    payload["teams"] = rows
    payload["teamMetadataSource"] = TEAM_METADATA_SOURCE_VERSION
    payload["teamMetadataStatus"] = "ok" if team_metadata else "unavailable"
    return payload


def enrich_selected_games(
    games: list[dict[str, Any]],
    rankings: dict[str, Any],
    existing_current: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Copy team identity fields from ranking rows onto each public game card."""
    by_team = {
        str(row.get("team")): row
        for row in rankings.get("teams", [])
        if isinstance(row, dict) and row.get("team")
    }
    existing_by_id = {
        str(row.get("id")): row
        for row in (existing_current or {}).get("games", [])
        if isinstance(row, dict) and row.get("id") is not None
    }

    out: list[dict[str, Any]] = []
    for raw in games:
        game = dict(raw)
        existing = existing_by_id.get(str(game.get("id")), {})
        home = by_team.get(str(game.get("homeTeam")), {})
        away = by_team.get(str(game.get("awayTeam")), {})

        for side, row in (("home", home), ("away", away)):
            field_map = {
                f"{side}TeamId": "teamId",
                f"{side}Abbreviation": "abbreviation",
                f"{side}Conference": "conference",
                f"{side}Color": "color",
                f"{side}AlternateColor": "alternateColor",
                f"{side}Logo": "logo",
            }
            for public_field, ranking_field in field_map.items():
                value = row.get(ranking_field)
                if value is None:
                    value = existing.get(public_field)
                game[public_field] = value
        out.append(game)
    return out


def build_week_rankings(
    client: Any,
    data_root: Any,
    *,
    season: int,
    week: int,
) -> dict[str, Any]:
    rankings = _original_build_week_rankings(
        client,
        data_root,
        season=season,
        week=week,
    )
    try:
        metadata = fetch_team_metadata(client)
    except (CfbdError, ValueError, AttributeError):
        metadata = {}
    return enrich_rankings(rankings, metadata)


def select_slate(
    schedule: list[dict[str, Any]],
    rankings: dict[str, Any],
    *,
    existing_current: dict[str, Any],
    model_by_id: dict[str, dict[str, Any]],
    market_by_id: dict[str, dict[str, Any]] | None = None,
    market_snapshot_at: str | None = None,
) -> list[dict[str, Any]]:
    games = _original_select_slate(
        schedule,
        rankings,
        existing_current=existing_current,
        model_by_id=model_by_id,
        market_by_id=market_by_id,
        market_snapshot_at=market_snapshot_at,
    )
    return enrich_selected_games(games, rankings, existing_current)


def install() -> None:
    base.LIVE_SCHEDULE_VERSION = LIVE_SCHEDULE_VERSION
    base.build_week_rankings = build_week_rankings
    base.select_slate = select_slate


install()


def main() -> None:
    base.main()


if __name__ == "__main__":
    main()

"""Canonical play normalization.

Canonical records preserve source values and add analytics-safe fields. Raw
records are never modified in place.
"""
from __future__ import annotations

from typing import Any

from cfb_analytics.canonical.play_types import classify_play_type


def normalize_play(source: dict[str, Any]) -> dict[str, Any]:
    rule = classify_play_type(source.get("playType"))
    source_yards = source.get("yardsGained")
    analytics_yards = 0 if rule.force_analytics_yards_zero else source_yards

    result = dict(source)
    result.update({
        "sourcePlayType": source.get("playType"),
        "eventCategory": rule.category,
        "eventSubtype": rule.subtype,
        "isScrimmagePlay": rule.is_scrimmage,
        "isOffensivePlay": rule.is_offensive_play,
        "isAdministrative": rule.is_administrative,
        "isSpecialTeams": rule.is_special_teams,
        "isPenalty": rule.is_penalty,
        "isTurnover": rule.is_turnover,
        "sourceYardsGained": source_yards,
        "analyticsYardsGained": analytics_yards,
        "yardsGainedWasNormalized": analytics_yards != source_yards,
    })
    return result

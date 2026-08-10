"""Canonical play normalization.

Canonical records preserve source values and add analytics-safe fields. Raw
records are never modified in place. Base event taxonomy and contextual
modifiers are intentionally separate: a rush can also contain a penalty,
review, fumble, or no-play context without losing its underlying play type.
"""
from __future__ import annotations

import re
from typing import Any

from cfb_analytics.canonical.play_types import classify_play_type


def _text(source: dict[str, Any]) -> str:
    return " ".join(str(source.get(k) or "") for k in ("playType", "playText")).lower()


def _context_modifiers(source: dict[str, Any]) -> dict[str, bool]:
    text = _text(source)
    # Conservative text signals. These describe context; they do not rewrite
    # the base event taxonomy or claim a specific enforcement outcome.
    penalty = "penalty" in text
    review = any(x in text for x in ("review", "reviewed", "replay official"))
    fumble = any(x in text for x in ("fumble", "fumbled"))
    interception = "intercept" in text
    no_play = bool(re.search(r"\bno play\b", text)) or any(
        x in text for x in ("play nullified", "nullified by penalty")
    )
    return {
        "hasPenaltyContext": penalty,
        "hasReviewContext": review,
        "hasFumbleContext": fumble,
        "hasInterceptionContext": interception,
        "hasNoPlayContext": no_play,
    }


def normalize_play(source: dict[str, Any]) -> dict[str, Any]:
    rule = classify_play_type(source.get("playType"))
    source_yards = source.get("yardsGained")
    analytics_yards = 0 if rule.force_analytics_yards_zero else source_yards
    modifiers = _context_modifiers(source)

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
        **modifiers,
        "hasStateTransitionModifier": any(modifiers.values()),
        "sourceYardsGained": source_yards,
        "analyticsYardsGained": analytics_yards,
        "yardsGainedWasNormalized": analytics_yards != source_yards,
    })
    return result

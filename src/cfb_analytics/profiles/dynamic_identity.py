"""Dynamic, stats-first team identity naming.

Identity names are composed from measured quality, tendencies, interactions,
consistency, and trajectory. They are not selected from a fixed archetype-name
database. Tags expose the supporting traits for fan-facing profile pages.
"""
from __future__ import annotations

import math
from statistics import mean
from typing import Any

DYNAMIC_IDENTITY_VERSION = "dynamic-team-identity-v2-quality-gated-grammar"

CORE_SERIES_FIELDS = (
    "identity_offense_quality",
    "identity_defense_quality",
    "identity_rushing_attack",
    "identity_passing_attack",
    "identity_rushing_defense",
    "identity_passing_defense",
    "rush_rate",
    "plays_per_possession",
    "identity_explosive_vs_methodical",
    "identity_predictability",
    "identity_scheme_constraint",
)


def _number(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _clip(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _quality_word(value: float | None) -> str:
    if value is None:
        return "Unknown"
    if value >= 90:
        return "Elite"
    if value >= 80:
        return "Excellent"
    if value >= 70:
        return "Strong"
    if value >= 60:
        return "Good"
    if value >= 45:
        return "Average"
    if value >= 30:
        return "Limited"
    return "Poor"


def _article(word: str) -> str:
    return "an" if word[:1].lower() in {"a", "e", "i", "o", "u"} else "a"


def _quality_phrase(value: float, noun: str) -> str:
    word = _quality_word(value).lower()
    return f"{_article(word)} {word} {noun}"


def _series_stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "final": None,
            "min": None,
            "max": None,
            "slopePerSnapshot": None,
            "residualSd": None,
            "stabilityScore": None,
        }
    n = len(values)
    avg = mean(values)
    if n == 1:
        slope = 0.0
        residual_sd = 0.0
    else:
        xbar = (n - 1) / 2.0
        denom = sum((i - xbar) ** 2 for i in range(n))
        slope = sum((i - xbar) * (v - avg) for i, v in enumerate(values)) / denom if denom else 0.0
        intercept = avg - slope * xbar
        residuals = [v - (intercept + slope * i) for i, v in enumerate(values)]
        residual_sd = math.sqrt(sum(r * r for r in residuals) / n)
    stability = _clip(100.0 - 5.0 * residual_sd)
    return {
        "count": n,
        "mean": avg,
        "final": values[-1],
        "min": min(values),
        "max": max(values),
        "slopePerSnapshot": slope,
        "residualSd": residual_sd,
        "stabilityScore": stability,
    }


def season_consistency(profiles: list[dict[str, float | None]]) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    for field in CORE_SERIES_FIELDS:
        values = [
            float(p[field])
            for p in profiles
            if isinstance(p.get(field), (int, float)) and not isinstance(p.get(field), bool)
        ]
        out[field] = _series_stats(values)
    return out


def _usage(profile: dict[str, float | None]) -> str:
    rush = _number(profile.get("rush_rate"))
    if rush is None:
        return "Balanced"
    if rush >= 80:
        return "Run-First"
    if rush <= 20:
        return "Pass-First"
    return "Balanced"


def _method(profile: dict[str, float | None]) -> str:
    value = _number(profile.get("identity_explosive_vs_methodical"))
    if value is None:
        return "Neutral"
    if value <= -18:
        return "Methodical"
    if value >= 18:
        return "Explosive"
    return "Neutral"


def _low_quality_name(profile: dict[str, float | None], off: float, defense: float) -> str:
    usage = _usage(profile)
    method = _method(profile)
    if max(off, defense) < 30:
        if method == "Explosive" and off >= 25:
            return "Explosive but Inefficient"
        if usage == "Run-First":
            return "Run-First Struggler"
        if usage == "Pass-First":
            return "Pass-First Struggler"
        return "Searching for Answers"
    if method == "Explosive" and off < 45:
        return "Explosive but Inefficient"
    if method == "Methodical" and defense >= off + 10:
        return "Methodical Survival"
    if usage == "Run-First":
        return "Run-First Survival"
    if usage == "Pass-First":
        return "Pass-First Survival"
    return "Limited Balance"


def _identity_name(profile: dict[str, float | None]) -> str:
    off = _number(profile.get("identity_offense_quality"))
    defense = _number(profile.get("identity_defense_quality"))
    method_value = _number(profile.get("identity_explosive_vs_methodical"))
    rush = _number(profile.get("rush_rate"))
    if off is None or defense is None:
        return "Unresolved Team Identity"

    gap = defense - off
    method = _method(profile)

    # Do not turn relative differences between two weak units into impressive-
    # sounding identities. Weak teams are named from their actual style/limits.
    if max(off, defense) < 45:
        return _low_quality_name(profile, off, defense)

    # Truly elite two-way teams get the cleanest top-level identity.
    if off >= 85 and defense >= 80:
        if min(off, defense) >= 90:
            return "Elite Two-Way Power"
        return "Two-Way Power"

    # Elite/strong defense paired with a competent offense. Control requires
    # methodical style; otherwise the team is simply defense-powered.
    if defense >= 85 and off >= 60:
        prefix = "Elite" if defense >= 90 else "Strong"
        return f"{prefix} Defensive Control" if method == "Methodical" else f"{prefix} Defensive Power"

    # Elite defense with a weak offense is survival, not control/power.
    if defense >= 85 and off < 60:
        return "Elite Defensive Survival" if defense >= 90 else "Defensive Survival"

    # Elite offense with a clearly weak defense can legitimately be pressure-
    # oriented because offensive quality is itself a major strength.
    if off >= 85 and defense < 60:
        return "Elite Offensive Pressure" if off >= 90 else "Offensive Pressure"

    # "Led" labels require the leading unit to be at least genuinely good.
    if gap >= 18 and defense >= 60:
        if method == "Methodical":
            return "Defense-Led Control"
        if method == "Explosive" and off >= 55:
            return "Defense-Led Counterpunch"
        return "Defense-Led Balance"

    if gap <= -18 and off >= 60:
        if method == "Explosive":
            return "Offense-Led Attack"
        if method == "Methodical":
            return "Offense-Led Control"
        return "Offense-Led Balance"

    # Style-specific names require enough offensive quality to make the style a
    # strength rather than merely a tendency.
    if rush is not None and rush >= 80 and method == "Methodical" and off >= 55:
        return "Methodical Ground Control"
    if rush is not None and rush <= 20 and method == "Explosive" and off >= 60:
        return "Explosive Air Attack"
    if method == "Explosive" and off >= 70:
        return "Explosive Offensive Power"
    if method == "Methodical" and min(off, defense) >= 55:
        return "Methodical Control"

    if min(off, defense) >= 70:
        return "Balanced Two-Way Power"

    if max(off, defense) < 60:
        return _low_quality_name(profile, off, defense)

    stronger = max(off, defense)
    if off >= defense and off >= 60:
        return f"{_quality_word(stronger)} Offensive Balance"
    if defense > off and defense >= 60:
        return f"{_quality_word(stronger)} Defensive Balance"
    return "Balanced Team"


def _tags(
    profile: dict[str, float | None],
    closing_form: dict[str, float | None] | None,
    consistency: dict[str, dict[str, float | None]],
) -> list[str]:
    tags: list[str] = []
    off = _number(profile.get("identity_offense_quality"))
    defense = _number(profile.get("identity_defense_quality"))
    rush = _number(profile.get("rush_rate"))
    method = _number(profile.get("identity_explosive_vs_methodical"))
    predict = _number(profile.get("identity_predictability"))
    run = _number(profile.get("identity_rushing_attack"))
    pas = _number(profile.get("identity_passing_attack"))

    if defense is not None and defense >= 90:
        tags.append("Elite Defense")
    elif defense is not None and defense >= 75:
        tags.append("Strong Defense")
    elif defense is not None and defense < 30:
        tags.append("Poor Defense")
    if off is not None and off >= 80:
        tags.append("High-Level Offense")
    elif off is not None and off >= 60:
        tags.append("Good Offense")
    elif off is not None and off < 30:
        tags.append("Poor Offense")

    if rush is not None:
        if rush >= 80:
            tags.append("Run-Heavy")
        elif rush <= 20:
            tags.append("Pass-Heavy")
        elif 40 <= rush <= 60:
            tags.append("Balanced Usage")
    if method is not None:
        if method <= -18:
            tags.append("Methodical")
        elif method >= 18:
            tags.append("Explosive")
    if predict is not None and predict >= 70:
        tags.append("Predictable by Choice")

    if run is not None and pas is not None and rush is not None:
        if rush >= 75 and pas - run >= 15:
            tags.append("Run-Committed")
        elif rush <= 25 and run - pas >= 15:
            tags.append("Pass-Committed")

    off_trajectory = None
    def_trajectory = None
    if closing_form:
        closing_off = _number(closing_form.get("identity_offense_quality"))
        closing_def = _number(closing_form.get("identity_defense_quality"))
        if off is not None and closing_off is not None:
            if closing_off <= off - 12:
                off_trajectory = "Offense Faded Late"
            elif closing_off >= off + 12:
                off_trajectory = "Offense Surged Late"
        if defense is not None and closing_def is not None:
            if closing_def <= defense - 12:
                def_trajectory = "Defense Faded Late"
            elif closing_def >= defense + 12:
                def_trajectory = "Defense Surged Late"

    if off_trajectory:
        tags.append(off_trajectory)
    if def_trajectory:
        tags.append(def_trajectory)

    def_stability = consistency.get("identity_defense_quality", {}).get("stabilityScore")
    off_stability = consistency.get("identity_offense_quality", {}).get("stabilityScore")
    if (
        not def_trajectory
        and isinstance(def_stability, (int, float))
        and def_stability >= 75
        and defense is not None
        and defense >= 75
    ):
        tags.append("Stable Defense")
    if (
        not off_trajectory
        and isinstance(off_stability, (int, float))
        and off_stability >= 75
        and off is not None
        and off >= 60
    ):
        tags.append("Stable Offense")

    return list(dict.fromkeys(tags))[:8]


def _summary(
    name: str,
    profile: dict[str, float | None],
    closing_form: dict[str, float | None] | None,
    consistency: dict[str, dict[str, float | None]],
) -> str:
    off = _number(profile.get("identity_offense_quality"))
    defense = _number(profile.get("identity_defense_quality"))
    rush = _number(profile.get("rush_rate"))
    method = _number(profile.get("identity_explosive_vs_methodical"))
    run = _number(profile.get("identity_rushing_attack"))
    pas = _number(profile.get("identity_passing_attack"))

    parts: list[str] = []
    if off is not None and defense is not None:
        if defense - off >= 12:
            parts.append(f"{_quality_phrase(defense, 'defense')} paired with {_quality_phrase(off, 'offense')}")
        elif off - defense >= 12:
            parts.append(f"{_quality_phrase(off, 'offense')} paired with {_quality_phrase(defense, 'defense')}")
        else:
            parts.append(f"{_quality_word(off).lower()} offense and {_quality_word(defense).lower()} defense")
    if rush is not None and rush >= 80:
        if run is not None and pas is not None and pas - run >= 15:
            parts.append("heavy run commitment even though the passing attack graded better")
        else:
            parts.append("a strongly run-oriented approach")
    elif rush is not None and rush <= 20:
        parts.append("a strongly pass-oriented approach")
    if method is not None and method <= -18:
        parts.append("methodical, low-explosive football")
    elif method is not None and method >= 18:
        parts.append("an explosive, big-play profile")

    def_stability = consistency.get("identity_defense_quality", {}).get("stabilityScore")
    if isinstance(def_stability, (int, float)) and def_stability >= 75 and defense is not None and defense >= 75:
        parts.append("defensive quality that stayed stable across the season")

    if closing_form and off is not None:
        closing_off = _number(closing_form.get("identity_offense_quality"))
        if closing_off is not None and closing_off <= off - 12:
            parts.append("with the offense cooling substantially late")
        elif closing_off is not None and closing_off >= off + 12:
            parts.append("with the offense surging late")

    if not parts:
        return name
    sentence = ", ".join(parts)
    return sentence[0].upper() + sentence[1:] + "."


def build_dynamic_identity(
    profile: dict[str, float | None],
    *,
    closing_form: dict[str, float | None] | None = None,
    season_profiles: list[dict[str, float | None]] | None = None,
) -> dict[str, Any]:
    season_profiles = season_profiles or [profile]
    consistency = season_consistency(season_profiles)
    name = _identity_name(profile)
    tags = _tags(profile, closing_form, consistency)
    return {
        "version": DYNAMIC_IDENTITY_VERSION,
        "name": name,
        "tags": tags,
        "summary": _summary(name, profile, closing_form, consistency),
        "consistency": consistency,
    }

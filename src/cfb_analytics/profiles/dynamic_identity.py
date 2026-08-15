"""Dynamic, stats-first team identity naming.

Identity names are composed from measured quality, tendencies, interactions,
consistency, and trajectory. They are not selected from a fixed archetype-name
database. Tags expose the supporting traits for fan-facing profile pages.
"""
from __future__ import annotations

import math
from statistics import mean
from typing import Any

DYNAMIC_IDENTITY_VERSION = "dynamic-team-identity-v1"

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
    # Residual movement is treated as noise; smooth directional movement is
    # trajectory rather than instability. A 20-point residual SD maps near 0.
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


def _style_word(profile: dict[str, float | None]) -> str:
    method = _number(profile.get("identity_explosive_vs_methodical"))
    rush = _number(profile.get("rush_rate"))
    if method is not None and method <= -18:
        return "Control"
    if method is not None and method >= 18:
        return "Attack"
    if rush is not None and rush >= 80:
        return "Ground Control"
    if rush is not None and rush <= 20:
        return "Air Attack"
    return "Balance"


def _identity_name(profile: dict[str, float | None]) -> str:
    off = _number(profile.get("identity_offense_quality"))
    defense = _number(profile.get("identity_defense_quality"))
    method = _number(profile.get("identity_explosive_vs_methodical"))
    rush = _number(profile.get("rush_rate"))
    if off is None or defense is None:
        return "Unresolved Team Identity"

    gap = defense - off
    style = _style_word(profile)

    if defense >= 85 and off >= 60:
        base = "Defensive Control" if method is not None and method <= -15 else "Defensive Power"
        prefix = "Elite" if defense >= 90 else "Strong"
        return f"{prefix} {base}"
    if defense >= 85 and off < 60:
        return "Elite Defensive Survival" if defense >= 90 else "Defensive Survival"
    if off >= 85 and defense >= 80:
        return "Elite Two-Way Power" if min(off, defense) >= 90 else "Two-Way Power"
    if off >= 85 and defense < 60:
        return "Elite Offensive Pressure" if off >= 90 else "Offensive Pressure"
    if gap >= 18:
        prefix = "Elite" if defense >= 90 else "Defense-Led"
        return f"{prefix} {style}"
    if gap <= -18:
        prefix = "Elite" if off >= 90 else "Offense-Led"
        return f"{prefix} {style}"
    if rush is not None and rush >= 80 and method is not None and method <= -15:
        return "Methodical Ground Control"
    if rush is not None and rush <= 20 and method is not None and method >= 10:
        return "Explosive Air Attack"
    if min(off, defense) >= 70:
        return "Balanced Two-Way Power"
    if max(off, defense) < 45:
        return "Searching for an Identity"
    return f"{_quality_word(max(off, defense))} {style}"


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
    if off is not None and off >= 80:
        tags.append("High-Level Offense")
    elif off is not None and off >= 60:
        tags.append("Good Offense")

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

    def_stability = consistency.get("identity_defense_quality", {}).get("stabilityScore")
    off_stability = consistency.get("identity_offense_quality", {}).get("stabilityScore")
    if isinstance(def_stability, (int, float)) and def_stability >= 75 and defense is not None and defense >= 75:
        tags.append("Stable Defense")
    if isinstance(off_stability, (int, float)) and off_stability >= 75 and off is not None and off >= 60:
        tags.append("Stable Offense")

    if closing_form:
        closing_off = _number(closing_form.get("identity_offense_quality"))
        closing_def = _number(closing_form.get("identity_defense_quality"))
        if off is not None and closing_off is not None:
            if closing_off <= off - 12:
                tags.append("Offense Faded Late")
            elif closing_off >= off + 12:
                tags.append("Offense Surged Late")
        if defense is not None and closing_def is not None:
            if closing_def <= defense - 12:
                tags.append("Defense Faded Late")
            elif closing_def >= defense + 12:
                tags.append("Defense Surged Late")

    # Preserve order while preventing duplicate labels.
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
            parts.append(f"a {_quality_word(defense).lower()} defense paired with a {_quality_word(off).lower()} offense")
        elif off - defense >= 12:
            parts.append(f"a {_quality_word(off).lower()} offense carrying a {_quality_word(defense).lower()} defense")
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

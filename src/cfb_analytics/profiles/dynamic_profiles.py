"""Materialize dynamic season identities for every historical team-season."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .dynamic_identity import DYNAMIC_IDENTITY_VERSION, build_dynamic_identity
from .layered_archetypes import (
    _season_identity_from_snapshot,
    closing_form_profile,
    final_snapshot,
)
from .snapshots import DEFAULT_SEASONS

OUTPUT_VERSION = "dynamic-team-profiles-v4-neutral-style-earned-effectiveness"

STYLE_METRIC_MAP = {
    "identity_success_quality": "oa_success_off",
    "identity_explosiveness_quality": "oa_explosiveness_off",
    "identity_finishing_quality": "oa_finishing_off",
    "identity_third_down_quality": "oa_third_down_off",
}


def _enrich_style_metrics(
    profile: dict[str, float | None],
    snapshot: dict[str, Any],
    *,
    prefix: str,
) -> dict[str, float | None]:
    """Attach direct percentile evidence used to distinguish offensive mechanisms."""
    out = dict(profile)
    for target, source in STYLE_METRIC_MAP.items():
        value = snapshot.get(f"{prefix}_{source}_percentile")
        out[target] = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
    return out


def build_dynamic_profiles(
    rows: list[dict[str, Any]],
    *,
    seasons: tuple[int, ...] = DEFAULT_SEASONS,
) -> dict[str, Any]:
    wanted = {int(x) for x in seasons}
    groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        season = int(row.get("season", -1))
        team = str(row.get("team") or "")
        if season in wanted and team:
            groups[(season, team)].append(row)

    items: list[dict[str, Any]] = []
    for (season, team), selected in sorted(groups.items()):
        selected.sort(
            key=lambda row: (
                int(row.get("gamesPlayed") or 0),
                str(row.get("startDate") or ""),
                str(row.get("throughGameId") or ""),
            )
        )
        final = final_snapshot(selected)
        season_profiles = [
            _enrich_style_metrics(_season_identity_from_snapshot(row), row, prefix="baseline")
            for row in selected
        ]
        profile = season_profiles[-1]
        closing = _enrich_style_metrics(closing_form_profile(selected), final, prefix="current")
        identity = build_dynamic_identity(
            profile,
            closing_form=closing,
            season_profiles=season_profiles,
        )
        items.append(
            {
                "season": season,
                "team": team,
                "identityName": identity["name"],
                "identityTags": identity["tags"],
                "identitySummary": identity["summary"],
                "identityStyle": identity["style"],
                "identityVersion": identity["version"],
                "profileBasis": "FINAL_SEASON_TO_DATE_BASELINE",
                "closingFormBasis": "RECENT_FOUR_GAMES",
                "finalGamesPlayed": int(final.get("gamesPlayed") or 0),
                "finalSeasonType": final.get("seasonType"),
                "finalWeek": final.get("week"),
                "finalStartDate": final.get("startDate"),
                "finalThroughGameId": final.get("throughGameId"),
                "profile": profile,
                "closingFormProfile": closing,
                "consistency": identity["consistency"],
            }
        )

    return {
        "version": OUTPUT_VERSION,
        "identityVersion": DYNAMIC_IDENTITY_VERSION,
        "namingBasis": "NEUTRAL_STYLE_PLUS_MECHANISM_PLUS_EARNED_EFFECTIVENESS",
        "seasons": sorted(wanted),
        "teamSeasonCount": len(items),
        "teamSeasons": items,
    }


def concise(report: dict[str, Any], *, examples: int = 20) -> str:
    lines = [
        "DYNAMIC TEAM IDENTITIES — STYLE + MECHANISM + EFFECTIVENESS",
        f"Team-seasons: {report['teamSeasonCount']:,}",
        f"Seasons: {', '.join(str(x) for x in report['seasons'])}",
        "Neutral style describes behavior; strength words are earned by quality.",
        "Tags expose supporting tendencies, mechanisms, quality, consistency, and trajectory.",
        "",
    ]
    for item in report["teamSeasons"][:examples]:
        tags = " · ".join(item.get("identityTags") or []) or "No strong tags"
        style = item.get("identityStyle") or {}
        lines.append(f"{item['season']} {item['team']} — {item['identityName']}")
        lines.append(
            "  STYLE | "
            f"usage={style.get('usage')} | method={style.get('method')} | pace={style.get('paceShape')} | "
            f"efficiency={style.get('efficiencyShape')} | driver={style.get('attackDriver')} | "
            f"commitment={style.get('commitment')} | structure={style.get('teamStructure')} | "
            f"effectiveness={style.get('effectiveness')}"
        )
        lines.append(f"  TAGS  | {tags}")
        lines.append(f"  {item['identitySummary']}")
        lines.append("")
    return "\n".join(lines)


def materialize(
    processed_root: Path,
    *,
    seasons: tuple[int, ...] = DEFAULT_SEASONS,
) -> Path:
    source = processed_root / "derived" / "profiles" / "identity_snapshots_v3_attack_scheme.json"
    if not source.exists():
        raise FileNotFoundError("build snapshots first: python -m cfb_analytics.profiles.snapshots")
    rows = json.loads(source.read_text())
    report = build_dynamic_profiles(rows, seasons=seasons)
    target = processed_root / "derived" / "profiles" / "dynamic_team_identities.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, separators=(",", ":")))
    return target


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    p.add_argument("--seasons", nargs="+", type=int, default=list(DEFAULT_SEASONS))
    p.add_argument("--examples", type=int, default=20)
    args = p.parse_args()
    target = materialize(args.processed_root, seasons=tuple(args.seasons))
    report = json.loads(target.read_text())
    print(concise(report, examples=args.examples))
    print(f"WROTE {target}")


if __name__ == "__main__":
    main()

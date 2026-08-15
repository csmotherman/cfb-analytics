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

OUTPUT_VERSION = "dynamic-team-profiles-v2-full-corpus"


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
        season_profiles = [_season_identity_from_snapshot(row) for row in selected]
        profile = season_profiles[-1]
        closing = closing_form_profile(selected)
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
        "namingBasis": "DYNAMIC_COMPOSITION_NOT_FIXED_ARCHETYPE_DATABASE",
        "seasons": sorted(wanted),
        "teamSeasonCount": len(items),
        "teamSeasons": items,
    }


def concise(report: dict[str, Any], *, examples: int = 20) -> str:
    lines = [
        "DYNAMIC TEAM IDENTITIES",
        f"Team-seasons: {report['teamSeasonCount']:,}",
        f"Seasons: {', '.join(str(x) for x in report['seasons'])}",
        "Names: composed from quality + tendencies + interactions + consistency + trajectory.",
        "Tags: supporting profile traits for fan-facing display.",
        "",
    ]
    for item in report["teamSeasons"][:examples]:
        tags = " · ".join(item.get("identityTags") or []) or "No strong tags"
        lines.append(f"{item['season']} {item['team']} — {item['identityName']}")
        lines.append(f"  {tags}")
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

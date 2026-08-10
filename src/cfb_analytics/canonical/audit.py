"""Coverage audits for canonical play taxonomy."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable

from cfb_analytics.canonical.play_types import RULES
from cfb_analytics.raw.audit import discover_partitions, partition_dir


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def play_type_coverage(root: Path, seasons: Iterable[int]) -> dict:
    counts = Counter()
    total = 0
    for season in seasons:
        for season_type, week in discover_partitions(root, season):
            d = partition_dir(root, season, season_type, week)
            for play in _load(d / "plays.json"):
                play_type = play.get("playType")
                counts[str(play_type)] += 1
                total += 1
    observed = set(counts)
    classified = observed & set(RULES)
    unclassified = observed - set(RULES)
    unused_rules = set(RULES) - observed
    return {
        "total_plays": total,
        "observed_play_types": len(observed),
        "classified_play_types": len(classified),
        "unclassified_play_types": {k: counts[k] for k in sorted(unclassified)},
        "unused_taxonomy_rules": sorted(unused_rules),
        "status": "PASS" if not unclassified else "REVIEW",
    }


def concise_play_type_coverage(r: dict) -> str:
    lines = [
        f"CANONICAL PLAY-TYPE COVERAGE: {r['status']}",
        f"Plays scanned: {r['total_plays']:,}",
        f"Observed play types: {r['observed_play_types']}",
        f"Classified play types: {r['classified_play_types']}",
        f"Unclassified play types: {len(r['unclassified_play_types'])}",
    ]
    if r["unclassified_play_types"]:
        lines.append("")
        lines.append("Unclassified source play types:")
        for name, count in sorted(r["unclassified_play_types"].items(), key=lambda x: -x[1]):
            lines.append(f"  {count:>8,}  {name}")
    else:
        lines.append("All observed play types are explicitly classified.")
    return "\n".join(lines)

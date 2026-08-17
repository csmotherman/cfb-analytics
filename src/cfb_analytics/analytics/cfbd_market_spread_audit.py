"""Audit clean CFBD historical market spreads before model comparison."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/raw/market_lines/cfbd-market-spreads-2014-2025.json")


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("games"), list):
        raise ValueError(f"Invalid market spread snapshot: {path}")
    rows = [row for row in payload["games"] if isinstance(row, dict)]
    seen: set[str] = set()
    for row in rows:
        gid = str(row.get("gameId"))
        if gid in seen:
            raise ValueError(f"Duplicate gameId {gid}")
        seen.add(gid)
        if not _finite_number(row.get("marketSpread")):
            raise ValueError(f"Non-finite marketSpread for gameId {gid}: {row.get('marketSpread')!r}")
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    spreads = [float(row["marketSpread"]) for row in rows]
    abs_spreads = [abs(value) for value in spreads]
    provider_counts = Counter(str(row.get("provider") or "") for row in rows)
    by_season: dict[int, list[float]] = defaultdict(list)
    for row, spread in zip(rows, spreads):
        by_season[int(row["season"])].append(spread)

    return {
        "n": len(rows),
        "nonFinite": sum(not math.isfinite(value) for value in spreads),
        "homeFavored": sum(value > 0 for value in spreads),
        "awayFavored": sum(value < 0 for value in spreads),
        "pickem": sum(value == 0 for value in spreads),
        "minSpread": min(spreads) if spreads else None,
        "maxSpread": max(spreads) if spreads else None,
        "meanSpread": statistics.fmean(spreads) if spreads else None,
        "medianSpread": statistics.median(spreads) if spreads else None,
        "meanAbsSpread": statistics.fmean(abs_spreads) if spreads else None,
        "medianAbsSpread": statistics.median(abs_spreads) if spreads else None,
        "absSpreadAtLeast40": sum(value >= 40 for value in abs_spreads),
        "absSpreadAtLeast50": sum(value >= 50 for value in abs_spreads),
        "absSpreadAtLeast60": sum(value >= 60 for value in abs_spreads),
        "providerCounts": dict(provider_counts.most_common()),
        "bySeason": [
            {
                "season": season,
                "n": len(values),
                "homeFavored": sum(value > 0 for value in values),
                "awayFavored": sum(value < 0 for value in values),
                "pickem": sum(value == 0 for value in values),
                "meanSpread": statistics.fmean(values),
                "medianSpread": statistics.median(values),
                "meanAbsSpread": statistics.fmean(abs(value) for value in values),
                "minSpread": min(values),
                "maxSpread": max(values),
            }
            for season, values in sorted(by_season.items())
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit clean CFBD market spreads")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()

    result = summarize(load_rows(args.input))
    print("CFBD MARKET SPREAD AUDIT")
    print(
        f"games={result['n']} nonfinite={result['nonFinite']} "
        f"home_favored={result['homeFavored']} away_favored={result['awayFavored']} "
        f"pickem={result['pickem']}"
    )
    print(
        f"spread_range=[{result['minSpread']:.1f}, {result['maxSpread']:.1f}] "
        f"mean={result['meanSpread']:.3f} median={result['medianSpread']:.3f} "
        f"mean_abs={result['meanAbsSpread']:.3f} median_abs={result['medianAbsSpread']:.3f}"
    )
    print(
        f"abs_spread>=40: {result['absSpreadAtLeast40']}  "
        f">=50: {result['absSpreadAtLeast50']}  >=60: {result['absSpreadAtLeast60']}"
    )
    print("\nPer-season:")
    for row in result["bySeason"]:
        print(
            f"  {row['season']}: n={row['n']} homeFav={row['homeFavored']} "
            f"awayFav={row['awayFavored']} pickem={row['pickem']} "
            f"mean={row['meanSpread']:+.3f} med={row['medianSpread']:+.3f} "
            f"meanAbs={row['meanAbsSpread']:.3f} "
            f"range=[{row['minSpread']:.1f},{row['maxSpread']:.1f}]"
        )
    print("\nTop providers:")
    for provider, count in list(result["providerCounts"].items())[:15]:
        print(f"  {provider or '<blank>'}: {count}")


if __name__ == "__main__":
    main()

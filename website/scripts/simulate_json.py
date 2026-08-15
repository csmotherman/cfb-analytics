from __future__ import annotations
import argparse
import json
from pathlib import Path

from cfb_analytics.profiles.game_simulator import _lookup, build_simulator, simulate_matchup


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--home-year", type=int, required=True)
    p.add_argument("--home-team", required=True)
    p.add_argument("--away-year", type=int, required=True)
    p.add_argument("--away-team", required=True)
    p.add_argument("--sims", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    model, states, cache_status = build_simulator(Path("data/raw"), Path("data/processed"))
    home = _lookup(states, a.home_year, a.home_team)
    away = _lookup(states, a.away_year, a.away_team)
    result = simulate_matchup(model, home, away, simulations=a.sims, seed=a.seed)
    result["cacheStatus"] = cache_status
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()

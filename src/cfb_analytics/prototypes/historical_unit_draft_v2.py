"""Playable-rules layer for the data-only 2019 LSU historical challenge.

The first prototype proved the statistical grading/calibration pipeline, but seven
mandatory spins made 2019 LSU effectively unbeatable. This layer changes only the
game rules, not the historical grades or calibrated probability model:

* wheel contains the top 10 SRS team-seasons from each supported season;
* the player must fill the same seven units;
* the player may PASS up to three spins, for at most 10 spins total;
* a final probability strictly greater than 50% beats 2019 LSU.

The pass mechanic is intentionally visible and finite. It adds strategy while
keeping the challenge difficult. Difficulty is evaluated only by simulation, not by
observed user outcomes.
"""
from __future__ import annotations

import argparse
import copy
import json
import random
from pathlib import Path
from statistics import mean
from typing import Any

from cfb_analytics.prototypes import historical_unit_draft as v1

CHALLENGE_VERSION = "historical-unit-draft-v2"
WHEEL_TOP_N_PER_SEASON = 10
MAX_PASSES = 3
REQUIRED_UNITS = len(v1.CATEGORY_ORDER)
MAX_SPINS = REQUIRED_UNITS + MAX_PASSES
BASELINE_PASS_GRADE = 90.0  # A-: intuitive, fixed before user testing.


def _finite(value: Any) -> bool:
    return v1._finite(value)


def _select(row: dict[str, Any], category: str) -> dict[str, Any]:
    return v1._selection_from_row(row, category)


def finalize_dataset(base: dict[str, Any]) -> dict[str, Any]:
    """Convert the broad v1 research pool into the fixed playable v2 contract."""
    payload = copy.deepcopy(base)
    pool = [
        row
        for row in payload.get("wheelPool", [])
        if int(row.get("srsRank") or 9999) <= WHEEL_TOP_N_PER_SEASON
    ]
    if len(pool) < 75:
        raise ValueError(f"Playable wheel pool unexpectedly small: {len(pool)}")

    payload["schemaVersion"] = 2
    payload["challengeVersion"] = CHALLENGE_VERSION
    payload["status"] = "data-prototype-playable"
    payload["wheelPool"] = pool
    payload["wheelEligibility"] = {
        "topSrsPerSeason": WHEEL_TOP_N_PER_SEASON,
        "targetExcluded": True,
        "eligibleTeamSeasons": len(pool),
        "reason": (
            "The first difficulty sweep showed a top-35 pool made 2019 LSU nearly "
            "impossible. Top-10 plus three finite passes preserves cross-era variety "
            "while making a >50% build rare but attainable."
        ),
    }
    payload["rules"] = {
        "requiredUnits": REQUIRED_UNITS,
        "maxSpins": MAX_SPINS,
        "passes": MAX_PASSES,
        "categories": [
            {"key": category, "label": v1.CATEGORY_LABELS[category]}
            for category in v1.CATEGORY_ORDER
        ],
        "wheel": "uniform random draw without replacement from eligible historical team-seasons",
        "onSpin": "draft one still-open unit from that team-season OR spend one remaining pass",
        "forcedDraftRule": (
            "When remaining spins equal remaining open units, the player must draft "
            "on every remaining spin."
        ),
        "site": "neutral",
        "winCondition": "estimated neutral-field win probability must be > 0.50",
        "winThreshold": v1.WIN_THRESHOLD,
    }
    notes = list(payload.get("dataNotes", []))
    notes.append(
        "Playable v2 uses a fixed top-10-per-season wheel and three passes; these rules were chosen from pre-user simulation difficulty, not tuned to user results."
    )
    payload["dataNotes"] = notes
    return payload


def evaluate_selections(dataset: dict[str, Any], selections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return v1.evaluate_selections(dataset, selections)


def pass_aware_baseline(
    dataset: dict[str, Any],
    spins: list[dict[str, Any]],
    *,
    pass_grade: float = BASELINE_PASS_GRADE,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    """Sequential, inspectable baseline strategy used only for difficulty testing.

    On each spin it finds the strongest weighted open unit. It passes if that unit is
    below A- while a pass is available, unless passing would leave too few spins to
    fill the roster. This is deliberately simple and is not meant to be optimal.
    """
    if len(spins) < REQUIRED_UNITS:
        raise ValueError("Not enough spins to fill all units")
    if len(spins) > MAX_SPINS:
        raise ValueError(f"Playable v2 allows at most {MAX_SPINS} spins")

    open_categories = set(v1.CATEGORY_ORDER)
    selections: dict[str, dict[str, Any]] = {}
    decisions: list[dict[str, Any]] = []
    passes_left = MAX_PASSES
    weights = dataset["strengthModel"]["categoryWeights"]

    for spin_index, row in enumerate(spins):
        if not open_categories:
            break
        remaining_including_current = len(spins) - spin_index
        forced = remaining_including_current <= len(open_categories)
        choices: list[tuple[float, float, str]] = []
        for category in open_categories:
            unit = row.get("categories", {}).get(category, {})
            z = unit.get("z")
            grade = unit.get("grade")
            if not (_finite(z) and _finite(grade)):
                continue
            weighted = float(weights[category]) * float(z)
            choices.append((weighted, float(grade), category))
        if not choices:
            if passes_left > 0 and not forced:
                passes_left -= 1
                decisions.append({"spin": spin_index + 1, "team": row.get("team"), "season": row.get("season"), "action": "pass"})
                continue
            raise ValueError(f"No draftable category on forced spin {spin_index + 1}")

        _, best_grade, category = max(choices)
        if not forced and passes_left > 0 and best_grade < float(pass_grade):
            passes_left -= 1
            decisions.append(
                {
                    "spin": spin_index + 1,
                    "team": row.get("team"),
                    "season": row.get("season"),
                    "action": "pass",
                    "bestAvailableGrade": best_grade,
                    "passesLeft": passes_left,
                }
            )
            continue

        selection = _select(row, category)
        selections[category] = selection
        open_categories.remove(category)
        decisions.append(
            {
                "spin": spin_index + 1,
                "team": row.get("team"),
                "season": row.get("season"),
                "action": "draft",
                "category": category,
                "grade": selection.get("grade"),
                "letter": selection.get("letter"),
                "passesLeft": passes_left,
            }
        )

    if open_categories:
        raise ValueError(f"Baseline ended with unfilled units: {sorted(open_categories)}")
    return selections, evaluate_selections(dataset, selections), decisions


def perfect_foresight_upper_bound(
    dataset: dict[str, Any],
    spins: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Best possible seven-unit assignment from at most ten spun team-seasons.

    Dynamic programming allows a spin to be passed and therefore supplies a strict
    upper bound on what a human could achieve from the exact same wheel results.
    """
    if len(spins) > MAX_SPINS:
        raise ValueError(f"Playable v2 allows at most {MAX_SPINS} spins")
    weights = dataset["strengthModel"]["categoryWeights"]
    states: dict[int, tuple[float, dict[str, int]]] = {0: (0.0, {})}

    for spin_idx, row in enumerate(spins):
        next_states = dict(states)  # passing/skipping this spin
        for mask, (score, assignment) in states.items():
            for cat_idx, category in enumerate(v1.CATEGORY_ORDER):
                bit = 1 << cat_idx
                if mask & bit:
                    continue
                z = row.get("categories", {}).get(category, {}).get("z")
                if not _finite(z):
                    continue
                new_mask = mask | bit
                new_score = score + float(weights[category]) * float(z)
                old = next_states.get(new_mask)
                if old is None or new_score > old[0]:
                    next_assignment = dict(assignment)
                    next_assignment[category] = spin_idx
                    next_states[new_mask] = (new_score, next_assignment)
        states = next_states

    full_mask = (1 << REQUIRED_UNITS) - 1
    if full_mask not in states:
        raise ValueError("Could not fill all seven units from these spins")
    assignment = states[full_mask][1]
    selections = {
        category: _select(spins[spin_idx], category)
        for category, spin_idx in assignment.items()
    }
    return selections, evaluate_selections(dataset, selections)


def benchmark_difficulty(
    dataset: dict[str, Any],
    *,
    simulations: int = 5000,
    seed: int = 2019,
) -> dict[str, Any]:
    if simulations <= 0:
        raise ValueError("simulations must be positive")
    pool = dataset["wheelPool"]
    if len(pool) < MAX_SPINS:
        raise ValueError("wheel pool too small")
    rng = random.Random(seed)
    baseline_probs: list[float] = []
    oracle_probs: list[float] = []

    for _ in range(simulations):
        spins = rng.sample(pool, MAX_SPINS)
        _, baseline, _ = pass_aware_baseline(dataset, spins)
        _, oracle = perfect_foresight_upper_bound(dataset, spins)
        baseline_probs.append(float(baseline["winProbability"]))
        oracle_probs.append(float(oracle["winProbability"]))

    def summarize(values: list[float]) -> dict[str, Any]:
        ordered = sorted(values)
        n = len(values)
        return {
            "winRate": sum(value > v1.WIN_THRESHOLD for value in values) / n,
            "meanWinProbability": mean(values),
            "medianWinProbability": ordered[n // 2],
            "p90WinProbability": ordered[min(n - 1, int(0.90 * n))],
            "maxWinProbability": ordered[-1],
        }

    return {
        "simulations": simulations,
        "seed": seed,
        "rules": {
            "wheelTopNPerSeason": WHEEL_TOP_N_PER_SEASON,
            "maxSpins": MAX_SPINS,
            "passes": MAX_PASSES,
            "baselinePassGrade": BASELINE_PASS_GRADE,
        },
        "aMinusPassBaseline": summarize(baseline_probs),
        "perfectForesightUpperBound": summarize(oracle_probs),
        "interpretation": (
            "The A- baseline is a simple sequential strategy. Perfect foresight is an impossible-to-beat ceiling. "
            "Actual skilled users should fall between them."
        ),
    }


def spin(dataset: dict[str, Any], *, seed: int, count: int = MAX_SPINS) -> list[dict[str, Any]]:
    if count > MAX_SPINS:
        raise ValueError(f"count cannot exceed {MAX_SPINS}")
    return random.Random(seed).sample(dataset["wheelPool"], count)


def build_playable_dataset(
    base: dict[str, Any],
    *,
    simulations: int = 5000,
    seed: int = 2019,
) -> dict[str, Any]:
    payload = finalize_dataset(base)
    payload["difficultyBenchmark"] = benchmark_difficulty(payload, simulations=simulations, seed=seed)
    return payload


def concise_demo(dataset: dict[str, Any], *, seed: int) -> str:
    spins = spin(dataset, seed=seed)
    selections, result, decisions = pass_aware_baseline(dataset, spins)
    lines = [dataset["title"], f"Playable v2 seed: {seed}", ""]
    for decision in decisions:
        prefix = f"Spin {decision['spin']}: {decision['season']} {decision['team']}"
        if decision["action"] == "pass":
            lines.append(f"{prefix} -> PASS")
        else:
            lines.append(
                f"{prefix} -> {v1.CATEGORY_LABELS[decision['category']]} {decision['letter']} ({float(decision['grade']):.1f})"
            )
    lines.extend(
        [
            "",
            f"Estimated hybrid SRS: {result['estimatedHybridSrs']:.2f}",
            f"2019 LSU SRS: {result['targetSrs']:.2f}",
            f"Expected neutral margin: {result['expectedNeutralMargin']:+.2f}",
            f"Chance to beat 2019 LSU: {result['winProbability'] * 100.0:.1f}%",
            "WIN" if result["win"] else "LOSS",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("data/prototypes/beat-2019-lsu/challenge-v1.json"))
    parser.add_argument("--output", type=Path, default=Path("data/prototypes/beat-2019-lsu/challenge-v2.json"))
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--difficulty-sims", type=int, default=5000)
    args = parser.parse_args()

    if args.build:
        base = json.loads(args.base.read_text())
        payload = build_playable_dataset(base, simulations=args.difficulty_sims)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        b = payload["difficultyBenchmark"]
        print("HISTORICAL UNIT DRAFT PLAYABLE V2: PASS")
        print(f"output={args.output}")
        print(f"wheel={len(payload['wheelPool'])}")
        print(f"spins={MAX_SPINS} passes={MAX_PASSES}")
        print("baselineWinRate=", b["aMinusPassBaseline"]["winRate"])
        print("oracleWinRate=", b["perfectForesightUpperBound"]["winRate"])

    if args.demo:
        dataset = json.loads(args.output.read_text())
        print(concise_demo(dataset, seed=args.seed))

    if not args.build and not args.demo:
        parser.error("choose --build and/or --demo")


if __name__ == "__main__":
    main()

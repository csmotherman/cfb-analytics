from __future__ import annotations

from cfb_analytics.prototypes import historical_player_team_year_wheel as wheel


def player(psid: str, cost: float, **slot_power: float) -> dict:
    return {
        "playerSeasonId": psid,
        "nilAskMillions": cost,
        "ratings": {
            slot: {"powerZ": power, "grade": 90.0, "letter": "A-", "eraScore": 0.9}
            for slot, power in slot_power.items()
        },
    }


def entry(name: str, roster: list[dict]) -> dict:
    return {"id": name, "team": name, "season": 2024, "roster": roster}


def test_pareto_options_removes_dominated_players() -> None:
    e = entry(
        "A",
        [
            player("cheap", 1.0, QB=0.5),
            player("dominated", 1.5, QB=0.4),
            player("elite", 2.0, QB=1.0),
        ],
    )
    options = wheel._pareto_options(e)["QB"]
    ids = [row[2] for row in options]
    assert ids == ["cheap", "elite"]


def test_draw_frontier_requires_one_player_per_spin_and_every_slot(monkeypatch) -> None:
    monkeypatch.setattr(wheel.base, "SLOT_ORDER", ("QB", "DB"))
    monkeypatch.setattr(wheel.base, "SLOT_WEIGHTS", {"QB": 0.6, "DB": 0.4})
    entries = [
        entry("A", [player("a-qb", 1.0, QB=1.0), player("a-db", 1.0, DB=0.2)]),
        entry("B", [player("b-qb", 1.0, QB=0.1), player("b-db", 1.0, DB=1.0)]),
    ]
    options = [wheel._pareto_options(e) for e in entries]
    frontier = wheel._draw_frontier([0, 1], options)
    assert frontier
    # Best assignment is A->QB and B->DB: .6*1 + .4*1 = 1.0.
    assert max(power for _, power in frontier) == 1.0
    assert min(cost for cost, _ in frontier) == 20


def test_probability_is_exactly_half_at_equal_roster_power() -> None:
    calibration = {"rosterPowerToMargin": 5.0, "residualSd": 12.0}
    assert wheel._result_probability(1.25, 1.25, calibration) == 0.5
    assert wheel._result_probability(1.5, 1.25, calibration) > 0.5
    assert wheel._result_probability(1.0, 1.25, calibration) < 0.5


def test_prune_keeps_only_cost_power_frontier() -> None:
    states = [(10, 1.0), (12, 0.9), (12, 1.2), (15, 1.1), (20, 1.5)]
    assert wheel._prune(states) == [(10, 1.0), (12, 1.2), (20, 1.5)]

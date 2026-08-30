from __future__ import annotations

import pytest

from cfb_analytics.analytics.returning_ppa import build_returning_ppa_report


def test_returning_ppa_matches_current_roster_and_separates_attribution_views() -> None:
    current = [
        {"id": "1", "firstName": "Broc", "lastName": "Lowry", "position": "QB"},
        {"id": "2", "firstName": "Jalen", "lastName": "Buckley", "position": "RB"},
        {"id": "99", "firstName": "Name", "lastName": "Match", "position": "QB"},
    ]
    prior_ppa = [
        {
            "id": "1",
            "name": "Broc Lowry",
            "position": "QB",
            "team": "Western Michigan",
            "totalPPA": {"all": 10.0, "pass": 8.0, "rush": 2.0},
        },
        {
            "id": "2",
            "name": "Jalen Buckley",
            "position": "RB",
            "team": "Western Michigan",
            "totalPPA": {"all": 5.0, "pass": 1.0, "rush": 4.0},
        },
        {
            "id": "3",
            "name": "Departed Receiver",
            "position": "WR",
            "team": "Western Michigan",
            "totalPPA": {"all": 6.0, "pass": 6.0, "rush": 0.0},
        },
        {
            "id": "4",
            "name": "Name Match",
            "position": "QB",
            "team": "Western Michigan",
            "totalPPA": {"all": 2.0, "pass": 2.0, "rush": 0.0},
        },
    ]

    report = build_returning_ppa_report(
        current,
        prior_ppa,
        team="Western Michigan",
        season=2026,
    )

    overall = report["overallPlayerAttributedPPA"]
    assert overall["priorSeasonPPA"] == pytest.approx(23.0)
    assert overall["returningPPA"] == pytest.approx(17.0)
    assert overall["returningShare"] == pytest.approx(17.0 / 23.0)

    passing = report["passingPPA"]
    assert passing["priorSeasonPPA"] == pytest.approx(10.0)
    assert passing["returningPPA"] == pytest.approx(10.0)
    assert passing["returningShare"] == pytest.approx(1.0)

    receiving = report["receivingAttributedPPA"]
    assert receiving["priorSeasonPPA"] == pytest.approx(7.0)
    assert receiving["returningPPA"] == pytest.approx(1.0)
    assert receiving["returningShare"] == pytest.approx(1.0 / 7.0)

    rushing = report["rushingPPA"]
    assert rushing["priorSeasonPPA"] == pytest.approx(6.0)
    assert rushing["returningPPA"] == pytest.approx(6.0)
    assert rushing["returningShare"] == pytest.approx(1.0)

    name_match = next(row for row in report["players"] if row["name"] == "Name Match")
    assert name_match["returning"] is True
    assert name_match["matchMethod"] == "name"


def test_returning_ppa_accepts_flattened_cfbd_field_names() -> None:
    current = [{"id": 10, "firstName": "Player", "lastName": "One", "position": "QB"}]
    prior_ppa = [
        {
            "id": 10,
            "name": "Player One",
            "position": "QB",
            "team": "Western Michigan",
            "total_PPA_all": 4.0,
            "total_PPA_pass": 3.5,
            "total_PPA_rush": 0.5,
        }
    ]

    report = build_returning_ppa_report(
        current,
        prior_ppa,
        team="Western Michigan",
        season=2026,
    )

    assert report["overallPlayerAttributedPPA"]["returningShare"] == pytest.approx(1.0)
    assert report["passingPPA"]["returningPPA"] == pytest.approx(3.5)
    assert report["rushingPPA"]["returningPPA"] == pytest.approx(0.5)

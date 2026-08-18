from __future__ import annotations

from cfb_analytics.prototypes.historical_player_nil_draft import (
    SLOT_ORDER,
    _best_board_lineup,
    _canonical_stat,
    _position_group,
    _slot_eligibility,
    aggregate_player_stats,
    assign_nil_prices,
    evaluate_lineup,
    letter_grade,
    roster_power,
    score_players,
)


def _meta():
    return {
        "Test U": {
            "teamId": 1,
            "conference": "TEST",
            "abbreviation": "TU",
            "logo": "https://example.com/logo.png",
            "color": "#112233",
            "alternateColor": "#445566",
        }
    }


def test_position_groups_and_slot_eligibility():
    assert _position_group("QB") == "QB"
    assert _position_group("HB") == "RB"
    assert _position_group("TE") == "TE"
    assert _position_group("EDGE") == "DL"
    assert _position_group("CB") == "DB"
    assert _slot_eligibility("RB") == ("RB", "FLEX")
    assert _slot_eligibility("WR") == ("WR", "FLEX")
    assert _slot_eligibility("TE") == ("FLEX",)


def test_canonical_stat_mapping():
    assert _canonical_stat("passing", "YDS") == "passYards"
    assert _canonical_stat("passing", "INT") == "passINT"
    assert _canonical_stat("rushing", "CAR") == "rushCarries"
    assert _canonical_stat("receiving", "REC") == "receptions"
    assert _canonical_stat("defensive", "TFL") == "tacklesForLoss"
    assert _canonical_stat("defensive", "SACKS") == "sacks"
    assert _canonical_stat("defensive", "INT") == "defInterceptions"


def test_player_rows_aggregate_and_derive_stats():
    payload = [
        {"playerId": 7, "player": "Demo QB", "team": "Test U", "position": "QB", "category": "passing", "statType": "YDS", "stat": "3000"},
        {"playerId": 7, "player": "Demo QB", "team": "Test U", "position": "QB", "category": "passing", "statType": "TD", "stat": "30"},
        {"playerId": 7, "player": "Demo QB", "team": "Test U", "position": "QB", "category": "passing", "statType": "INT", "stat": "5"},
        {"playerId": 7, "player": "Demo QB", "team": "Test U", "position": "QB", "category": "passing", "statType": "CMP", "stat": "240"},
        {"playerId": 7, "player": "Demo QB", "team": "Test U", "position": "QB", "category": "passing", "statType": "ATT", "stat": "360"},
        {"playerId": 7, "player": "Demo QB", "team": "Test U", "position": "QB", "category": "rushing", "statType": "YDS", "stat": "500"},
    ]
    rows = aggregate_player_stats(2024, payload, _meta())
    assert len(rows) == 1
    stats = rows[0]["stats"]
    assert stats["passYards"] == 3000
    assert stats["passTD"] == 30
    assert stats["passINT"] == 5
    assert round(stats["completionPct"], 4) == round(240 / 360, 4)
    assert stats["totalOffenseYards"] == 3500
    assert rows[0]["slotEligibility"] == ["QB"]


def _make_scored_players():
    rows = []
    for season in (2023, 2024):
        for idx in range(14):
            team = "Test U"
            base = 500 + idx * 100
            specs = [
                ("QB", {"passYards": 1500 + base * 2, "passTD": 10 + idx * 2, "passINT": max(1, 14 - idx), "passAttempts": 250, "passCompletions": 160, "rushYards": base / 3, "rushTD": idx / 2}),
                ("RB", {"rushYards": 700 + base, "rushTD": 4 + idx, "rushCarries": 130 + idx * 3, "recvYards": 100 + idx * 20, "receptions": 15 + idx, "recvTD": idx / 3}),
                ("WR", {"recvYards": 500 + base, "recvTD": 3 + idx, "receptions": 35 + idx * 2, "rushYards": idx * 10, "rushTD": idx / 5}),
                ("DL", {"tackles": 25 + idx * 3, "tacklesForLoss": 4 + idx, "sacks": 2 + idx / 2, "forcedFumbles": idx / 4, "passesDefended": idx / 3, "defInterceptions": 0}),
                ("LB", {"tackles": 45 + idx * 5, "tacklesForLoss": 4 + idx, "sacks": idx / 2, "forcedFumbles": idx / 4, "passesDefended": idx / 3, "defInterceptions": idx / 5}),
                ("DB", {"tackles": 25 + idx * 3, "tacklesForLoss": idx / 2, "sacks": idx / 4, "forcedFumbles": idx / 5, "passesDefended": 4 + idx, "defInterceptions": 1 + idx / 3}),
            ]
            for pos, stats in specs:
                if pos in {"RB", "WR"}:
                    stats = dict(stats)
                    stats["scrimmageYards"] = stats.get("rushYards", 0) + stats.get("recvYards", 0)
                    stats["totalTD"] = stats.get("rushTD", 0) + stats.get("recvTD", 0)
                    stats["touches"] = stats.get("rushCarries", 0) + stats.get("receptions", 0)
                    stats["yardsPerCarry"] = stats.get("rushYards", 0) / max(1, stats.get("rushCarries", 0))
                    stats["yardsPerReception"] = stats.get("recvYards", 0) / max(1, stats.get("receptions", 0))
                    stats["yardsPerTouch"] = stats["scrimmageYards"] / max(1, stats["touches"])
                if pos == "QB":
                    stats = dict(stats)
                    stats["completionPct"] = stats["passCompletions"] / stats["passAttempts"]
                    stats["totalOffenseYards"] = stats["passYards"] + stats["rushYards"]
                rows.append(
                    {
                        "season": season,
                        "playerId": int(f"{season}{idx}{len(rows) % 10}"),
                        "player": f"{pos} {season}-{idx}",
                        "team": team,
                        "position": pos,
                        "positionGroup": pos,
                        "slotEligibility": list(_slot_eligibility(pos)),
                        "stats": stats,
                        "teamId": 1,
                        "conference": "TEST",
                        "abbreviation": "TU",
                        "logo": "x",
                    }
                )
    score_players(rows)
    assign_nil_prices(rows)
    return rows


def test_grades_are_monotone_for_clear_qb_example():
    rows = _make_scored_players()
    qbs = [r for r in rows if r["positionGroup"] == "QB" and r["season"] == 2024]
    worst = min(qbs, key=lambda r: r["slotRatings"]["QB"]["eraScore"])
    best = max(qbs, key=lambda r: r["slotRatings"]["QB"]["eraScore"])
    assert best["slotRatings"]["QB"]["grade"] > worst["slotRatings"]["QB"]["grade"]
    assert best["nilAskMillions"] >= worst["nilAskMillions"]
    assert letter_grade(98) == "A+"
    assert letter_grade(94) == "A"


def _player(slot: str, ident: str, z: float, ask: float):
    return {
        "playerSeasonId": ident,
        "player": ident,
        "slot": slot,
        "powerZ": z,
        "nilAskMillions": ask,
        "grade": 95,
    }


def test_budget_optimizer_fills_unique_players():
    board = {}
    for i, slot in enumerate(SLOT_ORDER):
        board[slot] = [
            _player(slot, f"{slot}-cheap", 0.5 + i / 10, 1.0),
            _player(slot, f"{slot}-elite", 1.5 + i / 10, 3.0),
        ]
    lineup = _best_board_lineup(board, 15.0)
    assert lineup is not None
    assert set(lineup) == set(SLOT_ORDER)
    assert len({p["playerSeasonId"] for p in lineup.values()}) == 7
    assert sum(p["nilAskMillions"] for p in lineup.values()) <= 15.0


def test_equal_roster_power_maps_to_fifty_percent():
    lineup = {slot: _player(slot, slot, 1.0, 1.0) for slot in SLOT_ORDER}
    calibration = {"rosterPowerToMargin": 8.0, "residualSd": 14.0}
    result = evaluate_lineup(lineup, lineup, calibration)
    assert abs(roster_power(lineup) - 1.0) < 1e-12
    assert abs(result["expectedNeutralMargin"]) < 1e-12
    assert abs(result["winProbability"] - 0.5) < 1e-12
    assert result["win"] is False

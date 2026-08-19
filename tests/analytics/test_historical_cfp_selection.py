import pytest

from cfb_analytics.analytics.historical_cfp_selection import ResumeRow, build_resume_rows, leave_one_season_out


def game(team_id: int, team: str, opponent_id: int, opponent: str, win: int, points_for: int, points_against: int) -> dict:
    return {"season_type": "regular", "team_id": team_id, "team": team, "opponent_id": opponent_id, "opponent": opponent, "win": win, "loss": 1 - win, "points_for": points_for, "points_against": points_against}


def test_resume_uses_opponent_record_for_schedule_strength() -> None:
    games = [
        game(1, "A", 2, "B", 1, 30, 20), game(1, "A", 3, "C", 1, 24, 10),
        game(2, "B", 1, "A", 0, 20, 30), game(2, "B", 3, "C", 1, 21, 7),
        game(3, "C", 1, "A", 0, 10, 24), game(3, "C", 2, "B", 0, 7, 21),
    ]
    rows = {row.team: row for row in build_resume_rows(2023, games, {"A"}, {"A"})}
    assert rows["A"].strength_of_schedule == pytest.approx(0.25)
    assert rows["A"].quality_wins == 0
    assert rows["A"].conference_champion is True


def test_leave_one_season_out_respects_each_field_size() -> None:
    rows = []
    for season in (2022, 2023, 2024):
        field_size = 2 if season < 2024 else 3
        for index in range(8):
            wins = 12 - index
            rows.append(ResumeRow(season, season * 10 + index, f"Team {index}", wins, index % 4, wins / 12, 0.45 + index / 100, max(0, 4 - index), 22 - index * 2, index == 0, index < field_size))
    scored, audit = leave_one_season_out(rows)
    for season in (2022, 2023, 2024):
        season_rows = [row for row in scored if row["season"] == season]
        assert sum(row["selectionChance"] for row in season_rows) == pytest.approx(2 if season < 2024 else 3, abs=1e-5)
        assert all(0 <= row["selectionChance"] <= 1 for row in season_rows)
    assert audit["evaluation"] == "leave-one-season-out"
    assert audit["maxFieldSizeSumError"] <= 0.00001

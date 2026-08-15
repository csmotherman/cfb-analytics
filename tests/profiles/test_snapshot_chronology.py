from cfb_analytics.profiles.opponent_adjustment import METRIC_SPECS
from cfb_analytics.profiles.snapshots import build_identity_snapshots


def _row(game_id: str, team: str, opponent: str, start_date: str, value: float):
    row = {
        "season": 2023,
        "seasonType": "postseason",
        "week": 1,
        "gameId": game_id,
        "team": team,
        "opponent": opponent,
        "startDate": start_date,
        "gameValidationStatus": "PASS",
        "validatedPossessions": 10,
        "offensivePlays": 60,
    }
    for spec in METRIC_SPECS:
        row[spec.denominator] = 100.0
        row[spec.numerator] = 100.0 * value
    return row


def test_same_partition_games_advance_by_start_date():
    rows = [
        _row("g1", "A", "B", "2024-01-01T22:00:00.000Z", 0.80),
        _row("g1", "B", "A", "2024-01-01T22:00:00.000Z", 0.20),
        _row("g2", "A", "C", "2024-01-09T00:30:00.000Z", 0.20),
        _row("g2", "C", "A", "2024-01-09T00:30:00.000Z", 0.80),
    ]

    snapshots = build_identity_snapshots(rows, min_games=1, recent_games=1)
    a = [x for x in snapshots if x["team"] == "A"]

    assert [x["throughGameId"] for x in a] == ["g1", "g2"]
    assert [x["startDate"] for x in a] == [
        "2024-01-01T22:00:00.000Z",
        "2024-01-09T00:30:00.000Z",
    ]
    assert a[0]["baseline_oa_success_off"] != a[1]["baseline_oa_success_off"]


def test_simultaneous_games_share_one_adjustment_context():
    rows = [
        _row("g1", "A", "B", "2024-01-01T22:00:00.000Z", 0.80),
        _row("g1", "B", "A", "2024-01-01T22:00:00.000Z", 0.20),
        _row("g2", "C", "D", "2024-01-01T22:00:00.000Z", 0.70),
        _row("g2", "D", "C", "2024-01-01T22:00:00.000Z", 0.30),
    ]

    snapshots = build_identity_snapshots(rows, min_games=1, recent_games=1)

    assert len(snapshots) == 4
    assert {x["startDate"] for x in snapshots} == {"2024-01-01T22:00:00.000Z"}

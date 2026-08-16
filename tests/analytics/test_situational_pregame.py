from collections import defaultdict

from cfb_analytics.analytics.situational_pregame import (
    BUCKETS,
    add_rows,
    bucket_names,
    snapshot_before_partition,
)


def _row(**kwargs):
    base = {
        "team": "Michigan",
        "side": "offense",
        "down": 3,
        "distance": 2,
        "half": 1,
        "redZone": False,
        "goalToGo": False,
        "plays": 1,
        "successes": 1,
        "yards": 3,
        "firstDowns": 1,
        "rushPlays": 1,
        "passPlays": 0,
        "rushSuccesses": 1,
        "passSuccesses": 0,
        "rushYards": 3,
        "passYards": 0,
        "explosiveEligiblePlays": 1,
        "explosivePlays": 0,
        "conversionAttempts": 1,
        "conversions": 1,
    }
    base.update(kwargs)
    return base


def test_bucket_names_are_broad_and_stable():
    assert bucket_names(_row(down=3, distance=2)) == ("all_plays", "third_short")
    assert bucket_names(_row(down=3, distance=5)) == ("all_plays", "third_medium")
    assert bucket_names(_row(down=3, distance=12)) == ("all_plays", "third_long")
    assert bucket_names(_row(down=2, distance=10, half=2, redZone=True)) == (
        "all_plays",
        "early_down",
        "red_zone",
        "second_half",
    )


def test_snapshot_is_taken_before_current_partition_is_added():
    acc = {}

    week1 = snapshot_before_partition(
        acc,
        season=2023,
        season_type="regular",
        week=1,
        teams=["Michigan"],
    )
    assert len(week1) == 2 * len(BUCKETS)
    assert all(r["plays"] == 0 for r in week1)

    add_rows(acc, [_row()])

    week2 = snapshot_before_partition(
        acc,
        season=2023,
        season_type="regular",
        week=2,
        teams=["Michigan"],
    )
    short = next(
        r for r in week2
        if r["team"] == "Michigan"
        and r["side"] == "offense"
        and r["bucket"] == "third_short"
    )
    assert short["plays"] == 1
    assert short["conversionRate"] == 1.0


def test_offense_and_defense_accumulate_separately():
    acc = {}
    add_rows(acc, [_row(), _row(team="Ohio State", side="defense")])

    assert acc[("Michigan", "offense", "third_short")]["plays"] == 1
    assert acc[("Ohio State", "defense", "third_short")]["plays"] == 1
    assert ("Michigan", "defense", "third_short") not in acc

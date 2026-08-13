from cfb_analytics.analytics.basic_yardage_final_forensics import merge


def test_recovered_interception_attempts_are_denominator_only():
    result = merge(
        [
            {
                "counts": {
                    "standard_dropbacks": 10,
                    "standard_dropback_yards": 80,
                    "recovered_int_attempts": 2,
                    "excluded_recovered_int_return_yards": -55,
                    "rush_attempts": 5,
                    "rush_yards": 25,
                }
            }
        ]
    )

    counts = result["counts"]
    assert counts["dropbacks"] == 12
    assert counts["dropback_yards"] == 80
    assert counts["excluded_recovered_int_return_yards"] == -55
    assert counts["classified_scrimmage_events"] == 17
    assert counts["classified_scrimmage_yards"] == 105


def test_recovered_interception_return_yards_never_change_passing_numerator():
    negative_return = merge(
        [
            {
                "counts": {
                    "standard_dropbacks": 4,
                    "standard_dropback_yards": 30,
                    "recovered_int_attempts": 1,
                    "excluded_recovered_int_return_yards": -99,
                    "rush_attempts": 0,
                    "rush_yards": 0,
                }
            }
        ]
    )["counts"]
    positive_return = merge(
        [
            {
                "counts": {
                    "standard_dropbacks": 4,
                    "standard_dropback_yards": 30,
                    "recovered_int_attempts": 1,
                    "excluded_recovered_int_return_yards": 100,
                    "rush_attempts": 0,
                    "rush_yards": 0,
                }
            }
        ]
    )["counts"]

    assert negative_return["dropback_yards"] == 30
    assert positive_return["dropback_yards"] == 30
    assert negative_return["dropbacks"] == positive_return["dropbacks"] == 5

from cfb_analytics.aggregations.rankings import Metric, add_rankings


def test_rank_direction_and_competition_ties():
    metric = Metric("value", "Value", "rate", False, "defense", "defense")
    rows = add_rankings([{"value": 0.2}, {"value": 0.1}, {"value": 0.1}, {"value": 0.3}], [metric])
    assert [row["national_value_rank"] for row in rows] == [3, 1, 1, 4]
    assert rows[1]["national_value_percentile"] == 1.0
    assert rows[3]["national_value_percentile"] == 0.0


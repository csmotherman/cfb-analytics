from cfb_analytics.raw.acquire import calendar_partitions


def test_calendar_partitions_supports_api_camel_case():
    calendar = [
        {"season": 2025, "week": 1, "seasonType": "regular"},
        {"season": 2025, "week": 2, "seasonType": "regular"},
        {"season": 2025, "week": 1, "seasonType": "postseason"},
    ]
    assert calendar_partitions(calendar) == [("postseason", 1), ("regular", 1), ("regular", 2)]

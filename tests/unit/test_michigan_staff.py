import json
from pathlib import Path


def test_michigan_staff_table_covers_supported_seasons_and_labels_2026_preseason():
    path = Path("src/cfb_analytics/config/michigan_staff.json")
    payload = json.loads(path.read_text())
    rows = {row["season"]: row for row in payload["seasons"]}
    assert set(rows) == set(range(2010, 2027))
    assert rows[2025]["value_type"] == "ACTUAL"
    assert rows[2026]["value_type"] == "PRESEASON"
    assert rows[2026]["head_coach"] == "Kyle Whittingham"
    assert payload["sources"]

import json
from pathlib import Path

from cfb_analytics.canonical.materialize import materialize_partition, verify_canonical_partition


def _write_raw(root: Path):
    d = root / "cfbd" / "season=2025" / "season_type=regular" / "week=01"
    d.mkdir(parents=True)
    rows = [
        {"id": "1", "playType": "Timeout", "yardsGained": 9},
        {"id": "2", "playType": "Rush", "yardsGained": 5},
    ]
    (d / "plays.json").write_text(json.dumps(rows), encoding="utf-8")


def test_materialize_partition_preserves_raw_and_writes_manifest(tmp_path: Path):
    raw = tmp_path / "raw"; processed = tmp_path / "processed"; _write_raw(raw)
    before = (raw / "cfbd" / "season=2025" / "season_type=regular" / "week=01" / "plays.json").read_text()
    result = materialize_partition(raw, processed, 2025, "regular", 1)
    assert result["status"] == "WRITTEN"
    target = processed / "canonical" / "season=2025" / "season_type=regular" / "week=01" / "plays.json"
    rows = json.loads(target.read_text())
    assert rows[0]["sourceYardsGained"] == 9 and rows[0]["analyticsYardsGained"] == 0
    assert rows[1]["sourceYardsGained"] == 5 and rows[1]["analyticsYardsGained"] == 5
    assert before == (raw / "cfbd" / "season=2025" / "season_type=regular" / "week=01" / "plays.json").read_text()
    assert verify_canonical_partition(raw, processed, 2025, "regular", 1)["status"] == "PASS"


def test_materialize_reuses_unchanged_partition(tmp_path: Path):
    raw = tmp_path / "raw"; processed = tmp_path / "processed"; _write_raw(raw)
    materialize_partition(raw, processed, 2025, "regular", 1)
    second = materialize_partition(raw, processed, 2025, "regular", 1)
    assert second["status"] == "REUSED"

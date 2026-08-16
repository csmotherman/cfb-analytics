import json
from pathlib import Path

from cfb_analytics.profiles import snapshots


def _write_snapshot(processed_root: Path) -> Path:
    target = processed_root / "derived" / "profiles" / snapshots.SNAPSHOT_FILENAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            [
                {
                    "season": 2025,
                    "team": "Example",
                    "snapshotVersion": snapshots.SNAPSHOT_VERSION,
                }
            ]
        )
    )
    return target


def test_existing_current_snapshot_is_reused_without_rebuild(tmp_path, monkeypatch):
    processed_root = tmp_path / "processed"
    target = _write_snapshot(processed_root)
    source = tmp_path / "source.json"
    source.write_text("[]")

    # Ensure the source is older than the already-built artifact.
    source.touch()
    target.touch()
    monkeypatch.setattr(snapshots, "_snapshot_source_files", lambda *_args, **_kwargs: [source])

    reusable, rows = snapshots._can_reuse_snapshots(
        processed_root,
        min_games=snapshots.DEFAULT_MIN_GAMES,
        recent_games=snapshots.DEFAULT_RECENT_GAMES,
    )

    assert reusable is True
    assert rows is not None
    assert rows[0]["snapshotVersion"] == snapshots.SNAPSHOT_VERSION
    assert (processed_root / "derived" / "profiles" / snapshots.SNAPSHOT_CACHE_FILENAME).exists()


def test_changed_source_invalidates_snapshot_cache(tmp_path, monkeypatch):
    processed_root = tmp_path / "processed"
    target = _write_snapshot(processed_root)
    source = tmp_path / "source.json"
    source.write_text("[]")
    monkeypatch.setattr(snapshots, "_snapshot_source_files", lambda *_args, **_kwargs: [source])

    manifest = {
        "snapshotVersion": snapshots.SNAPSHOT_VERSION,
        "minGames": snapshots.DEFAULT_MIN_GAMES,
        "recentGames": snapshots.DEFAULT_RECENT_GAMES,
        "newestSourceMtimeNs": source.stat().st_mtime_ns,
        "sourceFileCount": 1,
    }
    cache = processed_root / "derived" / "profiles" / snapshots.SNAPSHOT_CACHE_FILENAME
    cache.write_text(json.dumps(manifest))

    source.write_text("changed")

    reusable, rows = snapshots._can_reuse_snapshots(
        processed_root,
        min_games=snapshots.DEFAULT_MIN_GAMES,
        recent_games=snapshots.DEFAULT_RECENT_GAMES,
    )

    assert reusable is False
    assert rows is None


def test_force_flag_bypasses_reuse(tmp_path, monkeypatch):
    processed_root = tmp_path / "processed"
    _write_snapshot(processed_root)
    monkeypatch.setattr(snapshots, "_can_reuse_snapshots", lambda *_args, **_kwargs: (True, [{"season": 2025, "team": "Example"}]))

    called = {"load": False}

    def fake_load(_root):
        called["load"] = True
        return []

    monkeypatch.setattr(snapshots, "load_team_games", fake_load)
    monkeypatch.setattr(snapshots, "build_identity_snapshots", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(snapshots, "add_context_percentiles", lambda rows: rows)
    monkeypatch.setattr(snapshots, "_cache_manifest", lambda *_args, **_kwargs: {})

    snapshots.materialize_identity_snapshots(processed_root, force=True)

    assert called["load"] is True

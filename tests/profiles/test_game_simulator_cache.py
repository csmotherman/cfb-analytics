from pathlib import Path

from cfb_analytics.profiles.game_simulator_cache import load_or_build


def test_cache_reuses_prepared_bundle(tmp_path: Path):
    path = tmp_path / "sim.json"
    calls = {"n": 0}

    def builder():
        calls["n"] += 1
        return {"residualSd": 10.0, "trainingRows": 1}, [{"season": 2025, "team": "A"}]

    first = load_or_build(
        path,
        simulator_version="sim-v1",
        tournament_version="tourn-v1",
        seasons=(2025,),
        builder=builder,
    )
    second = load_or_build(
        path,
        simulator_version="sim-v1",
        tournament_version="tourn-v1",
        seasons=(2025,),
        builder=builder,
    )

    assert first[2] == "WRITTEN"
    assert second[2] == "REUSED"
    assert calls["n"] == 1
    assert second[0]["residualSd"] == 10.0
    assert second[1][0]["team"] == "A"


def test_refresh_rebuilds_cache(tmp_path: Path):
    path = tmp_path / "sim.json"
    calls = {"n": 0}

    def builder():
        calls["n"] += 1
        return {"residualSd": float(calls["n"])}, []

    load_or_build(
        path,
        simulator_version="sim-v1",
        tournament_version="tourn-v1",
        seasons=(2025,),
        builder=builder,
    )
    refreshed = load_or_build(
        path,
        simulator_version="sim-v1",
        tournament_version="tourn-v1",
        seasons=(2025,),
        builder=builder,
        refresh=True,
    )

    assert refreshed[2] == "WRITTEN"
    assert calls["n"] == 2
    assert refreshed[0]["residualSd"] == 2.0

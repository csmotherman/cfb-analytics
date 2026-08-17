from __future__ import annotations

import pytest

from cfb_analytics.analytics.prediction_v1_site_aware_challenger import SITE_AWARE
from cfb_analytics.analytics.prediction_v2_notebook_feature_challenger import (
    ALL_COMPONENTS,
    EFFICIENCY,
    NEW_CORE,
    NOTEBOOK_DRIVE_CONV,
    NOTEBOOK_EPA,
    NOTEBOOK_OVERALL,
    NOTEBOOK_PPD,
    NOTEBOOK_SPREAD,
    NOTEBOOK_SR,
    VARIANTS,
    _feature_tuple,
    merge_common_rows,
)


def _v2(gid: str, margin: float = 3.0) -> dict:
    return {
        "gameId": gid,
        "homeTeam": "Home",
        "awayTeam": "Away",
        "target_margin": margin,
        "target_homeWin": margin > 0,
    }


def _notebook(gid: str, margin: float = 3.0) -> dict:
    return {
        "gameId": gid,
        "homeTeam": "Home",
        "awayTeam": "Away",
        "target_margin": margin,
        NOTEBOOK_SPREAD: 1.0,
        NOTEBOOK_SR: 2.0,
        NOTEBOOK_EPA: 3.0,
        NOTEBOOK_PPD: 4.0,
        NOTEBOOK_DRIVE_CONV: 5.0,
        NOTEBOOK_OVERALL: 3.0,
    }


def test_predeclared_variants_are_exact_and_exclude_overall() -> None:
    assert NEW_CORE == (NOTEBOOK_EPA, NOTEBOOK_PPD, NOTEBOOK_DRIVE_CONV)
    assert EFFICIENCY == (NOTEBOOK_SR, NOTEBOOK_EPA, NOTEBOOK_PPD, NOTEBOOK_DRIVE_CONV)
    assert ALL_COMPONENTS == (
        NOTEBOOK_SPREAD,
        NOTEBOOK_SR,
        NOTEBOOK_EPA,
        NOTEBOOK_PPD,
        NOTEBOOK_DRIVE_CONV,
    )
    assert set(VARIANTS) == {"NEW_CORE", "EFFICIENCY", "ALL_COMPONENTS"}
    assert all(NOTEBOOK_OVERALL not in features for features in VARIANTS.values())


def test_feature_tuple_keeps_v2_architecture_first() -> None:
    features = _feature_tuple(NEW_CORE)
    assert features[: len(SITE_AWARE)] == tuple(SITE_AWARE)
    assert features[len(SITE_AWARE) :] == NEW_CORE


def test_merge_common_rows_joins_only_common_ids_and_adds_notebook_features() -> None:
    merged = merge_common_rows([_v2("1"), _v2("2")], [_notebook("2"), _notebook("3")])
    assert [row["gameId"] for row in merged] == ["2"]
    assert merged[0][NOTEBOOK_EPA] == 3.0
    assert merged[0][NOTEBOOK_OVERALL] == 3.0


def test_merge_common_rows_rejects_target_mismatch() -> None:
    with pytest.raises(ValueError, match="Target mismatch"):
        merge_common_rows([_v2("1", 3.0)], [_notebook("1", 4.0)])


def test_merge_common_rows_rejects_team_mismatch() -> None:
    bad = _notebook("1")
    bad["homeTeam"] = "Different"
    with pytest.raises(ValueError, match="Home-team mismatch"):
        merge_common_rows([_v2("1")], [bad])


def test_merge_common_rows_rejects_duplicate_game_ids() -> None:
    with pytest.raises(ValueError, match="Duplicate gameId"):
        merge_common_rows([_v2("1"), _v2("1")], [_notebook("1")])

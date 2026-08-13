from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES, eligible_iterative_row
from cfb_analytics.analytics.walk_forward_baseline import FEATURES as RAW_FEATURES


def _row(games):
    r={"homeIterativeGamesPlayedBefore":games,"awayIterativeGamesPlayedBefore":games,"target_margin":7.0,"target_homeWin":1}
    r.update({k:0.1 for k in ITERATIVE_FEATURES})
    r.update({k:0.2 for k in RAW_FEATURES})
    return r


def test_three_game_gate_accepts_three_but_four_game_gate_does_not():
    r=_row(3)
    assert eligible_iterative_row(r,3)
    assert not eligible_iterative_row(r,4)


def test_four_game_gate_accepts_four():
    assert eligible_iterative_row(_row(4),4)


def test_raw_iterative_and_combined_feature_sets_are_complete_on_same_row():
    r=_row(4)
    assert all(k in r for k in RAW_FEATURES)
    assert all(k in r for k in ITERATIVE_FEATURES)
    assert len(RAW_FEATURES)==14
    assert len(ITERATIVE_FEATURES)==12
    assert len(tuple(RAW_FEATURES)+tuple(ITERATIVE_FEATURES))==26

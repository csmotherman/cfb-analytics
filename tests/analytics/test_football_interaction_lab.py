import importlib.util
from pathlib import Path

import pytest

from cfb_analytics.analytics.football_mechanisms import TEAM_FIELDS,orient_matchup

_HARNESS_PATH=Path(__file__).with_name("football_interaction_lab_harness.py")
_SPEC=importlib.util.spec_from_file_location("football_interaction_lab_harness",_HARNESS_PATH)
_MODULE=importlib.util.module_from_spec(_SPEC)
assert _SPEC is not None and _SPEC.loader is not None
_SPEC.loader.exec_module(_MODULE)
add_lab_features=_MODULE.add_lab_features


def _team(prefix):
    return {f"{prefix}_{f}":0.5 for f in TEAM_FIELDS}


def test_scoring_chain_and_volume_features():
    m={"team1":"Home","team2":"Away"}
    m.update(_team("team1"));m.update(_team("team2"))
    m.update({
        "team1_OffScoringOpportunityRate":0.50,
        "team2_DefScoringOpportunityRateAllowed":0.40,
        "team2_OffScoringOpportunityRate":0.30,
        "team1_DefScoringOpportunityRateAllowed":0.35,
        "team1_OffPointsPerOpportunity":4.0,
        "team2_DefPointsPerOpportunityAllowed":3.0,
        "team2_OffPointsPerOpportunity":2.5,
        "team1_DefPointsPerOpportunityAllowed":3.5,
        "team1_OffTouchdownOpportunityRate":0.60,
        "team2_DefTouchdownOpportunityRateAllowed":0.50,
        "team2_OffTouchdownOpportunityRate":0.40,
        "team1_DefTouchdownOpportunityRateAllowed":0.45,
        "team1_OffPossessionsPerGame":12.0,
        "team2_DefPossessionsPerGame":12.0,
        "team2_OffPossessionsPerGame":10.0,
        "team1_DefPossessionsPerGame":10.0,
    })
    x=orient_matchup(m,"Home","Away")
    r={"homeTeam":"Home","awayTeam":"Away","home_MWDR_OffenseEdge":0.2,"home_MWDR_DefenseEdge":0.1}
    z=add_lab_features(r,m,x)
    assert z is not None
    assert z["expectedScoringPpdEdge"]==pytest.approx(0.6)
    assert z["expectedScoringMarginProxy"]==pytest.approx(6.6)
    assert z["expectedTdDriveEdge"]==pytest.approx(0.109375)
    assert z["mwdrXExpectedPossessions"]==pytest.approx(3.3)

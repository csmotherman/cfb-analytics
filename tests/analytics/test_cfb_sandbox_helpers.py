from cfb_analytics.analytics.cfb_sandbox_systems import RECENT_GAMES,EXPLOSIVE_YARDS,CLOSE_MARGIN

def test_sandbox_constants():
    assert RECENT_GAMES==3
    assert EXPLOSIVE_YARDS==20
    assert CLOSE_MARGIN==7

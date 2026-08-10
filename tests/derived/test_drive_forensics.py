from cfb_analytics.derived.drive_forensics import _drive_profile


def row(**kw):
    base={"eventCategory":"SCRIMMAGE","eventSubtype":"RUSH","sourcePlayType":"Rush","isAdministrative":False,"isSpecialTeams":False,"isOffensivePlay":True,"isScrimmagePlay":True,"offense":"A"}
    base.update(kw); return base


def test_conflicting_scrimmage_ownership_profile():
    assert _drive_profile([row(),row(offense="B")])=="CONFLICTING_SCRIMMAGE_OWNERSHIP"


def test_administrative_only_profile():
    assert _drive_profile([row(isAdministrative=True,isOffensivePlay=False,isScrimmagePlay=False,eventCategory="ADMINISTRATIVE")])=="ADMINISTRATIVE_ONLY"


def test_special_teams_only_profile():
    assert _drive_profile([row(isSpecialTeams=True,isOffensivePlay=False,isScrimmagePlay=False,eventCategory="SPECIAL_TEAMS")])=="SPECIAL_TEAMS_ONLY"

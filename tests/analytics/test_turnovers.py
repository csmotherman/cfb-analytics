from cfb_analytics.analytics.turnovers import classify_possession_turnover
from cfb_analytics.analytics.turnover_forensics import build_play_index

def d():return {"gameId":"1","driveId":"d1","sourceDriveId":"d1","offense":"A","defense":"B","isPossessionDrive":True,"driveValidationStatus":"PASS"}
def p(sub,is_turn=True,no_play=False):return {"gameId":"1","driveId":"d1","eventSubtype":sub,"isTurnover":is_turn,"hasNoPlayContext":no_play}
def classify(rows):return classify_possession_turnover(d(),build_play_index(rows))
def test_direct_interception_is_giveaway():
 r=classify([p("INTERCEPTION")]);assert r["giveaway"]==1 and r["interceptionThrown"]==1
def test_return_only_interception_is_giveaway():
 r=classify([p("INTERCEPTION_RETURN")]);assert r["giveaway"]==1 and r["interceptionThrown"]==1
def test_lost_fumble_is_giveaway():
 r=classify([p("FUMBLE_RECOVERY_OPPONENT")]);assert r["giveaway"]==1 and r["fumbleLost"]==1
def test_own_recovery_is_resolved_no_giveaway():
 r=classify([p("FUMBLE_RECOVERY_OWN")]);assert r["giveaway"]==0 and r["turnoverResolved"] is True
def test_nullified_turnover_is_excluded():
 r=classify([p("INTERCEPTION",no_play=True)]);assert r["giveaway"]==0 and r["turnoverResolved"] is False
def test_unresolved_fumble_is_not_guessed():
 r=classify([p("FUMBLE")]);assert r["giveaway"]==0 and r["turnoverResolved"] is False

from cfb_analytics.analytics.turnover_forensics import classify_drive_turnover

def d():return {"gameId":"1","driveId":"d1","sourceDriveId":"d1","offense":"A","defense":"B","isPossessionDrive":True,"driveValidationStatus":"PASS"}
def p(sub,is_turn=True,**kw):return {"gameId":"1","driveId":"d1","eventSubtype":sub,"isTurnover":is_turn,"hasNoPlayContext":False,**kw}
def test_interception_is_one_giveaway_despite_return_record():assert classify_drive_turnover(d(),[p("INTERCEPTION"),p("INTERCEPTION_RETURN")])=="INTERCEPTION"
def test_opponent_fumble_recovery_is_fumble_lost():assert classify_drive_turnover(d(),[p("FUMBLE",False),p("FUMBLE_RECOVERY_OPPONENT")])=="FUMBLE_LOST"
def test_own_fumble_recovery_is_not_giveaway():assert classify_drive_turnover(d(),[p("FUMBLE",False),p("FUMBLE_RECOVERY_OWN")])=="TURNOVER_RECORD_WITHOUT_GIVEAWAY_SIGNAL"
def test_no_turnover():assert classify_drive_turnover(d(),[p("RUSH",False)])=="NO_EXPLICIT_TURNOVER"

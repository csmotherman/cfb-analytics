from cfb_analytics.derived.drives import derive_drive, derive_partition_drives


def play(**kw):
    base={"id":"p1","gameId":"g1","driveId":"d1","driveNumber":1,"offense":"A","defense":"B","period":1,"clock":{"minutes":10,"seconds":0},"down":1,"distance":10,"yardsToGoal":70,"offenseScore":0,"defenseScore":0,"isOffensivePlay":True,"isScrimmagePlay":True,"hasNoPlayContext":False,"analyticsYardsGained":4,"analyticsYardsWasCorrected":False,"eventCategory":"SCRIMMAGE","sourcePlayType":"Rush"}
    base.update(kw); return base


def test_drive_aggregates_canonical_play_membership():
    d=derive_drive("g1","d1",[play(),play(id="p2",down=2,distance=6,yardsToGoal=66,analyticsYardsGained=6)],2025,"regular",1)
    assert d["playCount"]==2 and d["analyticsYardsGained"]==10 and d["isPossessionDrive"] is True
    assert d["offense"]=="A" and d["defense"]=="B" and d["driveValidationStatus"]=="PASS"


def test_non_scrimmage_team_flip_does_not_change_drive_ownership():
    d=derive_drive("g1","d1",[play(),play(id="p2",isOffensivePlay=False,isScrimmagePlay=False,offense="B",defense="A")],2025,"regular",1)
    assert d["offense"]=="A" and d["defense"]=="B"


def test_other_offensive_play_can_fallback_when_no_scrimmage_evidence():
    d=derive_drive("g1","d1",[play(isScrimmagePlay=False)],2025,"regular",1)
    assert d["driveOwnershipSource"]=="other_offensive_plays"


def test_event_only_group_is_not_a_possession_drive():
    rows=[play(isOffensivePlay=False,isScrimmagePlay=False,eventCategory="SPECIAL_TEAMS",sourcePlayType="Kickoff")]
    drives,_=derive_partition_drives(rows,2025,"regular",1); d=drives[0]
    assert d["isPossessionDrive"] is False
    assert d["nonPossessionProfile"]=="NO_OFFENSIVE_PLAY" or d["nonPossessionProfile"]=="SPECIAL_TEAMS_ONLY"
    assert d["driveValidationStatus"]=="PASS"


def test_neighbor_resolution_ignores_event_only_group():
    rows=[play(id="a1",driveId="d1",driveNumber=1,offense="A",defense="B"),play(id="e1",driveId="d2",driveNumber=2,isOffensivePlay=False,isScrimmagePlay=False,eventCategory="SPECIAL_TEAMS",sourcePlayType="Kickoff"),play(id="b1",driveId="d3",driveNumber=3,offense="B",defense="A")]
    drives,_=derive_partition_drives(rows,2025,"regular",1); event=[d for d in drives if d["driveId"]=="d2"][0]
    assert event["isPossessionDrive"] is False and event["offense"] is None and event["defense"] is None


def test_conflicting_majority_can_resolve_with_opponent_context():
    rows=[play(id="a1",driveId="d1",driveNumber=1,offense="A",defense="B"),play(id="c1",driveId="d2",driveNumber=2,offense="B",defense="A"),play(id="c2",driveId="d2",driveNumber=2,offense="B",defense="A"),play(id="c3",driveId="d2",driveNumber=2,offense="A",defense="B"),play(id="a2",driveId="d3",driveNumber=3,offense="A",defense="B")]
    drives,_=derive_partition_drives(rows,2025,"regular",1); middle=[d for d in drives if d["driveId"]=="d2"][0]
    assert middle["offense"]=="B" and middle["defense"]=="A"
    assert middle["driveOwnershipSource"]=="scrimmage_majority_with_game_context"
    assert middle["driveValidationStatus"]=="PASS"


def test_partition_skips_only_plays_without_drive_id():
    rows=[play(),play(id="p2",driveId="d2",driveNumber=2),play(id="p3",driveId=None)]
    drives,coverage=derive_partition_drives(rows,2025,"regular",1)
    assert len(drives)==2 and coverage["plays_with_drive_id"]==2 and coverage["plays_without_drive_id"]==1

from cfb_analytics.derived.drives import derive_drive, derive_partition_drives


def play(**kw):
    base={
        "id":"p1","gameId":"g1","driveId":"d1","driveNumber":1,
        "offense":"A","defense":"B","period":1,"clock":{"minutes":10,"seconds":0},
        "down":1,"distance":10,"yardsToGoal":70,"offenseScore":0,"defenseScore":0,
        "isOffensivePlay":True,"isScrimmagePlay":True,"hasNoPlayContext":False,
        "analyticsYardsGained":4,"analyticsYardsWasCorrected":False,
    }
    base.update(kw); return base


def test_drive_aggregates_canonical_play_membership():
    rows=[play(),play(id="p2",down=2,distance=6,yardsToGoal=66,analyticsYardsGained=6)]
    d=derive_drive("g1","d1",rows,2025,"regular",1)
    assert d["playCount"]==2
    assert d["offensivePlayCount"]==2
    assert d["ownershipEvidencePlayCount"]==2
    assert d["analyticsYardsGained"]==10
    assert d["offense"]=="A" and d["defense"]=="B"
    assert d["driveValidationStatus"]=="PASS"


def test_non_scrimmage_team_flip_does_not_change_drive_ownership():
    rows=[
        play(),
        play(id="p2",isOffensivePlay=False,isScrimmagePlay=False,offense="B",defense="A"),
    ]
    d=derive_drive("g1","d1",rows,2025,"regular",1)
    assert d["offense"]=="A" and d["defense"]=="B"
    assert d["driveValidationStatus"]=="PASS"


def test_drive_surfaces_conflicting_offensive_scrimmage_ownership():
    rows=[play(),play(id="p2",offense="C",defense="D")]
    d=derive_drive("g1","d1",rows,2025,"regular",1)
    assert d["driveValidationStatus"]=="REVIEW"
    assert "MULTIPLE_OWNERSHIP_OFFENSES" in d["driveValidationIssues"]
    assert "MULTIPLE_OWNERSHIP_DEFENSES" in d["driveValidationIssues"]


def test_drive_without_offensive_scrimmage_evidence_is_review():
    rows=[play(isOffensivePlay=False,isScrimmagePlay=False)]
    d=derive_drive("g1","d1",rows,2025,"regular",1)
    assert d["offense"] is None and d["defense"] is None
    assert "MISSING_OWNERSHIP_OFFENSE" in d["driveValidationIssues"]


def test_partition_skips_only_plays_without_drive_id():
    rows=[play(),play(id="p2",driveId="d2",driveNumber=2),play(id="p3",driveId=None)]
    drives,coverage=derive_partition_drives(rows,2025,"regular",1)
    assert len(drives)==2
    assert coverage["plays_with_drive_id"]==2
    assert coverage["plays_without_drive_id"]==1
    assert sum(d["playCount"] for d in drives)==2

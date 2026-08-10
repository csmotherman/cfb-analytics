from cfb_analytics.canonical.corrections import promote_partition_yardage, yardage_decision


def play(**kw):
    base={"id":"1","gameId":"g","driveId":"d","driveNumber":1,"playNumber":1,"offense":"A","period":1,"yardsToGoal":70,"sourceYardsGained":9,"analyticsYardsGained":9,"textYardsGained":4,"textParseConfidence":"HIGH","textAmbiguous":False,"hasStateTransitionModifier":False}
    base.update(kw); return base


def test_high_confidence_text_and_state_promote_analytics_yards():
    a=play(); b=play(id="2",playNumber=2,yardsToGoal=66,sourceYardsGained=0,analyticsYardsGained=0,textYardsGained=None,textParseConfidence="NONE")
    rows=promote_partition_yardage([a,b])
    assert rows[0]["analyticsYardsGained"]==4
    assert rows[0]["sourceYardsGained"]==9
    assert rows[0]["analyticsYardsWasCorrected"] is True
    assert rows[0]["analyticsYardsSource"]=="TEXT_AND_NEXT_STATE"
    assert rows[0]["analyticsYardsConfidence"]=="HIGH"


def test_structure_supported_over_text_is_not_changed():
    a=play(); b=play(id="2",playNumber=2,yardsToGoal=61,sourceYardsGained=0,analyticsYardsGained=0,textYardsGained=None,textParseConfidence="NONE")
    rows=promote_partition_yardage([a,b])
    assert rows[0]["analyticsYardsGained"]==9
    assert rows[0]["analyticsYardsWasCorrected"] is False
    assert rows[0]["analyticsYardsSource"]=="STRUCTURED_SUPPORTED_BY_NEXT_STATE"


def test_ambiguous_text_never_promotes():
    a=play(textAmbiguous=True); b=play(id="2",playNumber=2,yardsToGoal=66)
    assert yardage_decision(a,b)["status"]=="KEEP"

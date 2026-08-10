from cfb_analytics.canonical.evidence import adjudicate_pair


def play(**kw):
    base={
        "driveId":"d","offense":"A","period":1,"yardsToGoal":70,
        "sourceYardsGained":9,"textYardsGained":4,"textParseConfidence":"HIGH",
        "textAmbiguous":False,"hasStateTransitionModifier":False,
    }
    base.update(kw)
    return base


def test_text_and_field_state_can_overrule_structured_yards():
    a=play()
    b=play(yardsToGoal=66, sourceYardsGained=0, textYardsGained=None)
    r=adjudicate_pair(a,b)
    assert r["status"]=="HIGH_CONFIDENCE_CORRECTION_CANDIDATE"
    assert r["recommended_value"]==4


def test_field_state_can_support_structure_over_text():
    a=play(sourceYardsGained=9,textYardsGained=4)
    b=play(yardsToGoal=61, sourceYardsGained=0, textYardsGained=None)
    r=adjudicate_pair(a,b)
    assert r["status"]=="STRUCTURE_SUPPORTED_OVER_TEXT"
    assert r["recommended_value"]==9


def test_ambiguous_text_is_not_used_for_correction():
    a=play(textAmbiguous=True)
    b=play(yardsToGoal=66, sourceYardsGained=0, textYardsGained=None)
    assert adjudicate_pair(a,b)["status"]=="INSUFFICIENT_TEXT_EVIDENCE"


def test_text_structure_agreement_is_recorded():
    a=play(sourceYardsGained=4,textYardsGained=4)
    b=play(yardsToGoal=66, sourceYardsGained=0, textYardsGained=None)
    assert adjudicate_pair(a,b)["status"]=="TEXT_STRUCTURE_AGREE"

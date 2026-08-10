from cfb_analytics.canonical.plays import normalize_play


def test_normalize_does_not_mutate_source():
    source={"id":"1","playType":"Timeout","yardsGained":17,"down":2}
    before=dict(source)
    normalize_play(source)
    assert source==before


def test_source_fields_survive_normalization():
    source={"id":"1","gameId":"g","driveId":"d","playType":"Rush","yardsGained":8,"down":1,"distance":10}
    canon=normalize_play(source)
    for key,value in source.items():
        assert canon[key]==value


def test_administrative_yards_are_analytics_zero_only():
    source={"id":"1","playType":"End Period","yardsGained":44}
    canon=normalize_play(source)
    assert canon["yardsGained"]==44
    assert canon["sourceYardsGained"]==44
    assert canon["analyticsYardsGained"]==0
    assert canon["yardsGainedWasNormalized"] is True


def test_non_administrative_yards_are_preserved():
    for play_type in ("Rush","Pass Reception","Kickoff","Punt Return"):
        canon=normalize_play({"playType":play_type,"yardsGained":13})
        assert canon["sourceYardsGained"]==13
        assert canon["analyticsYardsGained"]==13
        assert canon["yardsGainedWasNormalized"] is False

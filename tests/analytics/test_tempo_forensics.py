from cfb_analytics.analytics.tempo_forensics import _bucket,_neutral,clock_seconds,wallclock_seconds


def test_clock_seconds_and_bucket_boundaries():
    assert clock_seconds({"clock":{"minutes":12,"seconds":34}})==754
    assert clock_seconds({"clock":{"minutes":16,"seconds":0}}) is None
    assert clock_seconds({"clock":None}) is None
    assert _bucket(-1)=="negative"
    assert _bucket(0)=="0"
    assert _bucket(10)=="1-10"
    assert _bucket(11)=="11-20"
    assert _bucket(60)=="41-60"
    assert _bucket(61)==">60"


def test_wallclock_and_neutral_state():
    a={"wallclock":"2026-09-01T20:15:03Z"}
    b={"wallclock":"2026-09-01T20:15:41Z"}
    assert wallclock_seconds(b)-wallclock_seconds(a)==38
    assert _neutral({"period":3,"offenseScore":21,"defenseScore":7}) is True
    assert _neutral({"period":3,"offenseScore":22,"defenseScore":7}) is False
    assert _neutral({"period":4,"offenseScore":7,"defenseScore":7}) is False

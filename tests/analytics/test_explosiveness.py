from cfb_analytics.analytics.explosiveness import classify_explosive

def play(**kw):
 p={"isScrimmagePlay":True,"isOffensivePlay":True,"hasStateTransitionModifier":False,"hasNoPlayContext":False,"analyticsYardsGained":0,"eventSubtype":"Rush"};p.update(kw);return p

def test_rush_threshold():
 assert classify_explosive(play(analyticsYardsGained=10)) is True
 assert classify_explosive(play(analyticsYardsGained=9)) is False

def test_pass_threshold():
 assert classify_explosive(play(eventSubtype="Pass Reception",analyticsYardsGained=20)) is True
 assert classify_explosive(play(eventSubtype="Pass Reception",analyticsYardsGained=19)) is False

def test_sack_is_pass_family_nonexplosive():
 assert classify_explosive(play(eventSubtype="Sack",analyticsYardsGained=-7)) is False

def test_modified_context_excluded():
 assert classify_explosive(play(analyticsYardsGained=40,hasStateTransitionModifier=True)) is None

def test_non_scrimmage_excluded():
 assert classify_explosive(play(analyticsYardsGained=40,isScrimmagePlay=False)) is None

def test_unknown_family_excluded():
 assert classify_explosive(play(eventSubtype="Unknown",analyticsYardsGained=40)) is None

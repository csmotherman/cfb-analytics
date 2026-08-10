from cfb_analytics.analytics.success import classify_success

def play(down=1,distance=10,yards=5,**kw):
 p={"isScrimmagePlay":True,"isOffensivePlay":True,"hasStateTransitionModifier":False,"hasNoPlayContext":False,"down":down,"distance":distance,"analyticsYardsGained":yards}; p.update(kw); return p

def test_first_down_half_distance_is_success():
 assert classify_success(play(1,10,5)) is True
 assert classify_success(play(1,10,4)) is False

def test_second_down_requires_seventy_percent():
 assert classify_success(play(2,10,7)) is True
 assert classify_success(play(2,10,6)) is False

def test_late_down_requires_line_to_gain():
 assert classify_success(play(3,4,4)) is True
 assert classify_success(play(3,4,3)) is False
 assert classify_success(play(4,1,1)) is True

def test_modified_context_is_excluded():
 assert classify_success(play(hasStateTransitionModifier=True)) is None

def test_invalid_state_is_excluded():
 assert classify_success(play(distance=0)) is None
 assert classify_success(play(down=None)) is None

def test_non_offensive_play_is_excluded():
 assert classify_success(play(isOffensivePlay=False)) is None

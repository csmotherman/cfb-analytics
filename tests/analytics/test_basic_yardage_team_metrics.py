from cfb_analytics.analytics.basic_yardage_team_metrics import partition_game_team_basic_yardage_metrics


def test_standard_rush_and_dropback_mirror_to_opponent():
    plays = [
        {"gameId":"g","driveId":"d1","isScrimmagePlay":True,"isOffensivePlay":True,"sourcePlayType":"Rush","eventSubtype":"RUSH","analyticsYardsGained":6,"offense":"A","defense":"B"},
        {"gameId":"g","driveId":"d1","isScrimmagePlay":True,"isOffensivePlay":True,"sourcePlayType":"Pass Completion","eventSubtype":"PASS_COMPLETION","analyticsYardsGained":14,"offense":"A","defense":"B"},
        {"gameId":"g","driveId":"d1","isScrimmagePlay":True,"isOffensivePlay":True,"sourcePlayType":"Sack","eventSubtype":"SACK","analyticsYardsGained":-5,"offense":"A","defense":"B"},
    ]
    m = partition_game_team_basic_yardage_metrics(plays, [])
    a = m[("g", "A")]
    b = m[("g", "B")]
    assert a["rushAttempts"] == b["rushAttemptsFaced"] == 1
    assert a["rushYards"] == b["rushYardsAllowed"] == 6
    assert a["dropbacks"] == b["dropbacksFaced"] == 2
    assert a["netPassYards"] == b["netPassYardsAllowed"] == 9
    assert a["basicYardagePlays"] == b["basicYardagePlaysFaced"] == 3
    assert a["basicYardageYards"] == b["basicYardageYardsAllowed"] == 15
    assert a["yardsPerPlay"] == b["yardsPerPlayAllowed"] == 5
    assert a["netPassYardsPerDropback"] == b["netPassYardsPerDropbackAllowed"] == 4.5


def test_no_play_context_is_excluded():
    plays = [{"gameId":"g","driveId":"d","isScrimmagePlay":True,"isOffensivePlay":True,"sourcePlayType":"Rush","eventSubtype":"RUSH","analyticsYardsGained":20,"offense":"A","defense":"B","hasNoPlayContext":True}]
    assert partition_game_team_basic_yardage_metrics(plays, []) == {}

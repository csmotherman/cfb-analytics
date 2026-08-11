from cfb_analytics.analytics.havoc import corpus_havoc_audit

def test_tfl_and_sack_count_once_each():
 plays=[
  {"gameId":"g","isScrimmagePlay":True,"eventCategory":"SCRIMMAGE","sourcePlayType":"Rush","analyticsYardsGained":-4,"offense":"A","defense":"B","period":1,"clock":{"minutes":10,"seconds":0}},
  {"gameId":"g","isScrimmagePlay":True,"eventCategory":"SCRIMMAGE","sourcePlayType":"Sack","eventSubtype":"SACK","analyticsYardsGained":-7,"offense":"A","defense":"B","period":1,"clock":{"minutes":9,"seconds":0}},
 ]
 r=corpus_havoc_audit(plays,[])
 assert r["eligible_plays"]==2
 assert r["tfls"]==1
 assert r["sacks"]==1
 assert r["havoc_plays"]==2
 assert r["havoc_rate"]==1

def test_positive_rush_is_eligible_but_not_havoc():
 p={"gameId":"g","isScrimmagePlay":True,"eventCategory":"SCRIMMAGE","sourcePlayType":"Rush","analyticsYardsGained":4,"offense":"A","defense":"B"}
 r=corpus_havoc_audit([p],[])
 assert r["eligible_plays"]==1 and r["havoc_plays"]==0

def test_modified_play_excluded_from_denominator():
 p={"gameId":"g","isScrimmagePlay":True,"eventCategory":"SCRIMMAGE","sourcePlayType":"Rush","analyticsYardsGained":-2,"hasNoPlayContext":True}
 r=corpus_havoc_audit([p],[])
 assert r["eligible_plays"]==0

from cfb_analytics.analytics.epa_v1_research import next_score_examples,play_epa_v2

def s(i,off="A",a=0,b=0,p=1):
 os,ds=(a,b) if off=="A" else (b,a)
 return {"gameId":"g","driveNumber":1,"playNumber":i,"id":str(i),"offense":off,"defense":"B" if off=="A" else "A","home":"A","away":"B","offenseScore":os,"defenseScore":ds,"period":p,"clock":{"minutes":10,"seconds":0},"down":1,"distance":10,"yardsToGoal":75,"isScrimmagePlay":True,"isOffensivePlay":True,"hasNoPlayContext":False,"ppa":0.0}

def test_next_score_offense_and_opponent():
 x={p["id"]:v for p,v in next_score_examples([s(1),s(2,a=7)])}
 assert x["1"]==7 and x["2"]==7
 x={p["id"]:v for p,v in next_score_examples([s(1),s(2,off="B"),s(3,off="B",b=3)])}
 assert x["1"]==-3

def test_next_score_stops_at_half():
 x={p["id"]:v for p,v in next_score_examples([s(1,p=2),s(2,a=7,p=3)])}
 assert x["1"]==0

def test_entering_score_is_current_play_points():
 prev,cur,nxt=s(1),s(2,a=7),s(3,off="B",a=7)
 class M:
  def predict(self,p): return {"2":1.0,"3":0.5}[p["id"]]
 assert play_epa_v2(prev,cur,nxt,M())==5.5

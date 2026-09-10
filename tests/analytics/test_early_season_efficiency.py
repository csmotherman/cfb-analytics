import pytest

from cfb_analytics.analytics.early_season_efficiency import (
    METRICS, build_rankings, epa_family, game_counts, guarded_epa, rank_values,
)


def play(i, team='A', score=0, period=1, subtype='RUSH', **kw):
    return dict(gameId='1', driveId='d', driveNumber=1, playNumber=i,
        id=str(i), offense=team, defense='B' if team == 'A' else 'A',
        home='A', away='B', offenseScore=score, defenseScore=0,
        down=1, distance=10, yardsToGoal=75, clock={'minutes':10,'seconds':i},
        period=period, eventSubtype=subtype, isScrimmagePlay=True,
        isOffensivePlay=True, analyticsYardsGained=5, **kw)


class Model:
    def predict(self, p):
        return 2.0 if p['offense'] == 'A' else 1.0


def test_defensive_direction_and_exact_ties():
    ranked = rank_values({'A':-.2, 'B':.3, 'C':-.2, 'D':None}, higher=False)
    assert ranked['A']['rank'] == ranked['C']['rank'] == 1
    assert ranked['B']['rank'] == 3
    assert ranked['A']['percentile'] == 75
    assert ranked['D']['value'] is None


def test_epa_terminal_half_and_turnover_orientation():
    value, reason = guarded_epa(play(1),play(2),play(3,period=3),Model())
    assert reason is None and value == -2
    assert guarded_epa(play(1),play(2),None,Model())[0] == -2
    assert guarded_epa(play(1),play(2,subtype='INTERCEPTION'),play(3,team='B'),Model())[0] == -3


def test_epa_scoring_guard_and_scoring_play():
    assert guarded_epa(play(1,score=7),play(2,score=6),play(3),Model())[1] == 'conflicting_score_state'
    assert guarded_epa(play(1),play(2,score=7),play(3),Model())[1] == 'score_change_on_non_scoring_play'
    assert guarded_epa(play(1),play(2,score=7,subtype='RUSH_TD'),None,Model())[0] == 5


def test_pass_cohort_includes_sacks_and_return_interceptions():
    assert epa_family(play(1,subtype='SACK')) == 'pass'
    assert epa_family(play(1,subtype='INTERCEPTION_RETURN_TD')) == 'pass'
    assert epa_family(play(1,subtype='FUMBLE_RECOVERY_OPPONENT',playText='pass complete, fumbled')) == 'pass'
    assert epa_family(play(1,subtype='FUMBLE_RECOVERY_OWN',playText='recovered by A')) is None
    assert epa_family(play(1,subtype='SACK',hasNoPlayContext=True)) is None


def test_ppa_never_changes_epa_and_mirrors_match():
    games=[dict(id=1,homeTeam='A',awayTeam='B')]
    plays=[play(1,ppa=999),play(2),play(3,team='B')]
    rows, events, _ = game_counts(games, plays, Model(), set())
    plays[0]['ppa'] = -999
    again = game_counts(games, plays, Model(), set())
    assert events == again[1]
    assert rows[0]['offense'] == rows[1]['defense']


def test_duplicate_state_excluded_from_epa():
    a, b = play(1),play(2)
    b['clock'] = a['clock']
    rows, events, exclusions = game_counts([dict(id=1,homeTeam='A',awayTeam='B')],[a,b],Model(),set())
    assert not events
    assert exclusions == {'duplicate_or_disputed_start_state':2}
    assert rows[0]['offense']['successEligible'] == 2  # locked SR unaffected


def test_pooled_rates_fcs_and_quarantined_epa():
    games=[dict(id=1,homeTeam='A',awayTeam='B',homeClassification='fbs',awayClassification='fcs'),
           dict(id=2,homeTeam='A',awayTeam='C',homeClassification='fbs',awayClassification='fbs')]
    def counts(n,d):
        return {k:v for num,den in METRICS.values() for k,v in [(num,n),(den,d)]}
    rows=[dict(gameId='1',team='A',opponent='B',offense=counts(1,1),defense=counts(0,1),playDataAvailable=True,epaQuarantined=False),
          dict(gameId='2',team='A',opponent='C',offense=counts(0,9),defense=counts(1,9),playDataAvailable=True,epaQuarantined=True),
          dict(gameId='2',team='C',opponent='A',offense=counts(1,9),defense=counts(0,9),playDataAvailable=True,epaQuarantined=True)]
    rankings={r['team']:r for r in build_rankings(games,rows)}
    assert set(rankings) == {'A','C'}
    assert rankings['A']['metrics']['success']['offense']['value'] == pytest.approx(.1)
    assert rankings['A']['metrics']['epa']['offense']['value'] is None
    assert rankings['A']['composite']['overall']['rank'] is None
    assert rankings['A']['process']['overall']['rank'] is not None


def test_composite_weights_and_equal_defense():
    games = [dict(id=i,homeTeam=t,awayTeam='FCS',homeClassification='fbs',awayClassification='fcs')
             for i,t in enumerate(('A','B','C'),1)]
    rows = []
    for i,(t,sr,ex,epa) in enumerate([('A',9,1,3),('B',5,5,2),('C',1,9,1)],1):
        counts=dict(successful=sr,successEligible=10,explosive=ex,explosiveEligible=10,epaTotal=epa,epaPlays=10)
        allowed=dict(successful=5,successEligible=10,explosive=5,explosiveEligible=10,epaTotal=2,epaPlays=10)
        rows.append(dict(gameId=str(i),team=t,opponent='FCS',offense=counts,defense=allowed,
                         playDataAvailable=True,epaQuarantined=False))
    rankings={r['team']:r for r in build_rankings(games,rows)}
    assert rankings['A']['composite']['offense']['value'] == 75
    assert rankings['A']['composite']['defense']['value'] == 50
    assert rankings['A']['composite']['overall']['value'] == 62.5
    assert {r['process']['overall']['rank'] for r in rankings.values()} == {1}

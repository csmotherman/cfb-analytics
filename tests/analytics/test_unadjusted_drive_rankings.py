from cfb_analytics.analytics.unadjusted_drive_rankings import aggregate_rankings


def game(gid, home, away, away_class='fbs'):
    return dict(id=gid, homeTeam=home, awayTeam=away,
                homeClassification='fbs', awayClassification=away_class)


def row(gid, team, points, drives):
    return dict(gameId=str(gid), team=team, offensiveDrivePoints=points,
                resolvedPointPossessions=drives, unresolvedPointPossessions=0)


def test_pool_drives_include_fcs_and_reverse_defense_direction():
    games = [game(1, 'A', 'B'), game(2, 'A', 'FCS', 'fcs')]
    rows = [row(1, 'A', 7, 1), row(1, 'B', 3, 2),
            row(2, 'A', 0, 9), row(2, 'FCS', 0, 8)]
    result = {r['team']: r for r in aggregate_rankings(games, rows)}
    assert set(result) == {'A', 'B'}
    assert result['A']['offensePPD'] == .7
    assert result['A']['defensePPDAllowed'] == .3
    assert result['A']['netPPD'] == .4
    assert result['A']['offenseRank'] == 2
    assert result['A']['defenseRank'] == 1
    assert result['A']['fcsGames'] == 1


def test_exact_ties_and_missing_games():
    games = [game(1, 'A', 'B'), game(2, 'C', 'D')]
    rows = [row(1, 'A', 7, 3), row(1, 'B', 14, 6), row(2, 'C', 7, 3)]
    result = {r['team']: r for r in aggregate_rankings(games, rows)}
    assert result['A']['offenseRank'] == result['B']['offenseRank'] == 1
    assert result['A']['netPPD'] == result['B']['netPPD'] == 0
    assert result['C']['netRank'] is None
    assert result['D']['missingGames'] == ['2']

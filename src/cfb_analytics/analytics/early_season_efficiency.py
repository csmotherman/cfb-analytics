"""Unadjusted success, explosiveness and independently modeled EPA rankings."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from cfb_analytics.analytics.epa_v1_research import (
    EPA_V2_RESEARCH_VERSION, NextScoreExpectedPoints, _game_groups,
    half_number, oriented_score, state_eligible,
)
from cfb_analytics.derived.games import _metric_counts

VERSION = 'early-season-efficiency-v1'
EPA_COHORT_VERSION = 'epa-v2-ranking-transitions-v1'
TRAIN_SEASONS = (2021, 2022, 2023, 2024, 2025)
WEIGHTS = {'success': .50, 'explosive': .25, 'epa': .25}
METRICS = {
    'success': ('successful', 'successEligible'),
    'passSuccess': ('passSuccessful', 'passSuccessEligible'),
    'rushSuccess': ('rushSuccessful', 'rushSuccessEligible'),
    'explosive': ('explosive', 'explosiveEligible'),
    'passExplosive': ('passExplosive', 'passExplosiveEligible'),
    'rushExplosive': ('rushExplosive', 'rushExplosiveEligible'),
    'epa': ('epaTotal', 'epaPlays'),
    'passEpa': ('passEpaTotal', 'passEpaPlays'),
    'rushEpa': ('rushEpaTotal', 'rushEpaPlays'),
}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def train_model(root, cache, season):
    if max(TRAIN_SEASONS) >= season:
        raise ValueError('EPA training must precede the ranking season')
    paths = [p for year in TRAIN_SEASONS for p in sorted((root / 'canonical' / f'season={year}').glob('**/plays.json'))]
    if any(not any(f'season={year}' in p.parts for p in paths) for year in TRAIN_SEASONS):
        raise ValueError('Missing EPA training season')
    sources = [dict(path=str(p), sha256=digest(p)) for p in paths]
    signature = hashlib.sha256(json.dumps(dict(sources=sources, minCount=50, trainingSeasons=TRAIN_SEASONS), sort_keys=True).encode() +
        Path(__import__('cfb_analytics.analytics.epa_v1_research', fromlist=['x']).__file__).read_bytes()).hexdigest()
    model = NextScoreExpectedPoints(min_count=50)
    if cache.exists():
        saved = json.loads(cache.read_text())
        if saved['fingerprint'] == signature:
            model.stats.update({tuple(k): v for k, v in saved['stats']})
            print('EPA model cache reused', flush=True)
            return model, saved
    for i, path in enumerate(paths, 1):
        model.fit(json.loads(path.read_text()))
        if i % 8 == 0 or i == len(paths):
            print(f'EPA training: {i}/{len(paths)} partitions', flush=True)
    saved = dict(version=EPA_V2_RESEARCH_VERSION, trainingSeasons=TRAIN_SEASONS,
        minCount=model.min_count, fingerprint=signature, sources=sources,
        trainingStates=model.stats[('global',)][0], stats=[[list(k), v] for k, v in sorted(model.stats.items())])
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(saved) + '\n')
    return model, saved


def epa_family(play):
    """Source-record EPA cohort; does not change locked rush/dropback counts."""
    if play.get('hasNoPlayContext') or play.get('isNoPlay'):
        return None
    subtype = play.get('eventSubtype', '')
    if subtype in {'PASS_COMPLETION', 'PASS_INCOMPLETE', 'PASS_TD', 'SACK',
                   'INTERCEPTION', 'INTERCEPTION_RETURN', 'INTERCEPTION_RETURN_TD'}:
        return 'pass'
    if subtype in {'RUSH', 'RUSH_TD'}:
        return 'rush'
    if subtype in {'FUMBLE', 'FUMBLE_RECOVERY_OWN', 'FUMBLE_RECOVERY_OPPONENT', 'FUMBLE_RETURN_TD'}:
        text = str(play.get('playText') or '').lower()
        if re.search(r'\b(pass|sacked|sack)\b', text):
            return 'pass'
        if re.search(r'\b(rush|run)\b', text):
            return 'rush'
    return None


def guarded_epa(previous, play, following, model):
    """EPA-v2 EP surface with explicit terminal-half and score-quality handling."""
    if not state_eligible(play):
        return None, 'invalid_state'
    score = oriented_score(play)
    prior = oriented_score(previous) if previous is not None else None
    sub = play.get('eventSubtype', '')
    scoring = play.get('scoring') is True or sub.endswith('_TD') or sub == 'SAFETY'
    points = 0.0
    if prior is None:
        if scoring:
            return None, 'missing_before_score'
    else:
        delta = [a-b for a, b in zip(score, prior)]
        if any(d < 0 for d in delta) or sum(delta) > 8 or all(d > 0 for d in delta):
            return None, 'conflicting_score_state'
        if not scoring and any(delta):
            return None, 'score_change_on_non_scoring_play'
        points = delta[0]-delta[1] if play['offense'] == play['home'] else delta[1]-delta[0]
        if sub in {'RUSH_TD', 'PASS_TD'} and points not in (6, 7, 8):
            return None, 'unresolved_touchdown_points'
        if sub in {'INTERCEPTION_RETURN_TD', 'FUMBLE_RETURN_TD'} and points not in (-6, -7, -8):
            return None, 'unresolved_return_touchdown_points'
    ep_before = model.predict(play)
    if ep_before is None:
        return None, 'missing_model_state'
    if following is None or half_number(following) != half_number(play):
        ep_after = 0.0
    else:
        ep_after = model.predict(following)
        if ep_after is None:
            return None, 'missing_next_state'
        if following['offense'] != play['offense']:
            ep_after = -ep_after
    value = points + ep_after - ep_before
    return (value, None) if math.isfinite(value) else (None, 'nonfinite_epa')


def game_counts(games, plays, model, quarantined):
    """Keep both teams for exact offensive/defensive reconciliation, including FCS."""
    groups = _game_groups(plays)
    result, events, exclusions = [], [], Counter()
    for game in games:
        gid = str(game['id'])
        rows = groups.get(gid, [])
        teams = (game['homeTeam'], game['awayTeam'])
        counts = {team: _metric_counts([p for p in rows if p.get('offense') == team and p.get('defense') in teams]) for team in teams}
        candidate_states = defaultdict(list)
        for p in rows:
            if epa_family(p):
                key = (p.get('driveId'), p.get('offense'), p.get('period'),
                    json.dumps(p.get('clock'), sort_keys=True), p.get('down'), p.get('distance'), p.get('yardsToGoal'))
                candidate_states[key].append(p)
        ambiguous_ids = {id(p) for group in candidate_states.values() if len(group) > 1 for p in group}
        states = [p for p in rows if state_eligible(p)]
        indices = {id(p): i for i, p in enumerate(states)}
        for position, play in enumerate(rows):
            family = epa_family(play)
            if not family:
                continue
            team = play.get('offense')
            if team not in teams or play.get('defense') not in teams or team == play.get('defense'):
                raise ValueError(f'Unexpected team identity: {gid}, {play.get("id")}')
            counts[team]['epaCandidates'] += 1
            counts[team][family + 'EpaCandidates'] += 1
            i = indices.get(id(play))
            reason = None
            value = None
            if gid in quarantined:
                reason = 'quarantined_game_scoring_conflict'
            elif id(play) in ambiguous_ids:
                reason = 'duplicate_or_disputed_start_state'
            elif i is None:
                reason = 'invalid_state_or_overtime'
            else:
                previous = rows[position-1] if position else None
                following = states[i+1] if i+1 < len(states) else None
                value, reason = guarded_epa(previous, play, following, model)
            if value is None:
                exclusions[reason] += 1
                counts[team]['epaExcluded'] += 1
                continue
            counts[team]['epaTotal'] += value
            counts[team]['epaPlays'] += 1
            counts[team][family + 'EpaTotal'] += value
            counts[team][family + 'EpaPlays'] += 1
            events.append(dict(gameId=gid, playId=play['id'], offense=team,
                defense=play['defense'], family=family, epa=value, subtype=play['eventSubtype']))
        for team, opponent in (teams, teams[::-1]):
            result.append(dict(gameId=gid, team=team, opponent=opponent,
                offense=dict(counts[team]), defense=dict(counts[opponent]),
                playDataAvailable=bool(rows), epaQuarantined=gid in quarantined))
    return result, events, dict(exclusions)


def rank_values(values, higher=True, exact=False):
    """Exact ties receive shared competition ranks and average-rank percentiles."""
    ordered = sorted([v for v in values.values() if v is not None], reverse=higher)
    n = len(ordered)
    out = {}
    for team, value in values.items():
        if value is None:
            out[team] = dict(value=None, rank=None, percentile=None, cohort=n)
            continue
        first = ordered.index(value)
        tied = ordered.count(value)
        percentile = Fraction(50) if n == 1 else 100 * (1 - Fraction(2*first+tied-1, 2*(n-1)))
        out[team] = dict(value=value if exact else float(value), rank=first+1,
                        percentile=percentile if exact else float(percentile), cohort=n)
    return out


def build_rankings(games, rows):
    fbs = {g[side+'Team'] for g in games for side in ('home', 'away') if g.get(side+'Classification') == 'fbs'}
    totals = {t: {'offense': Counter(), 'defense': Counter(), 'games': [], 'epaQuarantined': False, 'missingGames': []} for t in fbs}
    for row in rows:
        if row['team'] not in fbs:
            continue
        t = totals[row['team']]
        t['games'].append(row['gameId'])
        if not row['playDataAvailable']:
            t['missingGames'].append(row['gameId'])
        t['epaQuarantined'] |= row['epaQuarantined']
        for side in ('offense', 'defense'):
            t[side].update(row[side])
    rankings = {t: dict(team=t, games=len(v['games']), gameIds=v['games'],
        missingGames=v['missingGames'], epaQuarantined=v['epaQuarantined'],
        counts={s: dict(v[s]) for s in ('offense', 'defense')}, metrics={}) for t, v in totals.items()}
    for metric, (numerator, denominator) in METRICS.items():
        rates = {}
        for side in ('offense', 'defense'):
            rates[side] = {}
            for team, t in totals.items():
                c = t[side]
                eligible = c[denominator] and not t['missingGames'] and not ('epa' in metric.lower() and t['epaQuarantined'])
                rates[side][team] = Fraction(c[numerator]) / c[denominator] if eligible else None
        rates['net'] = {t: rates['offense'][t]-rates['defense'][t] if rates['offense'][t] is not None and rates['defense'][t] is not None else None for t in totals}
        for side in ('offense', 'defense', 'net'):
            ranked = rank_values(rates[side], higher=side != 'defense')
            for team in totals:
                rankings[team]['metrics'].setdefault(metric, {})[side] = ranked[team]
    # Composite percentiles use the SAME complete-case cohort for every component.
    # This avoids shifting SR/explosiveness reference groups because EPA has gaps.
    for name, weights in [('process', {'success': .5, 'explosive': .5}), ('composite', WEIGHTS)]:
        complete = {t for t in rankings if all(rankings[t]['metrics'][m][s]['value'] is not None for m in weights for s in ('offense', 'defense'))}
        score_by_side = {}
        for side in ('offense', 'defense'):
            component = {m: rank_values({t: Fraction(totals[t][side][METRICS[m][0]]) / totals[t][side][METRICS[m][1]] for t in complete}, higher=side == 'offense', exact=True) for m in weights}
            score_by_side[side] = {t: sum(Fraction(str(weights[m]))*component[m][t]['percentile'] for m in weights) if t in complete else None for t in rankings}
        score_by_side['overall'] = {t: (score_by_side['offense'][t]+score_by_side['defense'][t])/2 if t in complete else None for t in rankings}
        for side, values in score_by_side.items():
            ranked = rank_values(values)
            for team in rankings:
                rankings[team].setdefault(name, {})[side] = ranked[team]
    return sorted(rankings.values(), key=lambda r: (r['composite']['overall']['rank'] or 9999, r['team']))


def audit(games, rows, events, rankings):
    lookup = {(r['gameId'], r['team']): r for r in rows}
    checks = {
        'unique_team_games': len(lookup) == len(rows) == 2*len(games),
        'unique_epa_plays': len({(r['gameId'], r['playId']) for r in events}) == len(events),
        'all_games_have_play_data': all(r['playDataAvailable'] for r in rows),
        'offense_defense_mirrors': all(r['offense'] == lookup[(r['gameId'], r['opponent'])]['defense'] for r in rows),
        'epa_pass_rush_denominators': all(r[s].get('epaPlays', 0) == r[s].get('passEpaPlays', 0)+r[s].get('rushEpaPlays', 0) for r in rows for s in ('offense', 'defense')),
        'epa_pass_rush_totals': all(math.isclose(r[s].get('epaTotal', 0), r[s].get('passEpaTotal', 0)+r[s].get('rushEpaTotal', 0), abs_tol=1e-9) for r in rows for s in ('offense', 'defense')),
        'epa_coverage_reconciles': all(r[s].get('epaCandidates', 0) == r[s].get('epaPlays', 0)+r[s].get('epaExcluded', 0) for r in rows for s in ('offense', 'defense')),
    }
    for team in rankings:
        source = [r for r in rows if r['team'] == team['team']]
        for side in ('offense', 'defense'):
            summed = Counter()
            for row in source:
                summed.update(row[side])
            assert dict(summed) == team['counts'][side]
    checks['season_counts_reconcile'] = True
    if not all(checks.values()):
        raise ValueError(checks)
    return checks


def table(rows, columns):
    lines = ['| ' + ' | '.join(label for label, _ in columns) + ' |',
             '| ' + ' | '.join('---' for _ in columns) + ' |']
    for row in rows:
        lines.append('| ' + ' | '.join(str(fn(row)) for _, fn in columns) + ' |')
    return lines


def report(artifact, output):
    rankings = artifact['rankings']
    def fmt(value, percentage=False):
        return '—' if value is None else f'{value:.1%}' if percentage else f'{value:+.3f}'
    def metric_fmt(value, metric, side):
        if value is not None and 'epa' not in metric.lower() and side == 'net':
            return f'{100*value:+.1f} pp'
        return fmt(value, 'epa' not in metric.lower())
    lines = ['# SOAR Analytics — 2026 early-season efficiency rankings', '',
        f'As of {artifact["asOf"]}. All {len(artifact["completedGames"])} completed FBS-involving games in the September 8 snapshot are represented, including FCS opponents. No opponent adjustment, preseason priors, or additional garbage-time filter.', '',
        '**Overall efficiency:** 50% success-rate percentile + 25% explosive-play-rate percentile + 25% EPA/play percentile on each side; overall is the average of offense and defense scores. Higher composite scores are better. Defense percentiles reward lower opponent rates. Components share the same eligible cohort. The weights are an explicit research choice, not a fitted or validated power model. Total points and scoring volume are not components.', '',
        '**Process-only ranking:** equal-weight success and explosive-play percentiles, averaging offense and defense. This companion ranking covers teams whose EPA is unavailable and shows performance without any point-value input.', '',
        '**Metric definitions:** success requires 50% of yards needed on first down, 70% on second, and 100% on third/fourth. Explosive plays gain 10+ rushing yards or 20+ passing yards. These reuse the locked repository classifiers. EPA is independently modeled expected points added using SOAR’s research EP-v2 surface trained on 2021–2025, never on 2026 outcomes or CFBD PPA. EPA passing includes sacks and interceptions; rushing includes source-labeled quarterback runs. EPA uses its own documented source-record cohort, including identifiable fumble plays. It is not the locked dropback denominator.', '',
        '**Reading the tables:** offensive EPA is value gained; defensive EPA allowed is opponent value gained (lower/negative is better); net subtracts defense allowed from offense. Rates pool play totals rather than averaging game rates. Exact metric ties share competition rank. Display rounding can make unequal values look tied. Scores on a 0–100 scale are weighted percentile scores, not win probabilities.', '',
        '**EPA limitations:** regulation only; half-ending future EP is zero. Invalid state, conflicting scoring transitions, ambiguous scoring outcomes, and duplicate/disputed start states are excluded and counted. Source scoring conflicts in UAB–Illinois and Ole Miss–Louisville keep those four teams unranked for EPA and the EPA-inclusive composite. Their success, explosiveness, and process-only rankings remain available. No values are fabricated or manually corrected. Source-only unclassified fumble/recovery events are not assigned to passing or rushing. No film-based scramble or designed-run inference is made. The extended EPA cohort and transition guards are new research behavior; historical benchmark results for the original EPA-v2 cohort do not validate these rankings.', '',
        f'Coverage: {len(rankings)} FBS teams; {sum(r["composite"]["overall"]["rank"] is not None for r in rankings)} EPA-inclusive composite rankings; {len(artifact["epaPlays"]):,} EPA-scored plays across both FBS and FCS offenses. EPA exclusions: `{json.dumps(artifact["epaExclusions"], sort_keys=True)}`. Per-team EPA coverage and raw numerators/denominators are in rankings.json.', '',
        '## Overall efficiency rankings', '']
    lines += table(rankings, [('Rank', lambda r:r['composite']['overall']['rank'] or '—'), ('Team', lambda r:r['team']),
        ('Score', lambda r:fmt(r['composite']['overall']['value'])),
        ('Off. rank',lambda r:r['composite']['offense']['rank'] or '—'), ('Def. rank',lambda r:r['composite']['defense']['rank'] or '—'),
        ('Process-only rank',lambda r:r['process']['overall']['rank'] or '—'),
        ('Net success',lambda r:metric_fmt(r['metrics']['success']['net']['value'],'success','net')),
        ('Net explosive',lambda r:metric_fmt(r['metrics']['explosive']['net']['value'],'explosive','net')),
        ('Net EPA/play',lambda r:fmt(r['metrics']['epa']['net']['value']))])
    lines += ['', '## EPA per play, pass, and rush', '', 'All teams, sorted by net EPA/play. Each cell shows value (rank). Defense columns report EPA allowed.', '']
    columns = [('Team', lambda r:r['team'])]
    for metric, label in [('epa','EPA/play'),('passEpa','EPA/pass'),('rushEpa','EPA/rush')]:
        for side in ('offense','defense','net'):
            columns.append((f'{side.title()} {label}', lambda r,m=metric,s=side: f'{fmt(r["metrics"][m][s]["value"])} ({r["metrics"][m][s]["rank"] or "—"})'))
    lines += table(sorted(rankings,key=lambda r:(r['metrics']['epa']['net']['rank'] or 9999,r['team'])),columns)
    for metric in METRICS:
        metric_lines = [f'# {metric} — unadjusted 2026 rankings', '', 'Defense is opponent production allowed; lower is better. Net = offense minus defense.', '']
        for side in ('offense','defense','net'):
            metric_lines += [f'## {side.title()}', '']
            metric_lines += table(sorted(rankings,key=lambda r:(r['metrics'][metric][side]['rank'] or 9999,r['team'])),
                [('Rank',lambda r,m=metric,s=side:r['metrics'][m][s]['rank'] or '—'), ('Team',lambda r:r['team']),
                 ('Value',lambda r,m=metric,s=side:metric_fmt(r['metrics'][m][s]['value'],m,s)),
                 ('Off. plays',lambda r,m=metric:r['counts']['offense'].get(METRICS[m][1],0)),
                 ('Def. plays',lambda r,m=metric:r['counts']['defense'].get(METRICS[m][1],0))])
            metric_lines.append('')
        (output/f'{metric}.md').write_text('\n'.join(metric_lines))
    lines += ['', '## Individual metric tables', ''] + [f'- [{m}]({m}.md): separate offense, defense and net leaderboards.' for m in METRICS]
    lines += ['- [Process-only rankings](process.md): overall, offense and defense without EPA.',
              '- [Composite rankings](composite.md): overall, offense and defense with EPA.',
              '- [EPA coverage](coverage.md): eligible/scored plays and exclusions for every team.']
    lines += ['', '## Validation', '', f'All {len(artifact["checks"])} artifact checks passed. Model training: {artifact["model"]["trainingStates"]:,} historical states; {artifact["model"]["minCount"]}-observation minimum before hierarchical fallback. Full provenance, game totals, play EPA, coverage and audit results are preserved in rankings.json. Methodology: docs/EARLY_SEASON_EFFICIENCY.md.', '']
    (output/'report.md').write_text('\n'.join(lines))
    coverage_columns = [('Team', lambda r:r['team'])]
    for side in ('offense','defense'):
        coverage_columns += [(f'{side} EPA plays',lambda r,s=side:r['counts'][s].get('epaPlays',0)),
            (f'{side} candidates',lambda r,s=side:r['counts'][s].get('epaCandidates',0)),
            (f'{side} coverage',lambda r,s=side:fmt(r['counts'][s].get('epaPlays',0)/r['counts'][s]['epaCandidates'] if r['counts'][s].get('epaCandidates') else None,True))]
    (output/'coverage.md').write_text('\n'.join(['# EPA coverage', '',
        'Candidates are source-identifiable rush/pass plays, including sacks and turnovers; candidates outside regulation or with unusable states remain in the coverage denominator. Coverage is not completeness versus official box-score attempts. Quarantined games receive zero scored EPA plays.', ''] +
        table(sorted(rankings,key=lambda r:r['team']),coverage_columns))+'\n')
    for name in ('process','composite'):
        sections = [f'# {name.title()} rankings — 2026', '']
        for side in ('overall','offense','defense'):
            sections += [f'## {side.title()}', ''] + table(sorted(rankings,key=lambda r:(r[name][side]['rank'] or 9999,r['team'])),
                [('Rank',lambda r,n=name,s=side:r[n][s]['rank'] or '—'), ('Team',lambda r:r['team']),
                 ('Score',lambda r,n=name,s=side:fmt(r[n][s]['value']))]) + ['']
        (output/f'{name}.md').write_text('\n'.join(sections))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train-only', action='store_true')
    args = parser.parse_args()
    output = Path('data/research/early_season_efficiency/2026')
    model, metadata = train_model(Path('data/processed'), output/'epa_model.json', 2026)
    if args.train_only:
        return
    previous_path = Path('data/research/unadjusted_drive_rankings/2026/rankings.json')
    previous = json.loads(previous_path.read_text())
    games = previous['completedGames']
    play_path = Path('data/processed/unadjusted_drive_rankings_2026_20260908/canonical/season=2026/season_type=regular/week=01/plays.json')
    plays = json.loads(play_path.read_text())
    quarantined = {r['gameId'] for r in previous['coverage']['scoringConflicts']}
    rows, events, exclusions = game_counts(games, plays, model, quarantined)
    rankings = build_rankings(games, rows)
    checks = audit(games, rows, events, rankings)
    artifact = dict(version=VERSION, epaCohortVersion=EPA_COHORT_VERSION,
        asOf=previous['asOf'], generatedAtUtc=datetime.now(timezone.utc).isoformat(),
        weights=WEIGHTS, model={k:v for k,v in metadata.items() if k != 'stats'},
        sources=[dict(path=str(p), sha256=digest(p)) for p in (previous_path,play_path)],
        completedGames=games, rankings=rankings, teamGames=rows, epaPlays=events,
        epaExclusions=exclusions, checks=checks)
    (output/'rankings.json').write_text(json.dumps(artifact,indent=2)+'\n')
    report(artifact,output)
    print(json.dumps(dict(teams=len(rankings), epaPlays=len(events), exclusions=exclusions, checks=checks),indent=2))


if __name__ == '__main__':
    main()

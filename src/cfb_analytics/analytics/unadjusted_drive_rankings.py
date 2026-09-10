"""Descriptive FBS rankings using locked possession points, including FCS games."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from cfb_analytics.analytics.drive_ppd import build_team_game_drive_rows
from cfb_analytics.canonical.materialize import materialize_partition, canonical_partition_dir
from cfb_analytics.derived.drives import materialize_drive_partition, derived_drive_partition_dir
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.raw.storage import partition_dir, verify_manifest

VERSION = "unadjusted-drive-rankings-v1"


def aggregate_rankings(games, drive_rows):
    """Pool numerators/denominators; retain missing games as explicit coverage gaps."""
    lookup = {(str(r['gameId']), r['team']): r for r in drive_rows}
    if len(lookup) != len(drive_rows):
        raise ValueError('Duplicate team-game drive rows')
    teams = defaultdict(lambda: dict(gamesPlayed=0, gamesIncluded=0, fcsGames=0,
        offensivePoints=0, defensivePointsAllowed=0, offensiveDrives=0,
        defensiveDrives=0, offensiveUnresolved=0, defensiveUnresolved=0, missingGames=[]))
    for g in games:
        gid = str(g['id'])
        for side, other in [('home', 'away'), ('away', 'home')]:
            if g.get(side + 'Classification') != 'fbs':
                continue
            team, opponent = g[side + 'Team'], g[other + 'Team']
            t = teams[team]
            t['gamesPlayed'] += 1
            t['fcsGames'] += g.get(other + 'Classification') == 'fcs'
            own, allowed = lookup.get((gid, team)), lookup.get((gid, opponent))
            if not own or not allowed or not own['resolvedPointPossessions'] or not allowed['resolvedPointPossessions']:
                t['missingGames'].append(gid)
                continue
            t['gamesIncluded'] += 1
            for prefix, row in [('offensive', own), ('defensive', allowed)]:
                t[prefix + 'Drives'] += row['resolvedPointPossessions']
                t[prefix + 'Unresolved'] += row['unresolvedPointPossessions']
                t['offensivePoints' if prefix == 'offensive' else 'defensivePointsAllowed'] += row['offensiveDrivePoints']
    results, exact = [], {}
    for team, t in sorted(teams.items()):
        eligible = not t['missingGames'] and t['gamesIncluded'] > 0
        off = Fraction(t['offensivePoints']) / t['offensiveDrives'] if eligible else None
        deff = Fraction(t['defensivePointsAllowed']) / t['defensiveDrives'] if eligible else None
        exact[team] = (off, deff, off - deff if eligible else None)
        results.append(dict(team=team, **t, offensePPD=float(off) if eligible else None,
            defensePPDAllowed=float(deff) if eligible else None,
            netPPD=float(off-deff) if eligible else None))
    for index, field, descending in [(0, 'offenseRank', True), (1, 'defenseRank', False), (2, 'netRank', True)]:
        values = sorted([v[index] for v in exact.values() if v[index] is not None], reverse=descending)
        ranks = {}
        for position, value in enumerate(values, 1):
            ranks.setdefault(value, position)
        for row in results:
            row[field] = ranks.get(exact[row['team']][index])
    return sorted(results, key=lambda r: (r['netRank'] or 9999, r['team']))


def run(raw_root, processed_root, output, season, as_of):
    games, rows, sources, review = [], [], [], []
    for st, week in discover_partitions(raw_root, season):
        directory = partition_dir(raw_root, season, st, week)
        for entity in ('games', 'plays', 'drives'):
            if not verify_manifest(directory, entity):
                raise ValueError(f'Unverified raw evidence: {directory}/{entity}')
            path = directory / f'{entity}.json'
            sources.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                manifest=json.loads((directory / f'{entity}.manifest.json').read_text())))
        completed = [g for g in json.loads((directory / 'games.json').read_text())
            if g.get('completed') is True and g['startDate'][:10] <= as_of
            and g['season'] == season and 'fbs' in (g.get('homeClassification'), g.get('awayClassification'))]
        ids = {str(g['id']) for g in completed}
        games.extend(completed)
        materialize_partition(raw_root, processed_root, season, st, week)
        materialize_drive_partition(processed_root, season, st, week)
        plays = [p for p in json.loads((canonical_partition_dir(processed_root, season, st, week) / 'plays.json').read_text()) if str(p['gameId']) in ids]
        drives = [d for d in json.loads((derived_drive_partition_dir(processed_root, season, st, week) / 'drives.json').read_text()) if str(d['gameId']) in ids]
        review.extend(d for d in drives if d['driveValidationStatus'] != 'PASS')
        rows.extend(build_team_game_drive_rows(drives, plays))
    if len({str(g['id']) for g in games}) != len(games):
        raise ValueError('Duplicate completed games')
    lookup = {(str(r['gameId']), r['team']): r for r in rows}
    scoring_issues = []
    for game in games:
        for side in ('home', 'away'):
            row = lookup.get((str(game['id']), game[side + 'Team']))
            if row and game.get(side + 'Points') is not None and row['offensiveDrivePoints'] > game[side + 'Points']:
                scoring_issues.append(dict(gameId=str(game['id']), team=row['team'],
                    adjudicatedOffensivePoints=row['offensiveDrivePoints'], finalPoints=game[side + 'Points']))
    quarantined = {r['gameId'] for r in scoring_issues}
    rankings = aggregate_rankings(games, [r for r in rows if str(r['gameId']) not in quarantined])
    coverage = dict(completedGames=len(games), rankedTeams=sum(r['netRank'] is not None for r in rankings),
        fbsVsFcsGames=sum('fcs' in (g.get('homeClassification'), g.get('awayClassification')) for g in games),
        missingGames=sorted({gid for r in rankings for gid in r['missingGames']}),
        scoringConflicts=scoring_issues, gamesIncluded=len(games)-len({gid for r in rankings for gid in r['missingGames']}),
        resolvedPossessions=sum(r['resolvedPointPossessions'] for r in rows),
        unresolvedPossessions=sum(r['unresolvedPointPossessions'] for r in rows), reviewDriveGroups=len(review))
    output.mkdir(parents=True, exist_ok=True)
    artifact = dict(version=VERSION, season=season, asOf=as_of, generatedAtUtc=datetime.now(timezone.utc).isoformat(),
        coverage=coverage, sources=sources, rankings=rankings, teamGames=rows, completedGames=games, reviewDriveGroups=review)
    (output / 'rankings.json').write_text(json.dumps(artifact, indent=2) + '\n')
    lines = [f'# SOAR Analytics — {season} unadjusted drive rankings', '', f'As of {as_of}. {coverage["completedGames"]} completed games involving FBS teams, including {coverage["fbsVsFcsGames"]} against FCS opponents. {coverage["rankedTeams"]} FBS teams ranked.', '',
        'Offense = offensive points / resolved offensive possessions (higher is better). Defense = opponent offensive points / resolved defensive possessions (lower is better). Net = offense minus defense (higher is better). Totals are pooled across games; game averages are not averaged. No opponent adjustment, preseason priors, shrinkage, or additional garbage-time filter.', '',
        'Uses Drive Efficiency v1 and Finishing Drives v2 adjudication: validated possession drives only; adjudicated touchdowns include their conversion points, field goals count three, and empty possessions count zero. Defensive/return scores are not credited as offensive production. Unresolved point outcomes are excluded from both point numerator and resolved-drive denominator. Exact ties share competition rank (1, 1, 3).', '',
        f'Coverage across acquired games: {coverage["resolvedPossessions"]} resolved possessions; {coverage["unresolvedPossessions"]} unresolved; {coverage["reviewDriveGroups"]} source drive groups excluded for validation review. Games usable for rankings: {coverage["gamesIncluded"]}/{len(games)}. Teams with unavailable or quarantined games are unranked. This is observed early-season performance, not a schedule-adjusted power rating.', '']
    if scoring_issues:
        lines += ['Scoring conflicts (both teams in each affected game are unranked):', '']
        lines += [f'- {r["team"]}, game {r["gameId"]}: existing adjudication credits {r["adjudicatedOffensivePoints"]:g} offensive points, exceeding the final score of {r["finalPoints"]}. No points have been manually corrected.' for r in scoring_issues]
        lines.append('')
    for title, rank in [('Net rankings', 'netRank'), ('Offense rankings', 'offenseRank'), ('Defense rankings', 'defenseRank')]:
        lines += [f'## {title}', '', '| Rank | Team | Games | Off. drives | Def. drives | Off. PPD | Def. PPD allowed | Net PPD | Off. rank | Def. rank |', '|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in sorted(rankings, key=lambda r: (r[rank] or 9999, r['team'])):
            fmt = lambda v: '—' if v is None else f'{v:.3f}'
            lines.append(f'| {r[rank] or "—"} | {r["team"]} | {r["gamesIncluded"]}/{r["gamesPlayed"]} | {r["offensiveDrives"]} | {r["defensiveDrives"]} | {fmt(r["offensePPD"])} | {fmt(r["defensePPDAllowed"])} | {fmt(r["netPPD"])} | {r["offenseRank"] or "—"} | {r["defenseRank"] or "—"} |')
        lines.append('')
    (output / 'report.md').write_text('\n'.join(lines))
    print(json.dumps(coverage, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-root', type=Path, required=True)
    parser.add_argument('--processed-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--season', type=int, required=True)
    parser.add_argument('--as-of', required=True)
    args = parser.parse_args()
    run(args.raw_root, args.processed_root, args.output, args.season, args.as_of)


if __name__ == '__main__':
    main()

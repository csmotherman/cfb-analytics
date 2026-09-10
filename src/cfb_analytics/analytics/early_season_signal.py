"""Reproducible, disjoint-window early-season research; no production changes."""
from collections import Counter
import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

from cfb_analytics.analytics.schedule_adjusted.dataset import collect_published_team_games, build_observations
from cfb_analytics.analytics.schedule_adjusted.model import fit_schedule_adjusted
from cfb_analytics.analytics.schedule_adjusted.specs import CORE_METRICS, METRIC_SPECS

OUT = Path('data/research/early_season_signal')
YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025]


def run():
    records, coverage = [], []
    for year in YEARS:
        source = collect_published_team_games(Path('data/published'), year)
        teams = {str(r['team_id']): r['team'] for r in source if r.get('classification') == 'fbs'}
        rows = [r for r in source if r.get('season_type') == 'regular' and r.get('classification') == 'fbs' and r.get('opponent_classification') == 'fbs' and r.get('gameValidationStatus') == 'PASS']
        windows = {'week1': [r for r in rows if r['week'] == 1], 'week2': [r for r in rows if r['week'] == 2], 'weeks1_2': [r for r in rows if 1 <= r['week'] <= 2], 'rest': [r for r in rows if r['week'] > 2]}
        counts = {w: Counter(str(r['team_id']) for r in rr) for w, rr in windows.items()}
        assert not ({r['gameId'] for r in windows['weeks1_2']} & {r['gameId'] for r in windows['rest']})
        coverage.extend(dict(season=year, team=name, team_id=t, **{w: c[t] for w,c in counts.items()}) for t,name in teams.items())
        for metric in CORE_METRICS:
            spec = METRIC_SPECS[metric]
            values = {}
            for window, rr in windows.items():
                obs = build_observations(rr, spec)
                fitted = fit_schedule_adjusted(obs, spec)
                assert fitted.converged, (year, metric, window)
                values[window] = {}
                for team in teams:
                    off = [o for o in obs if o.offense_team == team]
                    deff = [o for o in obs if o.defense_team == team]
                    if not off or not deff: continue
                    raw_o = sum(o.numerator for o in off) / sum(o.denominator for o in off)
                    raw_d = sum(o.numerator for o in deff) / sum(o.denominator for o in deff)
                    values[window][team] = {'adjusted_offense': fitted.adjusted_offense_value(team) * spec.orientation,
                        'adjusted_defense': -fitted.adjusted_defense_value(team) * spec.orientation,
                        'adjusted_net': (fitted.adjusted_offense_value(team) - fitted.adjusted_defense_value(team)) * spec.orientation,
                        'raw_net': (raw_o - raw_d) * spec.orientation}
            for window in ('week1', 'week2', 'weeks1_2'):
                eligible = sorted(t for t in values[window] if t in values['rest'] and counts['rest'][t] >= 6)
                for kind in ('adjusted_offense', 'adjusted_defense', 'adjusted_net', 'raw_net'):
                    early = [values[window][t][kind] for t in eligible]
                    target_kind = 'adjusted_net' if kind == 'raw_net' else kind
                    later = [values['rest'][t][target_kind] for t in eligible]
                    ep = (rankdata(early) - .5) / len(eligible)
                    lp = (rankdata(later) - .5) / len(eligible)
                    for i,t in enumerate(eligible):
                        records.append(dict(season=year, team=teams[t], metric=metric, window=window, kind=kind, early=early[i], rest=later[i], early_percentile=ep[i], rest_percentile=lp[i], early_games=counts[window][t], rest_games=counts['rest'][t]))
        print(f'{year}: {len(teams)} teams processed', flush=True)
    summaries = []
    for metric in CORE_METRICS:
        for window in ('week1', 'week2', 'weeks1_2'):
            for kind in ('adjusted_offense', 'adjusted_defense', 'adjusted_net', 'raw_net'):
                rr = [r for r in records if (r['metric'], r['window'], r['kind']) == (metric, window, kind)]
                x = np.array([r['early_percentile'] for r in rr]); y = np.array([r['rest_percentile'] for r in rr])
                yearly = [float(spearmanr([r['early'] for r in rr if r['season']==yr], [r['rest'] for r in rr if r['season']==yr]).statistic) for yr in YEARS]
                top = x >= .75
                summaries.append(dict(metric=metric, window=window, kind=kind, n=len(rr), rank_correlation=float(spearmanr(x,y).statistic), yearly_min=min(yearly), yearly_max=max(yearly), median_percentile_move=float(np.median(abs(x-y))*100), half_flip=float(np.mean((x>=.5)!=(y>=.5))), top_quartile_retention=float(np.mean(y[top]>=.75)), early_top_to_bottom_half=float(np.mean(y[top]<.5))))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'results.json').write_text(json.dumps(dict(version='early-season-signal-v1', summaries=summaries, coverage=coverage, team_metrics=records), indent=2)+'\n')
    latest = [r for r in records if r['season']==2025 and r['metric']=='successRate' and r['window']=='weeks1_2' and r['kind']=='adjusted_net']
    lookup = {r['team']: r for r in latest}
    lines = ['# 2025 early-season signal: every FBS team', '', 'Opponent-adjusted net success rate. Percentiles are among eligible teams, higher is better. Early and later models are fit independently. Rates shown in percentage points. No eligible early game means no estimate.', '', '| Team | Early FBS games | Later FBS games | Early net SR | Later net SR | Early percentile | Later percentile |', '|---|---:|---:|---:|---:|---:|---:|']
    for c in sorted((c for c in coverage if c['season']==2025), key=lambda c:c['team']):
        r=lookup.get(c['team'])
        cells = f"{100*r['early']:.1f} | {100*r['rest']:.1f} | {100*r['early_percentile']:.0f} | {100*r['rest_percentile']:.0f}" if r else '— | — | — | —'
        lines.append(f"| {c['team']} | {c['weeks1_2']} | {c['rest']} | {cells} |")
    (OUT/'all-teams-2025.md').write_text('\n'.join(lines)+'\n')


if __name__ == '__main__':
    run()

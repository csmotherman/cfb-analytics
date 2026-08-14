from pathlib import Path
import math

from cfb_analytics.analytics.iterative_ratings import (
    ITERATIVE_FEATURES,
    SRS_FEATURES,
    eligible_iterative_row,
    materialize_iterative_model_dataset,
)
from cfb_analytics.analytics.opponent_adjustment_ablation import fit_model, score_model
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS, TEST_SEASONS
from cfb_analytics.derived.sandbox_pregame import SYSTEMS, build_matchups, build_pregame

BASE=tuple(ITERATIVE_FEATURES)+tuple(SRS_FEATURES)
SYSTEM_FEATURES={
    system:(f"home_{system}_OffenseEdge",f"home_{system}_DefenseEdge")
    for system in SYSTEMS
}
ALL_SYSTEMS=tuple(k for system in SYSTEMS for k in SYSTEM_FEATURES[system])
FULL=BASE+ALL_SYSTEMS


def finite(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))


def orient_sandbox(row,matchup):
    home=row.get("homeTeam");away=row.get("awayTeam")
    if {home,away}!={matchup.get("team1"),matchup.get("team2")}:
        return None
    home_is_1=home==matchup.get("team1")
    out=dict(row)
    for system in SYSTEMS:
        prefix="team1" if home_is_1 else "team2"
        out[f"home_{system}_OffenseEdge"]=matchup.get(f"{prefix}_{system}_OffenseEdge")
        out[f"home_{system}_DefenseEdge"]=matchup.get(f"{prefix}_{system}_DefenseEdge")
    return out


def load(raw_root,processed_root,season):
    result=materialize_iterative_model_dataset(raw_root,processed_root,season)
    if result["status"]!="PASS":
        raise RuntimeError(f"season {season} iterative audit failed: {result['checks']}")
    import json
    rows=json.loads((processed_root/"derived"/"iterative_ratings"/f"season={season}"/"games.json").read_text())
    snaps=build_pregame(raw_root,processed_root,season)
    matchups={str(r.get("gameId")):r for r in build_matchups(snaps,season)}
    merged=[]
    for row in rows:
        m=matchups.get(str(row.get("gameId")))
        if m:
            x=orient_sandbox(row,m)
            if x is not None:merged.append(x)
    print(f"LOAD {season}: model={len(rows):,} sandbox={len(matchups):,} merged={len(merged):,}")
    return merged


def eligible(row,min_games):
    return eligible_iterative_row(row,min_games) and all(finite(row.get(k)) for k in FULL)


def home_only(rows):
    return sum(r.get("target_homeWin")==1 for r in rows)/len(rows) if rows else 0.0


def main():
    raw_root=Path("data/raw");processed_root=Path("data/processed")
    data={s:load(raw_root,processed_root,s) for s in DEFAULT_SEASONS}
    models={"BASE_ITERATIVE_SRS":BASE,"SYSTEMS_ONLY":ALL_SYSTEMS}
    for system in SYSTEMS:
        models[f"BASE_PLUS_{system}"]=BASE+SYSTEM_FEATURES[system]
    models["BASE_PLUS_ALL_SYSTEMS"]=FULL

    print("CFB SANDBOX SYSTEM ABLATION v1")
    print("Baseline: ITERATIVE + SRS")
    print("Common eligible sample across every model: YES")
    print(f"Features: base={len(BASE)} systems={len(ALL_SYSTEMS)} full={len(FULL)}")

    for min_games in (3,4):
        elig={s:[r for r in data[s] if eligible(r,min_games)] for s in DEFAULT_SEASONS}
        print(f"\nMINIMUM PRIOR GAMES PER TEAM: {min_games}")
        for test_season in TEST_SEASONS:
            train=[r for s in DEFAULT_SEASONS if s<test_season for r in elig[s]]
            test=elig[test_season]
            print(f"\nTEST {test_season}")
            print(f"COMMON SAMPLE: train={len(train):,} test={len(test):,}")
            print(f"HOME-ONLY WINNER BASELINE: {home_only(test):.2%}")
            fitted={name:fit_model(train,features) for name,features in models.items()}
            scored={name:score_model(fitted[name],test) for name in models}
            base=scored["BASE_ITERATIVE_SRS"]
            for name,x in scored.items():
                print(f"{name}: n={x['test_games']:,} MAE={x['margin_mae']:.3f} RMSE={x['margin_rmse']:.3f} Winner={x['winner_accuracy']:.2%} LogitIters={x['logit_iterations']}")
            print("ADDITIONS VS BASE:")
            for system in SYSTEMS:
                x=scored[f"BASE_PLUS_{system}"]
                print(f"  {system}: MAE {x['margin_mae']-base['margin_mae']:+.3f}, RMSE {x['margin_rmse']-base['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-base['winner_accuracy'])*100:+.2f} pp")
            x=scored["BASE_PLUS_ALL_SYSTEMS"]
            print(f"  ALL: MAE {x['margin_mae']-base['margin_mae']:+.3f}, RMSE {x['margin_rmse']-base['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-base['winner_accuracy'])*100:+.2f} pp")
            print("LEAVE-ONE-SYSTEM-OUT FROM FULL:")
            for system in SYSTEMS:
                features=tuple(k for k in FULL if k not in SYSTEM_FEATURES[system])
                z=score_model(fit_model(train,features),test)
                print(f"  minus {system}: MAE {z['margin_mae']-x['margin_mae']:+.3f}, RMSE {z['margin_rmse']-x['margin_rmse']:+.3f}, Winner {(z['winner_accuracy']-x['winner_accuracy'])*100:+.2f} pp")


if __name__=="__main__":
    main()

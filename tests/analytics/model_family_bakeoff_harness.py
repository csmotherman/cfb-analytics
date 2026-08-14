from pathlib import Path
import json, math

try:
    import numpy as np
    from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import HuberRegressor, Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    raise SystemExit(
        'Missing research model dependencies. Run: pip install -e ".[models]"'
    ) from exc

from cfb_analytics.analytics.football_mechanisms import orient_matchup
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES, SRS_FEATURES, eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

BASE = tuple(ITERATIVE_FEATURES) + tuple(SRS_FEATURES)
MWDR = ("home_MWDR_OffenseEdge", "home_MWDR_DefenseEdge")
STABLE = BASE + MWDR + ("mwdrXExpectedPossessions",)
VOLUME = ("successVolumeEdge", "explosiveVolumeEdge", "turnoverVolumeEdge")
FEATURE_SETS = {
    "STABLE": STABLE,
    "VOLUME": STABLE + VOLUME,
}
VALIDATION_SEASONS = tuple(s for s in DEFAULT_SEASONS if s >= 2018)


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def add_features(r, x):
    z = {**r, **x}
    poss = z.get("expectedPossessionsPerTeam")
    mwdr = (float(z[MWDR[0]]) + float(z[MWDR[1]])) if finite(z.get(MWDR[0])) and finite(z.get(MWDR[1])) else None
    z["mwdrXExpectedPossessions"] = mwdr * float(poss) if finite(mwdr) and finite(poss) else None
    z["successVolumeEdge"] = float(z["netSuccessRateEdge"]) * float(poss) if finite(z.get("netSuccessRateEdge")) and finite(poss) else None
    z["explosiveVolumeEdge"] = float(z["netExplosiveRateEdge"]) * float(poss) if finite(z.get("netExplosiveRateEdge")) and finite(poss) else None
    z["turnoverVolumeEdge"] = float(z["netTurnoverPressureEdge"]) * float(poss) if finite(z.get("netTurnoverPressureEdge")) and finite(poss) else None
    return z


def load_all():
    pr = Path("data/processed")
    data = {}
    print("Loading saved feature stores only; model-family bakeoff.")
    for season in DEFAULT_SEASONS:
        base = load_saved_feature_store(pr, season)
        p = pr / "derived" / "football_mechanisms" / f"season={season}" / "matchups.json"
        if not p.exists():
            raise FileNotFoundError(
                f"Missing football mechanisms for {season}. Run: python -m cfb_analytics.analytics.football_mechanisms --all"
            )
        match = {str(q.get("gameId")): q for q in json.loads(p.read_text())}
        rows = []
        for r in base:
            m = match.get(str(r.get("gameId")))
            if not m:
                continue
            x = orient_matchup(m, r.get("homeTeam"), r.get("awayTeam"))
            if x is not None:
                rows.append(add_features(r, x))
        data[season] = rows
    return data


def eligible(r, min_games, features):
    return eligible_iterative_row(r, min_games) and all(finite(r.get(k)) for k in features)


def xy(rows, features):
    x = np.asarray([[float(r[k]) for k in features] for r in rows], dtype=float)
    y = np.asarray([float(r["target_margin"]) for r in rows], dtype=float)
    wins = np.asarray([bool(r["target_homeWin"]) for r in rows], dtype=bool)
    return x, y, wins


def model_factories():
    return {
        "RIDGE": lambda: make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "HUBER": lambda: make_pipeline(StandardScaler(), HuberRegressor(epsilon=1.35, alpha=0.0001, max_iter=500)),
        "RANDOM_FOREST": lambda: RandomForestRegressor(
            n_estimators=250,
            max_depth=8,
            min_samples_leaf=10,
            max_features=0.7,
            random_state=42,
            n_jobs=-1,
        ),
        "EXTRA_TREES": lambda: ExtraTreesRegressor(
            n_estimators=250,
            max_depth=10,
            min_samples_leaf=8,
            max_features=0.8,
            random_state=42,
            n_jobs=-1,
        ),
        "GRADIENT_BOOSTING": lambda: GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.03,
            max_depth=2,
            min_samples_leaf=12,
            subsample=0.85,
            loss="huber",
            random_state=42,
        ),
    }


def score_predictions(pred, y, wins):
    err = pred - y
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err ** 2))),
        "winner": float(np.mean((pred > 0) == wins)),
    }


def summarize(rows):
    return {
        "mae": sum(r["dmae"] for r in rows) / len(rows),
        "rmse": sum(r["drmse"] for r in rows) / len(rows),
        "winner": sum(r["dwin"] for r in rows) / len(rows),
        "mae_wins": sum(r["dmae"] < 0 for r in rows),
        "rmse_wins": sum(r["drmse"] < 0 for r in rows),
        "n": len(rows),
    }


def main():
    data = load_all()
    results = {}
    reference_rows = {}

    for min_games in (3, 4):
        stable_elig = {
            s: [r for r in data[s] if eligible(r, min_games, STABLE)] for s in DEFAULT_SEASONS
        }
        volume_elig = {
            s: [r for r in data[s] if eligible(r, min_games, STABLE + VOLUME)] for s in DEFAULT_SEASONS
        }

        for test_season in VALIDATION_SEASONS:
            prior = [s for s in DEFAULT_SEASONS if s < test_season]
            if len(prior) < 4:
                continue

            # Reference ridge uses the common VOLUME-eligible sample so every model/feature set
            # is compared on exactly the same rows for this holdout.
            train_ref = [r for s in prior for r in volume_elig[s]]
            test_ref = volume_elig[test_season]
            if not train_ref or not test_ref:
                continue

            xtr, ytr, _ = xy(train_ref, STABLE)
            xte, yte, wins = xy(test_ref, STABLE)
            ref_model = model_factories()["RIDGE"]()
            ref_model.fit(xtr, ytr)
            ref_score = score_predictions(ref_model.predict(xte), yte, wins)
            reference_rows[(min_games, test_season)] = ref_score

            for feature_name, features in FEATURE_SETS.items():
                train = [r for s in prior for r in volume_elig[s]]
                test = volume_elig[test_season]
                xtr, ytr, _ = xy(train, features)
                xte, yte, wins = xy(test, features)

                for model_name, factory in model_factories().items():
                    model = factory()
                    model.fit(xtr, ytr)
                    q = score_predictions(model.predict(xte), yte, wins)
                    key = f"{feature_name}_{model_name}"
                    results.setdefault(key, []).append({
                        "min_games": min_games,
                        "season": test_season,
                        "n": len(test),
                        "dmae": q["mae"] - ref_score["mae"],
                        "drmse": q["rmse"] - ref_score["rmse"],
                        "dwin": (q["winner"] - ref_score["winner"]) * 100,
                    })

    ranked = []
    for name, rows in results.items():
        s = summarize(rows)
        recent_rows = [r for r in rows if r["season"] >= 2023]
        recent = summarize(recent_rows)
        ranked.append({"name": name, **s, "recent_mae": recent["mae"], "recent_rmse": recent["rmse"], "rows": rows})

    ranked.sort(key=lambda r: (r["mae"], r["rmse"], -r["mae_wins"]))

    print("MODEL FAMILY BAKEOFF — DECISION REPORT")
    print("Reference: STABLE_RIDGE on the common VOLUME-eligible sample")
    print("Feature sets: STABLE and STABLE + Volume Engine")
    print("Models: Ridge, Huber, Random Forest, Extra Trees, Gradient Boosting")
    print("All models use identical walk-forward holdouts and target_margin; negative MAE/RMSE is better.\n")

    print("TOP 10 ACROSS ALL HOLDOUTS:")
    for i, r in enumerate(ranked[:10], 1):
        print(
            f" {i:2d}. {r['name']}: MAE {r['mae']:+.4f} | RMSE {r['rmse']:+.4f} | "
            f"Winner {r['winner']:+.2f} pp | MAE better {r['mae_wins']}/{r['n']} | "
            f"RMSE better {r['rmse_wins']}/{r['n']} | 2023-25 MAE {r['recent_mae']:+.4f}"
        )

    best = ranked[0]
    recent_ranked = sorted(ranked, key=lambda r: (r["recent_mae"], r["recent_rmse"]))
    print(f"\nBEST OVERALL: {best['name']}")
    print(f"BEST 2023-2025: {recent_ranked[0]['name']} — MAE {recent_ranked[0]['recent_mae']:+.4f} | RMSE {recent_ranked[0]['recent_rmse']:+.4f}")

    print("\nMODEL-FAMILY BESTS:")
    for family in ("RIDGE", "HUBER", "RANDOM_FOREST", "EXTRA_TREES", "GRADIENT_BOOSTING"):
        subset = [r for r in ranked if r["name"].endswith(family)]
        b = min(subset, key=lambda r: (r["mae"], r["rmse"]))
        print(f" {family}: {b['name']} | MAE {b['mae']:+.4f} | RMSE {b['rmse']:+.4f} | Winner {b['winner']:+.2f} pp")

    print("\nBEST HOLDOUT CHECK:")
    for r in best["rows"]:
        print(
            f" min{r['min_games']} {r['season']}: MAE {r['dmae']:+.4f} | RMSE {r['drmse']:+.4f} | "
            f"Winner {r['dwin']:+.2f} pp | n={r['n']}"
        )


if __name__ == "__main__":
    main()

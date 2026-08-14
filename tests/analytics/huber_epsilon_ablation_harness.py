from pathlib import Path
import json, math

try:
    import numpy as np
    from sklearn.linear_model import HuberRegressor, LinearRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    raise SystemExit('Missing research model dependencies. Run: pip install -e ".[models]"') from exc

from cfb_analytics.analytics.football_mechanisms import orient_matchup
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES, SRS_FEATURES, eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

BASE = tuple(ITERATIVE_FEATURES) + tuple(SRS_FEATURES)
MWDR = ("home_MWDR_OffenseEdge", "home_MWDR_DefenseEdge")
STABLE = BASE + MWDR + ("mwdrXExpectedPossessions",)
VOLUME = ("successVolumeEdge", "explosiveVolumeEdge", "turnoverVolumeEdge")
FEATURE_SETS = {"STABLE": STABLE, "VOLUME": STABLE + VOLUME}
EPSILONS = (1.20, 1.35, 1.50, 1.75, 2.00)
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
    print("Loading saved feature stores only; Huber epsilon ablation.")
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


def eligible(r, min_games):
    return eligible_iterative_row(r, min_games) and all(finite(r.get(k)) for k in STABLE + VOLUME)


def xy(rows, features):
    x = np.asarray([[float(r[k]) for k in features] for r in rows], dtype=float)
    y = np.asarray([float(r["target_margin"]) for r in rows], dtype=float)
    wins = np.asarray([bool(r["target_homeWin"]) for r in rows], dtype=bool)
    return x, y, wins


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


def make_ols():
    return make_pipeline(StandardScaler(), LinearRegression())


def make_huber(epsilon):
    return make_pipeline(
        StandardScaler(),
        HuberRegressor(epsilon=epsilon, alpha=0.0001, max_iter=1000),
    )


def main():
    data = load_all()
    results = {}

    for min_games in (3, 4):
        elig = {s: [r for r in data[s] if eligible(r, min_games)] for s in DEFAULT_SEASONS}
        for test_season in VALIDATION_SEASONS:
            prior = [s for s in DEFAULT_SEASONS if s < test_season]
            if len(prior) < 4:
                continue
            train = [r for s in prior for r in elig[s]]
            test = elig[test_season]
            if not train or not test:
                continue

            xtr_ref, ytr, _ = xy(train, STABLE)
            xte_ref, yte, wins = xy(test, STABLE)
            ref = make_ols()
            ref.fit(xtr_ref, ytr)
            ref_score = score_predictions(ref.predict(xte_ref), yte, wins)

            for feature_name, features in FEATURE_SETS.items():
                xtr, ytr, _ = xy(train, features)
                xte, yte, wins = xy(test, features)

                if feature_name == "VOLUME":
                    ols = make_ols()
                    ols.fit(xtr, ytr)
                    q = score_predictions(ols.predict(xte), yte, wins)
                    results.setdefault("VOLUME_OLS", []).append({
                        "min_games": min_games,
                        "season": test_season,
                        "n": len(test),
                        "dmae": q["mae"] - ref_score["mae"],
                        "drmse": q["rmse"] - ref_score["rmse"],
                        "dwin": (q["winner"] - ref_score["winner"]) * 100,
                    })

                for epsilon in EPSILONS:
                    model = make_huber(epsilon)
                    model.fit(xtr, ytr)
                    q = score_predictions(model.predict(xte), yte, wins)
                    key = f"{feature_name}_HUBER_{epsilon:.2f}"
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
        overall = summarize(rows)
        recent = summarize([r for r in rows if r["season"] >= 2023])
        latest = summarize([r for r in rows if r["season"] >= 2024])
        ranked.append({
            "name": name,
            **overall,
            "recent_mae": recent["mae"],
            "recent_rmse": recent["rmse"],
            "recent_winner": recent["winner"],
            "latest_mae": latest["mae"],
            "latest_rmse": latest["rmse"],
            "rows": rows,
        })

    ranked.sort(key=lambda r: (r["mae"], r["rmse"], -r["mae_wins"]))
    recent_ranked = sorted(ranked, key=lambda r: (r["recent_mae"], r["recent_rmse"]))
    latest_ranked = sorted(ranked, key=lambda r: (r["latest_mae"], r["latest_rmse"]))

    print("HUBER EPSILON — DECISION REPORT")
    print("Reference: STABLE_OLS on the common VOLUME-eligible sample")
    print("Feature sets: STABLE and STABLE + Volume Engine")
    print("Huber epsilons: 1.20, 1.35, 1.50, 1.75, 2.00; lower is more robust, higher is more OLS-like.")
    print("Negative MAE/RMSE is better; positive Winner pp is better.\n")

    print("TOP 10 ACROSS ALL 14 HOLDOUTS:")
    for i, r in enumerate(ranked[:10], 1):
        print(
            f" {i:2d}. {r['name']}: MAE {r['mae']:+.4f} | RMSE {r['rmse']:+.4f} | "
            f"Winner {r['winner']:+.2f} pp | MAE better {r['mae_wins']}/{r['n']} | "
            f"RMSE better {r['rmse_wins']}/{r['n']} | 2023-25 MAE {r['recent_mae']:+.4f} | "
            f"2024-25 MAE {r['latest_mae']:+.4f}"
        )

    print(f"\nBEST OVERALL: {ranked[0]['name']}")
    print(
        f"BEST 2023-2025: {recent_ranked[0]['name']} — MAE {recent_ranked[0]['recent_mae']:+.4f} | "
        f"RMSE {recent_ranked[0]['recent_rmse']:+.4f} | Winner {recent_ranked[0]['recent_winner']:+.2f} pp"
    )
    print(
        f"BEST 2024-2025: {latest_ranked[0]['name']} — MAE {latest_ranked[0]['latest_mae']:+.4f} | "
        f"RMSE {latest_ranked[0]['latest_rmse']:+.4f}"
    )

    best = ranked[0]
    print("\nBEST OVERALL HOLDOUT CHECK:")
    for r in best["rows"]:
        print(
            f" min{r['min_games']} {r['season']}: MAE {r['dmae']:+.4f} | RMSE {r['drmse']:+.4f} | "
            f"Winner {r['dwin']:+.2f} pp | n={r['n']}"
        )


if __name__ == "__main__":
    main()

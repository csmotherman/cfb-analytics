from pathlib import Path
import json, math

try:
    import numpy as np
    from sklearn.linear_model import LinearRegression, LogisticRegression
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
FEATURES = STABLE + VOLUME
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
    print("Loading saved feature stores only; two-stage margin architecture.")
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
    return eligible_iterative_row(r, min_games) and all(finite(r.get(k)) for k in FEATURES)


def xy(rows):
    x = np.asarray([[float(r[k]) for k in FEATURES] for r in rows], dtype=float)
    margin = np.asarray([float(r["target_margin"]) for r in rows], dtype=float)
    wins = np.asarray([bool(r["target_homeWin"]) for r in rows], dtype=bool)
    return x, margin, wins


def ols_model():
    return make_pipeline(StandardScaler(), LinearRegression())


def logistic_model():
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs"),
    )


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
        "winner_wins": sum(r["dwin"] > 0 for r in rows),
        "n": len(rows),
    }


def main():
    data = load_all()
    results = {
        "TWO_STAGE_HARD_SIGN": [],
        "TWO_STAGE_SOFT_SIGN": [],
    }

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

            xtr, ytr, win_tr = xy(train)
            xte, yte, win_te = xy(test)

            reference = ols_model()
            reference.fit(xtr, ytr)
            ref_pred = reference.predict(xte)
            ref_score = score_predictions(ref_pred, yte, win_te)

            direction = logistic_model()
            magnitude = ols_model()
            direction.fit(xtr, win_tr.astype(int))
            magnitude.fit(xtr, np.abs(ytr))

            p_home = direction.predict_proba(xte)[:, 1]
            expected_abs_margin = np.maximum(magnitude.predict(xte), 0.0)

            hard_sign = np.where(p_home >= 0.5, 1.0, -1.0)
            hard_pred = hard_sign * expected_abs_margin
            soft_pred = (2.0 * p_home - 1.0) * expected_abs_margin

            candidates = {
                "TWO_STAGE_HARD_SIGN": hard_pred,
                "TWO_STAGE_SOFT_SIGN": soft_pred,
            }

            for name, pred in candidates.items():
                q = score_predictions(pred, yte, win_te)
                results[name].append({
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
            "latest_winner": latest["winner"],
            "rows": rows,
        })

    ranked.sort(key=lambda r: (r["mae"], r["rmse"], -r["winner"]))
    recent_ranked = sorted(ranked, key=lambda r: (r["recent_mae"], r["recent_rmse"], -r["recent_winner"]))
    latest_ranked = sorted(ranked, key=lambda r: (r["latest_mae"], r["latest_rmse"], -r["latest_winner"]))

    print("TWO-STAGE MARGIN ARCHITECTURE — DECISION REPORT")
    print("Reference: VOLUME_OLS trained directly on signed target_margin")
    print("Two-stage: logistic win direction + OLS expected absolute margin")
    print("Hard sign uses p>=0.50; soft sign uses (2p-1) x expected absolute margin.")
    print("Negative MAE/RMSE is better; positive Winner pp is better.\n")

    print("RESULTS ACROSS ALL 14 HOLDOUTS:")
    for i, r in enumerate(ranked, 1):
        print(
            f" {i}. {r['name']}: MAE {r['mae']:+.4f} | RMSE {r['rmse']:+.4f} | "
            f"Winner {r['winner']:+.2f} pp | MAE better {r['mae_wins']}/{r['n']} | "
            f"RMSE better {r['rmse_wins']}/{r['n']} | Winner better {r['winner_wins']}/{r['n']} | "
            f"2023-25 MAE {r['recent_mae']:+.4f} | 2024-25 MAE {r['latest_mae']:+.4f}"
        )

    print(f"\nBEST OVERALL: {ranked[0]['name']}")
    print(
        f"BEST 2023-2025: {recent_ranked[0]['name']} — MAE {recent_ranked[0]['recent_mae']:+.4f} | "
        f"RMSE {recent_ranked[0]['recent_rmse']:+.4f} | Winner {recent_ranked[0]['recent_winner']:+.2f} pp"
    )
    print(
        f"BEST 2024-2025: {latest_ranked[0]['name']} — MAE {latest_ranked[0]['latest_mae']:+.4f} | "
        f"RMSE {latest_ranked[0]['latest_rmse']:+.4f} | Winner {latest_ranked[0]['latest_winner']:+.2f} pp"
    )

    print("\nBEST OVERALL HOLDOUT CHECK:")
    for r in ranked[0]["rows"]:
        print(
            f" min{r['min_games']} {r['season']}: MAE {r['dmae']:+.4f} | RMSE {r['drmse']:+.4f} | "
            f"Winner {r['dwin']:+.2f} pp | n={r['n']}"
        )


if __name__ == "__main__":
    main()

from pathlib import Path
import json, math

from cfb_analytics.analytics.football_mechanisms import orient_matchup
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES, SRS_FEATURES, eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS, _solve

BASE = tuple(ITERATIVE_FEATURES) + tuple(SRS_FEATURES)
MWDR = ("home_MWDR_OffenseEdge", "home_MWDR_DefenseEdge")
STABLE = BASE + MWDR + ("mwdrXExpectedPossessions",)
VOLUME = ("successVolumeEdge", "explosiveVolumeEdge", "turnoverVolumeEdge")
LEADING = STABLE + VOLUME
FULL = LEADING
INDEX = {k: i for i, k in enumerate(FULL)}
VALIDATION_SEASONS = tuple(s for s in DEFAULT_SEASONS if s >= 2018)
DECAYS = {
    "EQUAL": 1.00,
    "MILD_090": 0.90,
    "MEDIUM_080": 0.80,
    "STRONG_070": 0.70,
}


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def add_features(r, x, season):
    z = {**r, **x, "_train_season": season}
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
    print("Loading saved feature stores only; recency-weighting ablation.")
    for season in DEFAULT_SEASONS:
        base = load_saved_feature_store(pr, season)
        p = pr / "derived" / "football_mechanisms" / f"season={season}" / "matchups.json"
        if not p.exists():
            raise FileNotFoundError(f"Missing football mechanisms for {season}. Run: python -m cfb_analytics.analytics.football_mechanisms --all")
        match = {str(q.get("gameId")): q for q in json.loads(p.read_text())}
        rows = []
        for r in base:
            m = match.get(str(r.get("gameId")))
            if not m:
                continue
            x = orient_matchup(m, r.get("homeTeam"), r.get("awayTeam"))
            if x is not None:
                rows.append(add_features(r, x, season))
        data[season] = rows
    return data


def eligible(r, min_games):
    return eligible_iterative_row(r, min_games) and all(finite(r.get(k)) for k in FULL)


def season_weight(row_season, test_season, decay):
    if decay >= 1.0:
        return 1.0
    age = max(0, int(test_season) - int(row_season) - 1)
    return decay ** age


def prepare(rows, test_season, decay):
    weights = [season_weight(r["_train_season"], test_season, decay) for r in rows]
    total_w = sum(weights)
    means, scales = [], []
    for k in FULL:
        vals = [float(r[k]) for r in rows]
        m = sum(w * x for w, x in zip(weights, vals)) / total_w
        v = sum(w * (x - m) ** 2 for w, x in zip(weights, vals)) / total_w
        means.append(m)
        scales.append(math.sqrt(v) or 1.0)

    p = len(FULL) + 1
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p
    for r, w in zip(rows, weights):
        x = [1.0] + [(float(r[k]) - means[i]) / scales[i] for i, k in enumerate(FULL)]
        y = float(r["target_margin"])
        for i, xi in enumerate(x):
            xty[i] += w * xi * y
            for j in range(i, p):
                xtx[i][j] += w * xi * x[j]
    for i in range(p):
        for j in range(i):
            xtx[i][j] = xtx[j][i]
    return {"means": means, "scales": scales, "xtx": xtx, "xty": xty}


def fit(stats, features, ridge=1e-6):
    idx = [0] + [INDEX[k] + 1 for k in features]
    a = [[stats["xtx"][i][j] for j in idx] for i in idx]
    b = [stats["xty"][i] for i in idx]
    for i in range(1, len(a)):
        a[i][i] += ridge
    w = _solve(a, b)
    if w is None:
        raise ValueError("singular model")
    return {"features": tuple(features), "weights": w, "means": stats["means"], "scales": stats["scales"]}


def score(model, rows):
    ae, se, correct = [], [], 0
    for r in rows:
        pred = model["weights"][0]
        for j, k in enumerate(model["features"], 1):
            i = INDEX[k]
            pred += model["weights"][j] * (float(r[k]) - model["means"][i]) / model["scales"][i]
        y = float(r["target_margin"])
        ae.append(abs(pred - y))
        se.append((pred - y) ** 2)
        correct += int((pred > 0) == bool(r["target_homeWin"]))
    n = len(rows)
    return {"mae": sum(ae) / n, "rmse": math.sqrt(sum(se) / n), "winner": correct / n}


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
    configs = {}
    for label, decay in DECAYS.items():
        configs[f"STABLE_{label}"] = (STABLE, decay)
        configs[f"VOLUME_{label}"] = (LEADING, decay)

    results = {name: [] for name in configs}
    baseline_rows = []

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

            stats_by_decay = {decay: prepare(train, test_season, decay) for decay in set(DECAYS.values())}
            baseline = score(fit(stats_by_decay[1.0], STABLE), test)
            baseline_rows.append((min_games, test_season, baseline, len(test)))

            for name, (features, decay) in configs.items():
                q = score(fit(stats_by_decay[decay], features), test)
                results[name].append({
                    "min_games": min_games,
                    "season": test_season,
                    "n": len(test),
                    "dmae": q["mae"] - baseline["mae"],
                    "drmse": q["rmse"] - baseline["rmse"],
                    "dwin": (q["winner"] - baseline["winner"]) * 100,
                })

    ranked = []
    for name, rows in results.items():
        if name == "STABLE_EQUAL":
            continue
        overall = summarize(rows)
        recent = summarize([r for r in rows if r["season"] >= 2023])
        older = summarize([r for r in rows if r["season"] <= 2022])
        ranked.append((name, overall, older, recent, rows))
    ranked.sort(key=lambda x: (x[1]["mae"], x[1]["rmse"], -x[1]["mae_wins"]))

    print("RECENCY WEIGHTING — DECISION REPORT")
    print("Reference: STABLE_EQUAL = ITERATIVE + SRS + MWDR + MWDR x EXPECTED POSSESSIONS with equal historical weights")
    print("Decay is applied by season age during training; latest prior season always has weight 1.00.")
    print("MILD=0.90, MEDIUM=0.80, STRONG=0.70 per season back.")
    print("Negative MAE/RMSE is better; positive Winner pp is better.\n")

    print("RANKED ACROSS ALL 14 HOLDOUTS:")
    for i, (name, overall, _, recent, _) in enumerate(ranked, 1):
        print(
            f" {i}. {name}: MAE {overall['mae']:+.4f} | RMSE {overall['rmse']:+.4f} | Winner {overall['winner']:+.2f} pp | "
            f"MAE better {overall['mae_wins']}/{overall['n']} | RMSE better {overall['rmse_wins']}/{overall['n']} | "
            f"2023-25 MAE {recent['mae']:+.4f}"
        )

    best_name, overall, older, recent, rows = ranked[0]
    print(f"\nBEST: {best_name}")
    print(f"OVERALL: MAE {overall['mae']:+.4f} | RMSE {overall['rmse']:+.4f} | Winner {overall['winner']:+.2f} pp")
    print(f"2018-2022: MAE {older['mae']:+.4f} | RMSE {older['rmse']:+.4f} | Winner {older['winner']:+.2f} pp")
    print(f"2023-2025: MAE {recent['mae']:+.4f} | RMSE {recent['rmse']:+.4f} | Winner {recent['winner']:+.2f} pp")

    best_holdout = min(rows, key=lambda r: r["dmae"])
    worst_holdout = max(rows, key=lambda r: r["dmae"])
    print(f"BEST HOLDOUT: min{best_holdout['min_games']} {best_holdout['season']} — MAE {best_holdout['dmae']:+.4f} | RMSE {best_holdout['drmse']:+.4f} | Winner {best_holdout['dwin']:+.2f} pp")
    print(f"WORST HOLDOUT: min{worst_holdout['min_games']} {worst_holdout['season']} — MAE {worst_holdout['dmae']:+.4f} | RMSE {worst_holdout['drmse']:+.4f} | Winner {worst_holdout['dwin']:+.2f} pp")

    print("\nINTERPRETATION CHECK:")
    best_stable = min((x for x in ranked if x[0].startswith("STABLE_")), key=lambda x: x[1]["mae"])
    best_volume = min((x for x in ranked if x[0].startswith("VOLUME_")), key=lambda x: x[1]["mae"])
    print(f" Best recency-weighted STABLE: {best_stable[0]} — MAE {best_stable[1]['mae']:+.4f} | RMSE {best_stable[1]['rmse']:+.4f}")
    print(f" Best recency-weighted VOLUME: {best_volume[0]} — MAE {best_volume[1]['mae']:+.4f} | RMSE {best_volume[1]['rmse']:+.4f}")


if __name__ == "__main__":
    main()

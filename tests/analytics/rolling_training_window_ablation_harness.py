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
WINDOWS = (None, 8, 6, 4)


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
    print("Loading saved feature stores only; rolling training-window ablation.")
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
                rows.append(add_features(r, x))
        data[season] = rows
    return data


def eligible(r, min_games):
    return eligible_iterative_row(r, min_games) and all(finite(r.get(k)) for k in FULL)


def prepare(rows):
    means, scales = [], []
    for k in FULL:
        vals = [float(r[k]) for r in rows]
        m = sum(vals) / len(vals)
        v = sum((x - m) ** 2 for x in vals) / len(vals)
        means.append(m)
        scales.append(math.sqrt(v) or 1.0)
    p = len(FULL) + 1
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p
    for r in rows:
        x = [1.0] + [(float(r[k]) - means[i]) / scales[i] for i, k in enumerate(FULL)]
        y = float(r["target_margin"])
        for i, xi in enumerate(x):
            xty[i] += xi * y
            for j in range(i, p):
                xtx[i][j] += xi * x[j]
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


def window_seasons(prior, window):
    if window is None or len(prior) <= window:
        return tuple(prior)
    return tuple(prior[-window:])


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
    experiments = {}

    for model_name, features in (("STABLE", STABLE), ("VOLUME", LEADING)):
        for window in WINDOWS:
            if model_name == "STABLE" and window is None:
                continue
            label = f"{model_name}_{'ALL' if window is None else f'LAST_{window}'}"
            experiments[label] = []

    for min_games in (3, 4):
        elig = {s: [r for r in data[s] if eligible(r, min_games)] for s in DEFAULT_SEASONS}
        for test_season in VALIDATION_SEASONS:
            prior = [s for s in DEFAULT_SEASONS if s < test_season]
            if len(prior) < 4:
                continue
            test = elig[test_season]
            ref_train = [r for s in prior for r in elig[s]]
            if not ref_train or not test:
                continue
            ref_stats = prepare(ref_train)
            reference = score(fit(ref_stats, STABLE), test)

            for model_name, features in (("STABLE", STABLE), ("VOLUME", LEADING)):
                for window in WINDOWS:
                    if model_name == "STABLE" and window is None:
                        continue
                    selected = window_seasons(prior, window)
                    train = [r for s in selected for r in elig[s]]
                    if not train:
                        continue
                    stats = prepare(train)
                    q = score(fit(stats, features), test)
                    label = f"{model_name}_{'ALL' if window is None else f'LAST_{window}'}"
                    experiments[label].append({
                        "min_games": min_games,
                        "season": test_season,
                        "n": len(test),
                        "train_seasons": selected,
                        "dmae": q["mae"] - reference["mae"],
                        "drmse": q["rmse"] - reference["rmse"],
                        "dwin": (q["winner"] - reference["winner"]) * 100,
                    })

    ranked = []
    for name, rows in experiments.items():
        if not rows:
            continue
        s = summarize(rows)
        recent_rows = [r for r in rows if r["season"] >= 2023]
        older_rows = [r for r in rows if r["season"] <= 2022]
        ranked.append({
            "name": name,
            **s,
            "recent": summarize(recent_rows),
            "older": summarize(older_rows),
            "rows": rows,
        })
    ranked.sort(key=lambda x: (x["mae"], x["rmse"], -x["mae_wins"]))

    print("ROLLING TRAINING WINDOW — DECISION REPORT")
    print("Reference: STABLE_ALL = ITERATIVE + SRS + MWDR + MWDR x EXPECTED POSSESSIONS trained on all prior seasons")
    print("Windows use the last N available corpus seasons, not calendar-year subtraction.")
    print("Candidates: STABLE and STABLE + Volume Engine; windows = all, 8, 6, 4 prior seasons.")
    print("Negative MAE/RMSE is better; positive Winner pp is better.\n")

    print("RANKED ACROSS ALL 14 HOLDOUTS:")
    for i, x in enumerate(ranked, 1):
        print(
            f" {i}. {x['name']}: MAE {x['mae']:+.4f} | RMSE {x['rmse']:+.4f} | Winner {x['winner']:+.2f} pp | "
            f"MAE better {x['mae_wins']}/{x['n']} | RMSE better {x['rmse_wins']}/{x['n']} | 2023-25 MAE {x['recent']['mae']:+.4f}"
        )

    best = ranked[0]
    print(f"\nBEST: {best['name']}")
    print(f"OVERALL: MAE {best['mae']:+.4f} | RMSE {best['rmse']:+.4f} | Winner {best['winner']:+.2f} pp")
    print(f"2018-2022: MAE {best['older']['mae']:+.4f} | RMSE {best['older']['rmse']:+.4f} | Winner {best['older']['winner']:+.2f} pp")
    print(f"2023-2025: MAE {best['recent']['mae']:+.4f} | RMSE {best['recent']['rmse']:+.4f} | Winner {best['recent']['winner']:+.2f} pp")

    recent_ranked = sorted(ranked, key=lambda x: (x["recent"]["mae"], x["recent"]["rmse"]))
    print("\nBEST FOR 2023-2025:")
    for i, x in enumerate(recent_ranked[:3], 1):
        print(f" {i}. {x['name']}: MAE {x['recent']['mae']:+.4f} | RMSE {x['recent']['rmse']:+.4f} | Winner {x['recent']['winner']:+.2f} pp")

    best_holdout = min(best["rows"], key=lambda r: r["dmae"])
    worst_holdout = max(best["rows"], key=lambda r: r["dmae"])
    print(f"\nBEST HOLDOUT: min{best_holdout['min_games']} {best_holdout['season']} — MAE {best_holdout['dmae']:+.4f} | RMSE {best_holdout['drmse']:+.4f} | Winner {best_holdout['dwin']:+.2f} pp")
    print(f"WORST HOLDOUT: min{worst_holdout['min_games']} {worst_holdout['season']} — MAE {worst_holdout['dmae']:+.4f} | RMSE {worst_holdout['drmse']:+.4f} | Winner {worst_holdout['dwin']:+.2f} pp")


if __name__ == "__main__":
    main()

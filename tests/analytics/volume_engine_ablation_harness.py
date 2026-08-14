from pathlib import Path
import json, math

from cfb_analytics.analytics.football_mechanisms import orient_matchup
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES, SRS_FEATURES, eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS, TEST_SEASONS, _solve

BASE = tuple(ITERATIVE_FEATURES) + tuple(SRS_FEATURES)
MWDR = ("home_MWDR_OffenseEdge", "home_MWDR_DefenseEdge")
STABLE = BASE + MWDR + ("mwdrXExpectedPossessions",)
VOLUME = ("successVolumeEdge", "explosiveVolumeEdge", "turnoverVolumeEdge")
FULL = STABLE + VOLUME
INDEX = {k: i for i, k in enumerate(FULL)}


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
    print("Loading saved feature stores only; volume-engine ablation.")
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


def main():
    data = load_all()
    models = {
        "TURNOVER": STABLE + ("turnoverVolumeEdge",),
        "SUCCESS": STABLE + ("successVolumeEdge",),
        "EXPLOSIVE": STABLE + ("explosiveVolumeEdge",),
        "TURNOVER_SUCCESS": STABLE + ("turnoverVolumeEdge", "successVolumeEdge"),
        "TURNOVER_EXPLOSIVE": STABLE + ("turnoverVolumeEdge", "explosiveVolumeEdge"),
        "SUCCESS_EXPLOSIVE": STABLE + ("successVolumeEdge", "explosiveVolumeEdge"),
        "ALL_THREE": STABLE + VOLUME,
    }
    results = {name: [] for name in models}
    stable_results = []

    for min_games in (3, 4):
        elig = {s: [r for r in data[s] if eligible(r, min_games)] for s in DEFAULT_SEASONS}
        for test_season in TEST_SEASONS:
            train = [r for s in DEFAULT_SEASONS if s < test_season for r in elig[s]]
            test = elig[test_season]
            stats = prepare(train)
            st = score(fit(stats, STABLE), test)
            stable_results.append((min_games, test_season, st, len(test)))
            for name, features in models.items():
                q = score(fit(stats, features), test)
                results[name].append((min_games, test_season, q, st, len(test)))

    ranked = []
    for name, rows in results.items():
        dmae = [q["mae"] - st["mae"] for _, _, q, st, _ in rows]
        drmse = [q["rmse"] - st["rmse"] for _, _, q, st, _ in rows]
        dwin = [(q["winner"] - st["winner"]) * 100 for _, _, q, st, _ in rows]
        ranked.append({
            "name": name,
            "mae": sum(dmae) / len(dmae),
            "rmse": sum(drmse) / len(drmse),
            "winner": sum(dwin) / len(dwin),
            "mae_wins": sum(x < 0 for x in dmae),
            "rmse_wins": sum(x < 0 for x in drmse),
            "rows": rows,
        })
    ranked.sort(key=lambda x: (x["mae"], x["rmse"], -x["mae_wins"]))

    print("VOLUME ENGINE — SIX-HOLDOUT DECISION REPORT")
    print("Benchmark: CURRENT_STABLE = ITERATIVE + SRS + MWDR + MWDR x EXPECTED POSSESSIONS")
    print("Ranking combines 2023-2025 at minimum-prior-games 3 and 4.")
    print("Negative MAE/RMSE is better; positive Winner pp is better.\n")
    for i, x in enumerate(ranked, 1):
        print(f" {i}. {x['name']}: MAE {x['mae']:+.4f} | RMSE {x['rmse']:+.4f} | Winner {x['winner']:+.2f} pp | MAE better {x['mae_wins']}/6 | RMSE better {x['rmse_wins']}/6")

    best = ranked[0]
    print(f"\nBEST: {best['name']}")
    print("HOLDOUT CHECK:")
    for min_games, season, q, st, n in best["rows"]:
        print(f" min{min_games} {season}: MAE {q['mae']-st['mae']:+.3f} | RMSE {q['rmse']-st['rmse']:+.3f} | Winner {(q['winner']-st['winner'])*100:+.2f} pp | n={n}")


if __name__ == "__main__":
    main()

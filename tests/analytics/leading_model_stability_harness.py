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
    print("Loading saved feature stores only; leading-model stability validation.")
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


def summarize(rows):
    dmae = [r["dmae"] for r in rows]
    drmse = [r["drmse"] for r in rows]
    dwin = [r["dwin"] for r in rows]
    return {
        "mae": sum(dmae) / len(dmae),
        "rmse": sum(drmse) / len(drmse),
        "winner": sum(dwin) / len(dwin),
        "mae_wins": sum(x < 0 for x in dmae),
        "rmse_wins": sum(x < 0 for x in drmse),
        "winner_wins": sum(x > 0 for x in dwin),
        "n": len(rows),
    }


def main():
    data = load_all()
    holdouts = []

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
            stats = prepare(train)
            stable = score(fit(stats, STABLE), test)
            leading = score(fit(stats, LEADING), test)
            holdouts.append({
                "min_games": min_games,
                "season": test_season,
                "n": len(test),
                "dmae": leading["mae"] - stable["mae"],
                "drmse": leading["rmse"] - stable["rmse"],
                "dwin": (leading["winner"] - stable["winner"]) * 100,
            })

    overall = summarize(holdouts)
    older = summarize([r for r in holdouts if r["season"] <= 2022])
    recent = summarize([r for r in holdouts if r["season"] >= 2023])
    worst = max(holdouts, key=lambda r: r["dmae"])
    best = min(holdouts, key=lambda r: r["dmae"])

    print("LEADING MODEL — HISTORICAL STABILITY REPORT")
    print("Benchmark: STABLE = ITERATIVE + SRS + MWDR + MWDR x EXPECTED POSSESSIONS")
    print("Candidate: STABLE + SUCCESS/EXPLOSIVE/TURNOVER x EXPECTED POSSESSIONS")
    print(f"Expanding-window holdouts: {', '.join(map(str, VALIDATION_SEASONS))}; min-games 3 and 4")
    print("Negative MAE/RMSE is better; positive Winner pp is better.\n")

    print(f"OVERALL ({overall['n']} holdouts): MAE {overall['mae']:+.4f} | RMSE {overall['rmse']:+.4f} | Winner {overall['winner']:+.2f} pp | MAE better {overall['mae_wins']}/{overall['n']} | RMSE better {overall['rmse_wins']}/{overall['n']}")
    print(f"2018-2022: MAE {older['mae']:+.4f} | RMSE {older['rmse']:+.4f} | Winner {older['winner']:+.2f} pp | MAE better {older['mae_wins']}/{older['n']} | RMSE better {older['rmse_wins']}/{older['n']}")
    print(f"2023-2025: MAE {recent['mae']:+.4f} | RMSE {recent['rmse']:+.4f} | Winner {recent['winner']:+.2f} pp | MAE better {recent['mae_wins']}/{recent['n']} | RMSE better {recent['rmse_wins']}/{recent['n']}")

    print(f"\nBEST HOLDOUT: min{best['min_games']} {best['season']} — MAE {best['dmae']:+.4f} | RMSE {best['drmse']:+.4f} | Winner {best['dwin']:+.2f} pp | n={best['n']}")
    print(f"WORST HOLDOUT: min{worst['min_games']} {worst['season']} — MAE {worst['dmae']:+.4f} | RMSE {worst['drmse']:+.4f} | Winner {worst['dwin']:+.2f} pp | n={worst['n']}")

    verdict = "KEEP" if overall["mae"] < 0 and overall["mae_wins"] >= 9 and overall["rmse"] <= 0 else "REVIEW"
    print(f"\nVERDICT: {verdict}")
    print("HOLDOUTS:")
    for r in holdouts:
        print(f" min{r['min_games']} {r['season']}: MAE {r['dmae']:+.4f} | RMSE {r['drmse']:+.4f} | Winner {r['dwin']:+.2f} pp | n={r['n']}")


if __name__ == "__main__":
    main()

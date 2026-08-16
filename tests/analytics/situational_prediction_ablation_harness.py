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
PREDICTION_V1 = STABLE + VOLUME

SITUATIONAL_SPECS = {
    "earlyDownSuccessEdge": ("early_down", "successRate", "plays", 50),
    "thirdShortConversionEdge": ("third_short", "conversionRate", "conversionAttempts", 10),
    "thirdMediumConversionEdge": ("third_medium", "conversionRate", "conversionAttempts", 10),
    "thirdLongConversionEdge": ("third_long", "conversionRate", "conversionAttempts", 10),
    "redZoneSuccessEdge": ("red_zone", "successRate", "plays", 20),
    "secondHalfSuccessEdge": ("second_half", "successRate", "plays", 40),
}
SITUATIONAL = tuple(SITUATIONAL_SPECS)
FULL = PREDICTION_V1 + SITUATIONAL
INDEX = {k: i for i, k in enumerate(FULL)}


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def add_volume_features(r, x):
    z = {**r, **x}
    poss = z.get("expectedPossessionsPerTeam")
    mwdr = (float(z[MWDR[0]]) + float(z[MWDR[1]])) if finite(z.get(MWDR[0])) and finite(z.get(MWDR[1])) else None
    z["mwdrXExpectedPossessions"] = mwdr * float(poss) if finite(mwdr) and finite(poss) else None
    z["successVolumeEdge"] = float(z["netSuccessRateEdge"]) * float(poss) if finite(z.get("netSuccessRateEdge")) and finite(poss) else None
    z["explosiveVolumeEdge"] = float(z["netExplosiveRateEdge"]) * float(poss) if finite(z.get("netExplosiveRateEdge")) and finite(poss) else None
    z["turnoverVolumeEdge"] = float(z["netTurnoverPressureEdge"]) * float(poss) if finite(z.get("netTurnoverPressureEdge")) and finite(poss) else None
    return z


def load_situational_index(processed_root, season):
    path = processed_root / "derived" / "situational_pregame" / f"season={season}" / "states.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing situational pregame states for {season}. Run: "
            "python -m cfb_analytics.analytics.situational_pregame --all"
        )
    rows = json.loads(path.read_text())
    return {
        (
            str(r.get("seasonType")),
            int(r.get("week")),
            str(r.get("team")),
            str(r.get("side")),
            str(r.get("bucket")),
        ): r
        for r in rows
    }


def matchup_situational_edge(index, game, bucket, metric, denom, minimum):
    key0 = (str(game.get("seasonType")), int(game.get("week")))
    home = str(game.get("homeTeam"))
    away = str(game.get("awayTeam"))
    ho = index.get(key0 + (home, "offense", bucket))
    hd = index.get(key0 + (home, "defense", bucket))
    ao = index.get(key0 + (away, "offense", bucket))
    ad = index.get(key0 + (away, "defense", bucket))
    states = (ho, hd, ao, ad)
    if any(s is None for s in states):
        return None
    if any(float(s.get(denom) or 0) < minimum for s in states):
        return None
    vals = [s.get(metric) for s in states]
    if not all(finite(v) for v in vals):
        return None

    # Expected home performance = average of home offense and away defense allowed.
    # Expected away performance = average of away offense and home defense allowed.
    # Positive values therefore always favor the home team.
    home_expected = (float(ho[metric]) + float(ad[metric])) / 2.0
    away_expected = (float(ao[metric]) + float(hd[metric])) / 2.0
    return home_expected - away_expected


def add_situational_features(row, index):
    z = dict(row)
    for feature, (bucket, metric, denom, minimum) in SITUATIONAL_SPECS.items():
        z[feature] = matchup_situational_edge(index, z, bucket, metric, denom, minimum)
    return z


def load_all():
    pr = Path("data/processed")
    data = {}
    print("Loading saved feature stores + saved situational pregame states only.")
    for season in DEFAULT_SEASONS:
        base = load_saved_feature_store(pr, season)
        mech_path = pr / "derived" / "football_mechanisms" / f"season={season}" / "matchups.json"
        if not mech_path.exists():
            raise FileNotFoundError(
                f"Missing football mechanisms for {season}. Run: "
                "python -m cfb_analytics.analytics.football_mechanisms --all"
            )
        match = {str(q.get("gameId")): q for q in json.loads(mech_path.read_text())}
        sit = load_situational_index(pr, season)
        rows = []
        for r in base:
            m = match.get(str(r.get("gameId")))
            if not m:
                continue
            x = orient_matchup(m, r.get("homeTeam"), r.get("awayTeam"))
            if x is None:
                continue
            z = add_volume_features(r, x)
            rows.append(add_situational_features(z, sit))
        data[season] = rows
        complete = sum(all(finite(r.get(k)) for k in SITUATIONAL) for r in rows)
        print(f" {season}: rows={len(rows):,} | complete situational={complete:,}")
    return data


def eligible(r, min_games):
    return (
        eligible_iterative_row(r, min_games)
        and all(finite(r.get(k)) for k in PREDICTION_V1)
        and all(finite(r.get(k)) for k in SITUATIONAL)
        and finite(r.get("target_margin"))
        and r.get("target_homeWin") is not None
    )


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
    models = {name: PREDICTION_V1 + (name,) for name in SITUATIONAL}
    models["ALL_SITUATIONAL"] = PREDICTION_V1 + SITUATIONAL
    results = {name: [] for name in models}

    print("\nSITUATIONAL PREDICTION — SIX-HOLDOUT DECISION REPORT")
    print("Benchmark: locked Prediction v1 (VOLUME + OLS)")
    print("Common sample: benchmark and challenger use identical rows with all six situational features available.")
    print("Holdouts: 2023-2025 at minimum-prior-games 3 and 4.")
    print("Negative MAE/RMSE delta is better; positive Winner pp is better.\n")

    for min_games in (3, 4):
        elig = {s: [r for r in data[s] if eligible(r, min_games)] for s in DEFAULT_SEASONS}
        for test_season in TEST_SEASONS:
            train = [r for s in DEFAULT_SEASONS if s < test_season for r in elig[s]]
            test = elig[test_season]
            if not train or not test:
                raise RuntimeError(f"No common-sample rows for min{min_games} holdout {test_season}")
            stats = prepare(train)
            benchmark = score(fit(stats, PREDICTION_V1), test)
            for name, features in models.items():
                challenger = score(fit(stats, features), test)
                results[name].append((min_games, test_season, challenger, benchmark, len(test), len(train)))

    ranked = []
    for name, rows in results.items():
        dmae = [q["mae"] - b["mae"] for _, _, q, b, _, _ in rows]
        drmse = [q["rmse"] - b["rmse"] for _, _, q, b, _, _ in rows]
        dwin = [(q["winner"] - b["winner"]) * 100 for _, _, q, b, _, _ in rows]
        ranked.append({
            "name": name,
            "mae": sum(dmae) / len(dmae),
            "rmse": sum(drmse) / len(drmse),
            "winner": sum(dwin) / len(dwin),
            "mae_wins": sum(x < 0 for x in dmae),
            "rmse_wins": sum(x < 0 for x in drmse),
            "winner_wins": sum(x > 0 for x in dwin),
            "rows": rows,
        })
    ranked.sort(key=lambda x: (x["mae"], x["rmse"], -x["mae_wins"]))

    for i, x in enumerate(ranked, 1):
        print(
            f" {i}. {x['name']}: MAE {x['mae']:+.4f} | RMSE {x['rmse']:+.4f} | "
            f"Winner {x['winner']:+.2f} pp | MAE better {x['mae_wins']}/6 | "
            f"RMSE better {x['rmse_wins']}/6 | Winner better {x['winner_wins']}/6"
        )

    all_result = next(x for x in ranked if x["name"] == "ALL_SITUATIONAL")
    print("\nALL_SITUATIONAL HOLDOUT CHECK:")
    for min_games, season, q, b, n, train_n in all_result["rows"]:
        print(
            f" min{min_games} {season}: MAE {q['mae']:.3f} ({q['mae']-b['mae']:+.3f}) | "
            f"RMSE {q['rmse']:.3f} ({q['rmse']-b['rmse']:+.3f}) | "
            f"Winner {q['winner']*100:.2f}% ({(q['winner']-b['winner'])*100:+.2f} pp) | "
            f"test n={n} | train n={train_n}"
        )


if __name__ == "__main__":
    main()

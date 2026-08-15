from pathlib import Path
import json, math

try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:
    raise SystemExit('Missing research model dependencies. Run: pip install -e ".[models]"') from exc

from cfb_analytics.analytics.drive_ppd import orient_matchup_ppd
from cfb_analytics.analytics.football_mechanisms import orient_matchup
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES, SRS_FEATURES, eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

BASE = tuple(ITERATIVE_FEATURES) + tuple(SRS_FEATURES)
MWDR = ("home_MWDR_OffenseEdge", "home_MWDR_DefenseEdge")
STABLE = BASE + MWDR + ("mwdrXExpectedPossessions",)
VOLUME = ("successVolumeEdge", "explosiveVolumeEdge", "turnoverVolumeEdge")
CURRENT = STABLE + VOLUME
PPD_COMPONENTS = ("homeExpectedOffensivePPD", "awayExpectedOffensivePPD")
PPD_EDGE = ("expectedPPDEdge",)
PPD_PROJECTED = ("ppdProjectedMargin",)
VALIDATION_SEASONS = tuple(s for s in DEFAULT_SEASONS if s >= 2018)

MODELS = {
    "CURRENT_VOLUME_OLS": CURRENT,
    "STABLE_PLUS_PPD_EDGE": STABLE + PPD_EDGE,
    "STABLE_PLUS_PPD_PROJECTED": STABLE + PPD_PROJECTED,
    "VOLUME_PLUS_PPD_EDGE": CURRENT + PPD_EDGE,
    "VOLUME_PLUS_PPD_COMPONENTS": CURRENT + PPD_COMPONENTS,
    "VOLUME_PLUS_PPD_PROJECTED": CURRENT + PPD_PROJECTED,
    "VOLUME_PLUS_PPD_ALL": CURRENT + PPD_COMPONENTS + PPD_PROJECTED,
}
ALL_FEATURES = tuple(dict.fromkeys(k for features in MODELS.values() for k in features))


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def add_features(row, mechanisms, ppd):
    z = {**row, **mechanisms, **ppd}
    poss = z.get("expectedPossessionsPerTeam")
    mwdr = (
        float(z[MWDR[0]]) + float(z[MWDR[1]])
        if finite(z.get(MWDR[0])) and finite(z.get(MWDR[1]))
        else None
    )
    z["mwdrXExpectedPossessions"] = mwdr * float(poss) if finite(mwdr) and finite(poss) else None
    z["successVolumeEdge"] = float(z["netSuccessRateEdge"]) * float(poss) if finite(z.get("netSuccessRateEdge")) and finite(poss) else None
    z["explosiveVolumeEdge"] = float(z["netExplosiveRateEdge"]) * float(poss) if finite(z.get("netExplosiveRateEdge")) and finite(poss) else None
    z["turnoverVolumeEdge"] = float(z["netTurnoverPressureEdge"]) * float(poss) if finite(z.get("netTurnoverPressureEdge")) and finite(poss) else None
    z["ppdProjectedMargin"] = float(z["expectedPPDEdge"]) * float(poss) if finite(z.get("expectedPPDEdge")) and finite(poss) else None
    return z


def load_all():
    processed = Path("data/processed")
    data = {}
    print("Loading saved feature stores + football mechanisms + drive PPD; drive-PPD ablation.")
    for season in DEFAULT_SEASONS:
        base = load_saved_feature_store(processed, season)
        mech_path = processed / "derived" / "football_mechanisms" / f"season={season}" / "matchups.json"
        ppd_path = processed / "derived" / "drive_ppd" / f"season={season}" / "matchups.json"
        if not mech_path.exists():
            raise FileNotFoundError(f"Missing football mechanisms for {season}. Run: python -m cfb_analytics.analytics.football_mechanisms --all")
        if not ppd_path.exists():
            raise FileNotFoundError(f"Missing drive PPD for {season}. Run: python -m cfb_analytics.analytics.drive_ppd --all")
        mechanisms = {str(r.get("gameId")): r for r in json.loads(mech_path.read_text())}
        ppd_matchups = {str(r.get("gameId")): r for r in json.loads(ppd_path.read_text())}
        rows = []
        for row in base:
            gid = str(row.get("gameId"))
            m = mechanisms.get(gid)
            p = ppd_matchups.get(gid)
            if not m or not p:
                continue
            mx = orient_matchup(m, row.get("homeTeam"), row.get("awayTeam"))
            px = orient_matchup_ppd(p, row.get("homeTeam"), row.get("awayTeam"))
            if mx is not None and px is not None:
                rows.append(add_features(row, mx, px))
        data[season] = rows
    return data


def eligible(row, min_games):
    return eligible_iterative_row(row, min_games) and all(finite(row.get(k)) for k in ALL_FEATURES)


def xy(rows, features):
    x = np.asarray([[float(r[k]) for k in features] for r in rows], dtype=float)
    y = np.asarray([float(r["target_margin"]) for r in rows], dtype=float)
    wins = np.asarray([bool(r["target_homeWin"]) for r in rows], dtype=bool)
    return x, y, wins


def model():
    return make_pipeline(StandardScaler(), LinearRegression())


def score(pred, y, wins):
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
    results = {name: [] for name in MODELS if name != "CURRENT_VOLUME_OLS"}

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

            xtr, ytr, _ = xy(train, CURRENT)
            xte, yte, wins = xy(test, CURRENT)
            ref = model()
            ref.fit(xtr, ytr)
            ref_score = score(ref.predict(xte), yte, wins)

            for name, features in MODELS.items():
                if name == "CURRENT_VOLUME_OLS":
                    continue
                xtr, ytr, _ = xy(train, features)
                xte, yte, wins = xy(test, features)
                candidate = model()
                candidate.fit(xtr, ytr)
                q = score(candidate.predict(xte), yte, wins)
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
            "latest_mae": latest["mae"],
            "latest_rmse": latest["rmse"],
            "rows": rows,
        })
    ranked.sort(key=lambda r: (r["mae"], r["rmse"], -r["mae_wins"]))
    recent_ranked = sorted(ranked, key=lambda r: (r["recent_mae"], r["recent_rmse"]))
    latest_ranked = sorted(ranked, key=lambda r: (r["latest_mae"], r["latest_rmse"]))

    print("DRIVE PPD MODEL — DECISION REPORT")
    print("Reference: CURRENT_VOLUME_OLS")
    print("Drive PPD is opponent-adjusted from validated, score-resolved offensive possessions only.")
    print("Projected margin = expected PPD edge x expected possessions per team.")
    print("Negative MAE/RMSE is better; positive Winner pp is better.\n")

    print("RANKED ACROSS ALL HOLDOUTS:")
    for i, r in enumerate(ranked, 1):
        print(
            f" {i}. {r['name']}: MAE {r['mae']:+.4f} | RMSE {r['rmse']:+.4f} | "
            f"Winner {r['winner']:+.2f} pp | MAE better {r['mae_wins']}/{r['n']} | "
            f"RMSE better {r['rmse_wins']}/{r['n']} | 2023-25 MAE {r['recent_mae']:+.4f} | "
            f"2024-25 MAE {r['latest_mae']:+.4f}"
        )

    best = ranked[0]
    print(f"\nBEST OVERALL: {best['name']}")
    print(f"BEST 2023-2025: {recent_ranked[0]['name']} — MAE {recent_ranked[0]['recent_mae']:+.4f} | RMSE {recent_ranked[0]['recent_rmse']:+.4f}")
    print(f"BEST 2024-2025: {latest_ranked[0]['name']} — MAE {latest_ranked[0]['latest_mae']:+.4f} | RMSE {latest_ranked[0]['latest_rmse']:+.4f}")

    print("\nBEST HOLDOUT CHECK:")
    for r in best["rows"]:
        print(
            f" min{r['min_games']} {r['season']}: MAE {r['dmae']:+.4f} | RMSE {r['drmse']:+.4f} | "
            f"Winner {r['dwin']:+.2f} pp | n={r['n']}"
        )


if __name__ == "__main__":
    main()

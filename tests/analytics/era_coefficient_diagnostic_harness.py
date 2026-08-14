from pathlib import Path
import json, math

from cfb_analytics.analytics.football_mechanisms import orient_matchup
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES, SRS_FEATURES, eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS, _solve

BASE = tuple(ITERATIVE_FEATURES) + tuple(SRS_FEATURES)
MWDR = ("home_MWDR_OffenseEdge", "home_MWDR_DefenseEdge")
KEY = (
    "home_MWDR_OffenseEdge",
    "home_MWDR_DefenseEdge",
    "mwdrXExpectedPossessions",
    "successVolumeEdge",
    "explosiveVolumeEdge",
    "turnoverVolumeEdge",
)
FULL = BASE + MWDR + (
    "mwdrXExpectedPossessions",
    "successVolumeEdge",
    "explosiveVolumeEdge",
    "turnoverVolumeEdge",
)
INDEX = {k: i for i, k in enumerate(FULL)}
OLD_SEASONS = tuple(s for s in DEFAULT_SEASONS if 2014 <= s <= 2019)
MODERN_SEASONS = tuple(s for s in DEFAULT_SEASONS if 2021 <= s <= 2025)


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
    print("Loading saved feature stores only; era coefficient diagnostic.")
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


def fit(rows, ridge=1e-6):
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
    for i in range(1, p):
        xtx[i][i] += ridge
    w = _solve(xtx, xty)
    if w is None:
        raise ValueError("singular model")
    return {k: w[INDEX[k] + 1] for k in KEY}


def sign(v, eps=0.02):
    if abs(v) < eps:
        return "0"
    return "+" if v > 0 else "-"


def mean(values):
    return sum(values) / len(values)


def main():
    data = load_all()
    print("ERA COEFFICIENT DIAGNOSTIC")
    print("Model: ITERATIVE + SRS + MWDR + MWDR x possessions + Success/Explosive/Turnover x possessions")
    print("Coefficients are standardized-feature OLS coefficients in point-margin units.")
    print("This is a structural diagnostic, not a predictive model-selection test.\n")

    pooled = {}
    seasonal = {k: [] for k in KEY}

    for min_games in (3, 4):
        elig = {s: [r for r in data[s] if eligible(r, min_games)] for s in DEFAULT_SEASONS}
        for era_name, seasons in (("OLD_2014_2019", OLD_SEASONS), ("MODERN_2021_2025", MODERN_SEASONS)):
            rows = [r for s in seasons for r in elig[s]]
            pooled[(min_games, era_name)] = (fit(rows), len(rows))
        for season in DEFAULT_SEASONS:
            rows = elig[season]
            if rows:
                coef = fit(rows)
                for k in KEY:
                    seasonal[k].append((min_games, season, coef[k]))

    print("POOLED ERA COMPARISON:")
    for k in KEY:
        old3 = pooled[(3, "OLD_2014_2019")][0][k]
        mod3 = pooled[(3, "MODERN_2021_2025")][0][k]
        old4 = pooled[(4, "OLD_2014_2019")][0][k]
        mod4 = pooled[(4, "MODERN_2021_2025")][0][k]
        old_avg = mean([old3, old4])
        mod_avg = mean([mod3, mod4])
        print(f" {k}: OLD {old_avg:+.3f} | MODERN {mod_avg:+.3f} | SHIFT {mod_avg-old_avg:+.3f} | signs {sign(old_avg)}->{sign(mod_avg)}")

    print("\nVOLUME STABILITY BY ERA:")
    for k in ("successVolumeEdge", "explosiveVolumeEdge", "turnoverVolumeEdge"):
        vals = seasonal[k]
        for era_name, seasons in (("OLD", set(OLD_SEASONS)), ("MODERN", set(MODERN_SEASONS))):
            xs = [v for _, s, v in vals if s in seasons]
            pos = sum(v > 0.02 for v in xs)
            neg = sum(v < -0.02 for v in xs)
            near = len(xs) - pos - neg
            print(f" {k} {era_name}: mean {mean(xs):+.3f} | positive {pos}/{len(xs)} | negative {neg}/{len(xs)} | near-zero {near}/{len(xs)}")

    print("\nMODERN YEAR CHECK (average of min3/min4 coefficients):")
    for season in MODERN_SEASONS:
        parts = []
        for k in KEY:
            xs = [v for mg, s, v in seasonal[k] if s == season]
            parts.append(f"{k}={mean(xs):+.3f}")
        print(f" {season}: " + " | ".join(parts))

    old_n3 = pooled[(3, "OLD_2014_2019")][1]
    mod_n3 = pooled[(3, "MODERN_2021_2025")][1]
    old_n4 = pooled[(4, "OLD_2014_2019")][1]
    mod_n4 = pooled[(4, "MODERN_2021_2025")][1]
    print(f"\nSAMPLES: old min3={old_n3:,}, modern min3={mod_n3:,}, old min4={old_n4:,}, modern min4={mod_n4:,}")
    print("INTERPRETATION: prioritize sign consistency and repeated modern-era magnitude; do not promote a feature from coefficient size alone.")


if __name__ == "__main__":
    main()

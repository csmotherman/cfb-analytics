"""Beat the Model live scheduler v3 market rules.

This is a narrow production override on top of the v2 live scheduler.  It fixes
CFBD spread interpretation and makes market closeness the first slate-selection
criterion while preserving the core fairness contract: Prediction-v2 output is
never used to choose its own opponents.

CFBD's numeric ``spread`` is home-team oriented: a positive spread means the away
team is favored and a negative spread means the home team is favored.  We use
paired no-vig moneyline probability when available; otherwise the signed spread
determines the market favorite.  The absolute spread is used only as a matchup-
closeness signal.
"""
from __future__ import annotations

import math
from statistics import median
from typing import Any

from cfb_analytics.analytics import publish_beat_the_model_schedule as base

LIVE_SCHEDULE_VERSION = "beat-the-model-live-schedule-v3"
LIVE_SLATE_SELECTION_VERSION = "btm-close-ranked-market-matchups-v3"
MARKET_SOURCE_VERSION = "cfbd-lines-consensus-v2"

PICKEM_MAX_SPREAD = 3.5
CLOSE_MAX_SPREAD = 7.5
COMPETITIVE_MAX_SPREAD = 10.5
MAX_PREFERRED_SPREAD = 14.0


def _finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _median_finite(values: list[Any]) -> float | None:
    cleaned = [float(value) for value in values if _finite(value)]
    return float(median(cleaned)) if cleaned else None


def _american_implied_probability(odds: Any) -> float | None:
    if not _finite(odds):
        return None
    value = float(odds)
    if value < 0:
        return -value / (-value + 100.0)
    if value > 0:
        return 100.0 / (value + 100.0)
    return None


def market_consensus(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Reduce one CFBD BettingGame into a stable, correctly oriented consensus."""
    gid = raw.get("id", raw.get("gameId"))
    home = raw.get("homeTeam", raw.get("home_team"))
    away = raw.get("awayTeam", raw.get("away_team"))
    lines = raw.get("lines")
    if gid is None or not home or not away or not isinstance(lines, list):
        return None

    home_name = str(home)
    away_name = str(away)
    spreads: list[float] = []
    home_moneylines: list[float] = []
    away_moneylines: list[float] = []
    home_no_vig_probabilities: list[float] = []
    providers: set[str] = set()

    for line in lines:
        if not isinstance(line, dict):
            continue

        provider = line.get("provider")
        if isinstance(provider, str) and provider.strip():
            providers.add(provider.strip())
        elif isinstance(provider, dict):
            provider_name = provider.get("name")
            if isinstance(provider_name, str) and provider_name.strip():
                providers.add(provider_name.strip())

        spread = line.get("spread")
        if _finite(spread):
            spreads.append(float(spread))

        home_ml = line.get("homeMoneyline", line.get("home_moneyline"))
        away_ml = line.get("awayMoneyline", line.get("away_moneyline"))
        if _finite(home_ml):
            home_moneylines.append(float(home_ml))
        if _finite(away_ml):
            away_moneylines.append(float(away_ml))

        home_implied = _american_implied_probability(home_ml)
        away_implied = _american_implied_probability(away_ml)
        if home_implied is not None and away_implied is not None:
            total = home_implied + away_implied
            if total > 0:
                home_no_vig_probabilities.append(home_implied / total)

    provider_count = len(providers) if providers else sum(isinstance(line, dict) for line in lines)
    if provider_count == 0:
        return None

    signed_spread = _median_finite(spreads)
    market_spread = abs(signed_spread) if signed_spread is not None else None
    home_probability = _median_finite(home_no_vig_probabilities)
    away_probability = 1.0 - home_probability if home_probability is not None else None

    favorite: str | None = None
    if home_probability is not None:
        if home_probability > 0.5000001:
            favorite = home_name
        elif home_probability < 0.4999999:
            favorite = away_name

    # CFBD spread is home-team oriented.  Positive => home is getting points =>
    # away favorite. Negative => home favorite. Do not infer the favorite merely
    # from the team name appearing in formattedSpread; that can be the underdog.
    if favorite is None and signed_spread is not None:
        if signed_spread > 0.001:
            favorite = away_name
        elif signed_spread < -0.001:
            favorite = home_name

    if market_spread is not None and market_spread <= 0.001:
        line_label = "Pick'em"
    elif market_spread is not None and favorite:
        line_label = f"{favorite} -{market_spread:g}"
    elif favorite:
        line_label = f"{favorite} favored"
    elif market_spread is not None:
        line_label = f"Consensus spread {market_spread:g}"
    else:
        line_label = "Market available"

    return {
        "marketSource": MARKET_SOURCE_VERSION,
        "marketProviderCount": int(provider_count),
        "marketSpread": market_spread,
        "marketFavorite": favorite,
        "marketLine": line_label,
        "marketHomeMoneyline": _median_finite(home_moneylines),
        "marketAwayMoneyline": _median_finite(away_moneylines),
        "marketHomeWinProbability": home_probability,
        "marketAwayWinProbability": away_probability,
    }


def selection_tier(home_rank: int, away_rank: int, market: dict[str, Any] | None) -> int:
    """Market closeness first; BTM quality decides among similarly close games."""
    spread = market.get("marketSpread") if market else None
    if _finite(spread):
        value = float(spread)
        if value <= PICKEM_MAX_SPREAD:
            return 0
        if value <= CLOSE_MAX_SPREAD:
            return 1
        if value <= COMPETITIVE_MAX_SPREAD:
            return 2
        if value <= MAX_PREFERRED_SPREAD:
            return 3
        return 5

    # Missing lines should not outrank known competitive games, but a genuinely
    # strong close-ranked matchup can still beat a known major mismatch.
    worst_rank = max(int(home_rank), int(away_rank))
    rank_gap = abs(int(home_rank) - int(away_rank))
    if worst_rank <= 40 and rank_gap <= 15:
        return 4
    return 6


def selection_score(home_rank: int, away_rank: int, market: dict[str, Any] | None) -> float:
    """Within a closeness tier, reward stronger teams and smaller rank gaps."""
    average_rank = (int(home_rank) + int(away_rank)) / 2.0
    rank_gap = abs(int(home_rank) - int(away_rank))
    spread = market.get("marketSpread") if market else None
    spread_penalty = float(spread) if _finite(spread) else MAX_PREFERRED_SPREAD
    return average_rank + 0.35 * rank_gap + 0.35 * spread_penalty


def install() -> None:
    """Install the v3 market/selection contract into the stable publisher shell."""
    base.LIVE_SCHEDULE_VERSION = LIVE_SCHEDULE_VERSION
    base.LIVE_SLATE_SELECTION_VERSION = LIVE_SLATE_SELECTION_VERSION
    base.MARKET_SOURCE_VERSION = MARKET_SOURCE_VERSION
    base.market_consensus = market_consensus
    base._selection_tier = selection_tier
    base._selection_score = selection_score

    # Keep the payload's human-readable threshold metadata aligned as closely as
    # possible with the v3 tiers used by the actual selector.
    base.ELITE_MAX_WORST_RANK = 999
    base.ELITE_MAX_RANK_GAP = 999
    base.ELITE_MAX_MARKET_SPREAD = PICKEM_MAX_SPREAD
    base.STRONG_MAX_WORST_RANK = 999
    base.STRONG_MAX_RANK_GAP = 999
    base.STRONG_MAX_MARKET_SPREAD = CLOSE_MAX_SPREAD
    base.COMPETITIVE_MAX_WORST_RANK = 999
    base.COMPETITIVE_MAX_MARKET_SPREAD = COMPETITIVE_MAX_SPREAD


install()


def main() -> None:
    base.main()


if __name__ == "__main__":
    main()

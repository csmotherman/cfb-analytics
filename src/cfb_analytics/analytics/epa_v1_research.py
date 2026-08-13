"""Independent Expected Points / EPA v1 research model.

This module deliberately does not use CFBD ``ppa`` for training. PPA is an
external benchmark only.

EPA v1 research scope:
- regulation only (periods 1-4)
- state = down, distance, yards to goal, seconds remaining in half
- target = realized net points for the current offense from the recorded state
  through the end of the half
- expected points = hierarchical empirical mean with minimum-sample backoff
- play EPA = scoreboard change + signed next-state EP - current-state EP

Score timing (whether a play row describes the state before or after the play)
must be audited from the local corpus before play-level PPA comparison is trusted.
"""
from __future__ import annotations
from collections import defaultdict
from math import sqrt
from typing import Any

from cfb_analytics.raw.sequence import _candidate_sort_key

EPA_RESEARCH_VERSION = "epa-v1-research-empirical"


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def clock_seconds(clock: Any) -> int | None:
    if isinstance(clock, dict):
        m, s = clock.get("minutes"), clock.get("seconds")
        if _num(m) and _num(s):
            return int(m) * 60 + int(s)
    if isinstance(clock, str) and ":" in clock:
        try:
            m, s = clock.split(":", 1)
            return int(m) * 60 + int(float(s))
        except ValueError:
            return None
    return None


def seconds_remaining_in_half(play: dict[str, Any]) -> int | None:
    period = play.get("period")
    c = clock_seconds(play.get("clock"))
    if period not in (1, 2, 3, 4) or c is None or c < 0 or c > 900:
        return None
    return c + (900 if period in (1, 3) else 0)


def half_number(play: dict[str, Any]) -> int | None:
    p = play.get("period")
    if p in (1, 2):
        return 1
    if p in (3, 4):
        return 2
    return None


def oriented_score(play: dict[str, Any]) -> tuple[float, float] | None:
    offense, home, away = play.get("offense"), play.get("home"), play.get("away")
    os, ds = play.get("offenseScore"), play.get("defenseScore")
    if not (_num(os) and _num(ds) and offense and home and away):
        return None
    if offense == home:
        return float(os), float(ds)
    if offense == away:
        return float(ds), float(os)
    return None


def state_eligible(play: dict[str, Any]) -> bool:
    if half_number(play) is None or seconds_remaining_in_half(play) is None:
        return False
    d, dist, ytg = play.get("down"), play.get("distance"), play.get("yardsToGoal")
    return d in (1, 2, 3, 4) and _num(dist) and dist >= 0 and _num(ytg) and 0 <= ytg <= 100 and bool(play.get("offense")) and oriented_score(play) is not None


def _distance_bucket(v: float) -> int:
    if v <= 1: return 1
    if v <= 3: return 3
    if v <= 6: return 6
    if v <= 10: return 10
    return 11


def _bucket(v: float, width: int) -> int:
    return int(v // width) * width


def state_keys(play: dict[str, Any]) -> list[tuple[Any, ...]]:
    sec = seconds_remaining_in_half(play)
    down, dist, ytg = int(play["down"]), float(play["distance"]), float(play["yardsToGoal"])
    db = _distance_bucket(dist)
    return [
        ("exact", down, db, _bucket(ytg, 5), _bucket(sec, 120)),
        ("coarse", down, db, _bucket(ytg, 10), _bucket(sec, 300)),
        ("field", down, db, _bucket(ytg, 10)),
        ("down_field", down, _bucket(ytg, 20)),
        ("down", down),
        ("global",),
    ]


def _game_groups(plays):
    by = defaultdict(list)
    for p in plays:
        if p.get("gameId") is not None:
            by[str(p.get("gameId"))].append(p)
    for rows in by.values():
        rows.sort(key=_candidate_sort_key)
    return by


def training_examples(plays):
    """Yield (play, realized future net points to end of half)."""
    for rows in _game_groups(plays).values():
        finals = {}
        for p in rows:
            h = half_number(p); score = oriented_score(p)
            if h is not None and score is not None:
                finals[h] = score
        for p in rows:
            if not state_eligible(p):
                continue
            h = half_number(p); final = finals.get(h); cur = oriented_score(p)
            if final is None or cur is None:
                continue
            home_delta, away_delta = final[0] - cur[0], final[1] - cur[1]
            if p.get("offense") == p.get("home"):
                target = home_delta - away_delta
            else:
                target = away_delta - home_delta
            yield p, float(target)


class EmpiricalExpectedPoints:
    def __init__(self, min_count: int = 50):
        self.min_count = min_count
        self.stats = defaultdict(lambda: [0, 0.0])

    def fit(self, plays):
        for p, target in training_examples(plays):
            for key in state_keys(p):
                self.stats[key][0] += 1
                self.stats[key][1] += target
        return self

    def predict(self, play):
        if not state_eligible(play):
            return None
        keys = state_keys(play)
        for i, key in enumerate(keys):
            n, total = self.stats.get(key, (0, 0.0))
            if n >= self.min_count or (i == len(keys) - 1 and n):
                return total / n
        return None


def scoreboard_delta(a, b, offense):
    sa, sb = oriented_score(a), oriented_score(b)
    if sa is None or sb is None:
        return None
    hd, ad = sb[0] - sa[0], sb[1] - sa[1]
    home, away = a.get("home"), a.get("away")
    if offense == home: return hd - ad
    if offense == away: return ad - hd
    return None


def transition_epa(start, end, model):
    """EPA for a start->end recorded-state transition, from start offense view."""
    ep0, ep1 = model.predict(start), model.predict(end)
    if ep0 is None or ep1 is None:
        return None
    offense = start.get("offense")
    points = scoreboard_delta(start, end, offense)
    if points is None:
        return None
    sign = 1.0 if end.get("offense") == offense else -1.0
    return points + sign * ep1 - ep0


def scoring_timing_counts(plays):
    """Compare score changes entering vs leaving source-marked scoring rows."""
    c = defaultdict(int)
    for rows in _game_groups(plays).values():
        eligible = [p for p in rows if oriented_score(p) is not None]
        for i, p in enumerate(eligible):
            scoring = p.get("scoring") is True or str(p.get("eventSubtype") or "").upper() in {"RUSH_TD", "PASS_TD", "FIELD_GOAL_GOOD", "SAFETY"}
            if not scoring:
                continue
            c["scoring_rows"] += 1
            if i > 0:
                d = scoreboard_delta(eligible[i - 1], p, eligible[i - 1].get("offense"))
                if d: c["score_change_entering_scoring_row"] += 1
            if i + 1 < len(eligible):
                d = scoreboard_delta(p, eligible[i + 1], p.get("offense"))
                if d: c["score_change_leaving_scoring_row"] += 1
    return dict(c)


def ppa_coverage(plays):
    c = defaultdict(int)
    for p in plays:
        if state_eligible(p):
            c["eligible_states"] += 1
            if _num(p.get("ppa")): c["eligible_with_ppa"] += 1
        if p.get("isScrimmagePlay") is True and p.get("isOffensivePlay") is True and not p.get("hasNoPlayContext"):
            c["clean_scrimmage"] += 1
            if _num(p.get("ppa")): c["clean_scrimmage_with_ppa"] += 1
    return dict(c)


def pearson(xs, ys):
    n = len(xs)
    if n < 2: return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = sum((x - mx) ** 2 for x in xs); sy = sum((y - my) ** 2 for y in ys)
    if not sx or not sy: return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sqrt(sx * sy)


def compare_to_ppa(train_plays, validation_plays, score_timing="pre", min_count=50):
    model = EmpiricalExpectedPoints(min_count=min_count).fit(train_plays)
    ours, source = [], []
    for rows in _game_groups(validation_plays).values():
        states = [p for p in rows if state_eligible(p)]
        for i in range(len(states) - 1):
            if score_timing == "pre":
                play, start, end = states[i], states[i], states[i + 1]
            elif score_timing == "post":
                if i == 0: continue
                play, start, end = states[i], states[i - 1], states[i]
            else:
                raise ValueError("score_timing must be 'pre' or 'post'")
            if play.get("isScrimmagePlay") is not True or play.get("isOffensivePlay") is not True or play.get("hasNoPlayContext"):
                continue
            if not _num(play.get("ppa")):
                continue
            epa = transition_epa(start, end, model)
            if epa is None:
                continue
            ours.append(float(epa)); source.append(float(play["ppa"]))
    n = len(ours)
    return {
        "version": EPA_RESEARCH_VERSION,
        "score_timing": score_timing,
        "comparison_plays": n,
        "correlation": pearson(ours, source),
        "mae": sum(abs(a - b) for a, b in zip(ours, source)) / n if n else None,
        "mean_epa": sum(ours) / n if n else None,
        "mean_ppa": sum(source) / n if n else None,
    }

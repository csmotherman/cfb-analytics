import numpy as np

from cfb_analytics.analytics.preseason_power.standings import apply_aq_and_seed, conference_standings

# Conference labels are real (championship_game_conferences/P4_CONFERENCES read the real
# 2026 canonical roster to classify them), but all teams/records below are synthetic.
CONF = "Mountain West"


def game(team: str, opponent: str, win: bool, conf: str = CONF, opp_conf: str = CONF) -> dict:
    return {"team": team, "opponent": opponent, "conference": conf, "opponent_conference": opp_conf, "win": int(win), "loss": int(not win)}


def test_two_way_tie_broken_by_head_to_head() -> None:
    # A and B both finish 1-1 in conference play; A beat B head-to-head -> A ranked above B.
    rows = [
        game("A", "B", win=True), game("A", "C", win=False),
        game("B", "A", win=False), game("B", "C", win=True),
        game("C", "A", win=True), game("C", "B", win=False),
    ]
    team_conf = {t: {"conference": CONF} for t in ("A", "B", "C")}
    standings = conference_standings(rows, team_conf, np.random.default_rng(0), season=2026)
    ordered = standings[CONF]
    assert ordered.index("A") < ordered.index("B")


def test_no_head_to_head_falls_back_to_overall_win_pct() -> None:
    # D and E tie in conference play (1-1 each) but never played each other; D has a better
    # overall (non-conference) record, so D should rank above E.
    rows = [
        game("D", "F", win=True), game("D", "G", win=False),
        game("D", "NC1", win=True, opp_conf="Other"),
        game("E", "F", win=False), game("E", "G", win=True),
        game("F", "D", win=False), game("F", "E", win=True), game("F", "G", win=False),
        game("G", "D", win=True), game("G", "E", win=False), game("G", "F", win=True),
    ]
    team_conf = {t: {"conference": CONF} for t in ("D", "E", "F", "G")}
    standings = conference_standings(rows, team_conf, np.random.default_rng(0), season=2026)
    ordered = standings[CONF]
    assert ordered.index("D") < ordered.index("E")


def test_apply_aq_and_seed_2026_rule_guarantees_p4_champions() -> None:
    # A weak P4 champion (low committee score) must still get an AQ bid and be in the 12-team
    # field under the 2026 rule, even though several non-champions outscore it.
    team_conf = {
        "P4WeakChamp": {"conference": "ACC"},
        "P4Champ2": {"conference": "Big Ten"},
        "P4Champ3": {"conference": "Big 12"},
        "P4Champ4": {"conference": "SEC"},
        "G6Champ_weak": {"conference": "Sun Belt"},
        "G6Champ_strong": {"conference": "Mountain West"},
    }
    committee_scores = {"P4WeakChamp": -5.0, "P4Champ2": 3.0, "P4Champ3": 2.0, "P4Champ4": 1.0,
                         "G6Champ_weak": -1.0, "G6Champ_strong": 0.5}
    for i in range(10):
        team = f"AtLarge{i}"
        team_conf[team] = {"conference": "SEC"}
        committee_scores[team] = 4.0 - i * 0.1  # all rank above the weak P4 champ

    conference_champions = {
        "ACC": "P4WeakChamp", "Big Ten": "P4Champ2", "Big 12": "P4Champ3", "SEC": "P4Champ4",
        "Sun Belt": "G6Champ_weak", "Mountain West": "G6Champ_strong",
    }

    field = apply_aq_and_seed(committee_scores, conference_champions, team_conf, season=2026)
    field_teams = {row["team"] for row in field}

    assert len(field) == 12
    assert "P4WeakChamp" in field_teams  # guaranteed despite the lowest score in the whole pool
    assert "G6Champ_strong" in field_teams  # higher-scored G6 champ takes the 5th AQ slot
    assert "G6Champ_weak" not in field_teams  # loses the G6-vs-G6 comparison, must compete as at-large instead
    bid_types = {row["team"]: row["bid_type"] for row in field}
    assert bid_types["P4WeakChamp"] == "AQ_P4_CHAMPION"
    assert bid_types["G6Champ_strong"] == "AQ_G6_CHAMPION"
    # seeding is by committee score regardless of championship status (post-May-2025 rule)
    seeds = {row["team"]: row["seed"] for row in field}
    assert seeds["P4WeakChamp"] > seeds["P4Champ2"]
    byes = {row["team"] for row in field if row["bye"]}
    assert len(byes) == 4


def test_apply_aq_and_seed_pre_2026_rule_can_exclude_a_p4_champion() -> None:
    # The 2024-2025 rule pooled ALL conference champions and took the top 5 by score --
    # a low-ranked P4 champion could miss the field entirely (the real 2025 Duke/ACC case).
    team_conf = {"WeakP4Champ": {"conference": "ACC"}}
    committee_scores = {"WeakP4Champ": -10.0}
    conference_champions = {"ACC": "WeakP4Champ"}
    for conf, name in [("Big Ten", "T1"), ("Big 12", "T2"), ("SEC", "T3"),
                        ("American Athletic", "T4"), ("Sun Belt", "T5"), ("Mountain West", "T6")]:
        team_conf[name] = {"conference": conf}
        committee_scores[name] = 5.0
        conference_champions[conf] = name
    # enough higher-scored non-champion filler to fill all 7 at-large slots ahead of -10
    for i in range(7):
        team_conf[f"Filler{i}"] = {"conference": "SEC"}
        committee_scores[f"Filler{i}"] = 1.0

    field = apply_aq_and_seed(committee_scores, conference_champions, team_conf, season=2025)
    field_teams = {row["team"] for row in field}
    assert "WeakP4Champ" not in field_teams

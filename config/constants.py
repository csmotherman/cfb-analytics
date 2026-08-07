# ============================================================
# SUCCESS RATE
# ============================================================

SUCCESS_RATE = {
    1: 0.50,
    2: 0.70,
    3: 1.00,
    4: 1.00
}

# ============================================================
# EXPLOSIVE PLAY THRESHOLDS
# ============================================================

EXPLOSIVE_RUN = 12

EXPLOSIVE_PASS = 16

# ============================================================
# PLAY FAMILIES
# ============================================================

PLAY_FAMILY = {

    # Run
    "Rush": "Run",
    "Rushing Touchdown": "Run",

    # Pass
    "Pass Reception": "Pass",
    "Pass Completion": "Pass",
    "Pass Incompletion": "Pass",
    "Passing Touchdown": "Pass",
    "Interception": "Pass",
    "Pass Interception Return": "Pass",
    "Interception Return Touchdown": "Pass",
    "Sack": "Pass",

    # Turnovers
    "Fumble": "Turnover",
    "Fumble Recovery (Opponent)": "Turnover",
    "Fumble Recovery (Own)": "Turnover",
    "Fumble Return Touchdown": "Turnover",

    # Punt
    "Punt": "Punt",
    "Punt Return": "Punt",
    "Punt Return Touchdown": "Punt",
    "Blocked Punt": "Punt",
    "Blocked Punt Touchdown": "Punt",

    # Kickoff
    "Kickoff": "Kickoff",
    "Kickoff Return (Offense)": "Kickoff",
    "Kickoff Return Touchdown": "Kickoff",

    # Field Goal
    "Field Goal Good": "Field Goal",
    "Field Goal Missed": "Field Goal",
    "Blocked Field Goal": "Field Goal",
    "Blocked Field Goal Touchdown": "Field Goal",
    "Missed Field Goal Return": "Field Goal",

    # Other Scoring
    "Safety": "Scoring",
    "Defensive 2pt Conversion": "Scoring",

    # Penalties
    "Penalty": "Penalty",

    # Administrative
    "Timeout": "Administrative",
    "End Period": "Administrative",
    "End of Half": "Administrative",
    "End of Game": "Administrative",
    "End of Regulation": "Administrative",

    # Other
    "Uncategorized": "Other",
    "placeholder": "Other"
}
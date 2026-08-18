"""Release-candidate runner for the historical player NIL challenge.

The first real-data benchmark showed the original fictional price bands made every
sampled seven-player board infeasible even at a $28M cap. Before any user outcomes
exist, this runner rescales the fictional SOAR market so cap management can be the
challenge rather than a hard impossibility. Player grades and matchup strength are
unchanged.
"""
from __future__ import annotations

from cfb_analytics.prototypes import historical_player_nil_draft as base
from cfb_analytics.prototypes import historical_player_nil_draft_fast as _fast  # noqa: F401

# Gameplay currency only; deliberately fixed before user testing.
base.NIL_PRICE_BANDS = {
    "QB": (1.0, 5.5),
    "RB": (0.4, 2.8),
    "WR": (0.6, 3.8),
    "TE": (0.4, 2.5),
    "DL": (0.6, 3.4),
    "LB": (0.5, 2.8),
    "DB": (0.5, 3.2),
}
base.BUDGET_CANDIDATES = (14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0)


if __name__ == "__main__":
    base.main()

# 2026 Prediction Product Contract

**Status:** ACTIVE PRESEASON PRODUCT CONTRACT  
**Game publication:** `soar-2026-predictions-v1`  
**Market outlook:** `soar-2026-market-outlook-v1`

SOAR publishes game margins only from immutable snapshots produced by the frozen Prediction v2 prospective pipeline. The product adapter filters those national snapshots to Michigan without changing the predicted margin or winner.

The frozen regression is not probability-calibrated. Public game surfaces therefore show predicted margin and winner and explicitly omit win probability, projected score, and expected wins.

CFP qualification can appear as a separately sourced market benchmark. A two-way Yes/No market is converted from American odds to implied probabilities, then normalized so the two sides sum to one. This removes the listed overround but does not turn the result into a SOAR model probability. The artifact must include source, source URL, timestamp, original odds, calculation, and `valueType=BENCHMARK`.

For 2026, the CFP remains a 12-team field: the ACC, Big Ten, Big 12 and SEC champions plus the highest-ranked champion from the other six FBS conferences receive automatic access, and the next seven highest-ranked teams complete the field. The four highest-ranked teams receive first-round byes.

A future SOAR CFP simulator must validate all of the following before publishing a model probability:

1. calibrated game probabilities;
2. complete national schedules;
3. conference standings and championship qualification;
4. automatic-qualifier selection;
5. a committee-ranking or selection model;
6. out-of-sample probability calibration and error reporting.

Until then, expected wins, conference-title probability, CFP model probability, and national-title probability remain unavailable.

The separately published `historical-cfp-resume-v1` model does not change this contract. It scores completed historical resumes with leave-one-season-out evaluation; it does not simulate 2026 outcomes. See `docs/HISTORICAL_CFP_SELECTION_MODEL.md`.

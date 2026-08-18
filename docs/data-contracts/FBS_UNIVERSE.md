# FBS Analytical Universe

Season-team membership is observed from authoritative season data and carries `season`, stable `team_id`, name, conference, classification, and slug. Conference membership is never assumed across seasons.

Raw/fact storage should retain every game involving an FBS team, including FCS opponents. Canonical schedules and FBS team histories retain those games. The primary national ranking population contains FBS teams only. FBS-vs-FBS-only opponent adjustment may be used when a rating requires a connected comparable population, but it must declare that policy; season totals may use all retained games when their metric contract says so. FCS teams never enter FBS national or conference percentiles. No layer may silently change universes.

Legacy raw partitions currently contain FBS-vs-FBS only. They remain the 2014–2025 regression baseline and are explicitly incomplete for FBS-vs-FCS history.

New broad facts are stored separately under `data/raw/cfbd_facts`. A season audit must prove that the legacy game-ID set is a subset of the broad fact game-ID set. Matchups are explicitly labeled `fbs_vs_fbs` or `fbs_vs_non_fbs`; games with no FBS participant are rejected. The canonical `fbs_membership` snapshot is derived only from participants whose source classification is FBS.

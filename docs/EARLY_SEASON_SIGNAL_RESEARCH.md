# Early-season signal v1

Research only. Does performance in source-labeled Weeks 1 and 2 persist after adjusting for opponents?

Run `.venv/bin/python -m cfb_analytics.analytics.early_season_signal` from the repository root. Outputs live in `data/research/early_season_signal/`.

The sample uses published 2014–2019 and 2021–2025 team-game artifacts, PASS validation, regular-season FBS-versus-FBS games only. Explicit Week 0 labels and postseason are excluded. These are source week labels, not each team's first two games. Some historical opening-week games are labeled Week 1: 18 eligible team-seasons have three FBS games across labels 1–2, 583 have two, and 798 have one. All FBS teams appear in coverage; estimates require an eligible early game, usable offensive and defensive metric observations, and at least six later FBS games. Missing early evidence is not imputed.

Each season and metric uses independent fits for Week 1, Week 2, Weeks 1–2, and Week 3 onward. All fits reuse `schedule-adjusted-ratings-v1`, its registered locked numerator/denominator pairs, home-field treatment, and default ridge 20. No later observations or preseason priors enter an early fit. Later ratings exclude every early game. The model's regularization is an existing research default, not tuned here.

Adjusted net is adjusted offense against an average defense minus adjusted allowance against an average offense, oriented so higher is better. Offense and defense are also analyzed separately. Net success rate is used for the all-team overview; it is not a newly validated overall power rating. Raw-net comparisons use the same opponent-adjusted later net target to keep the comparison matched.

Within each season and eligible metric/window cohort, values become percentile ranks. Summaries pool those within-season percentiles and report Spearman correlation, median absolute percentile movement, crossing the median, and top-quartile persistence. Threshold classifications are descriptive, not hypothesis tests. Team observations share opponents and are not independent; no naive team-level significance claims are made. Yearly correlation ranges accompany pooled results.

Limitations: early schedules are sparse and disconnected; ridge makes fitting possible but cannot identify opponent strength precisely from one game. FCS exclusions can remove one or both early games, limiting coverage and selecting a different early schedule sample. These results measure stability of early-only adjusted estimates, not how early performances would look using hindsight opponent ratings. Later performance is an estimated comparison target, not literal true strength. Changes can reflect development, injuries, schedule-network uncertainty, or sampling variation; this design does not identify causes. Garbage-time plays are not additionally filtered. No assertion about 2026 performance is supported by this completed-season study.

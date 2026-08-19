# Historical team grades

**Definition:** `historical-team-grade-v1`  
**Status:** Product composite  
**Scope:** Completed Michigan seasons with published national metric percentiles

Historical season pages show overall, offense, and defense grades. Python calculates these grades from the published, direction-aware national percentiles; the website only reads the resulting artifact.

Offense uses equal weight across success rate, explosive-play rate, yards per successful play, points per drive, points per scoring opportunity, and havoc rate allowed. Defense uses the corresponding allowed metrics plus defensive havoc rate. Overall is the equal-weight average of the offense and defense composites.

| Percentile | Grade |
| --- | --- |
| 95th+ | S+ |
| 90th–94th | S |
| 80th–89th | A |
| 65th–79th | B |
| 45th–64th | C |
| 25th–44th | D |
| Below 25th | F |

Missing audited national percentiles produce no grade. They are not replaced with record-based or box-score guesses.

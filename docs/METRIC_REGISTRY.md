# CFB Analytics Metric Registry

This registry is the production contract for derived football metrics in this repository.

It exists to prevent metric semantics from being reconstructed later from implementation details, audit scripts, or commit history. A metric should not be considered production-locked unless its definition, eligibility, exclusions, propagation level, reconciliation guarantees, and unresolved limitations are documented here.

## Status vocabulary

- **LOCKED** — definition and corpus have been audited and propagated to team-game and team-season outputs.
- **COUNT ONLY** — positive event count is production-safe, but no rate denominator is locked.
- **PARTIAL** — some production components exist, but the metric family is not complete.
- **FORENSIC ONLY** — investigated but intentionally not propagated.
- **NOT STARTED** — planned but not yet implemented.

## Shared production invariants

- Team-game corpus: **17,020 rows** across **8,510 games**.
- Team-season corpus: **1,438 rows** across **11 seasons**.
- Sequence-sensitive metrics must use canonical chronology: **driveNumber -> playNumber -> play ID**.
- Team-game offense and defense mirrors must reconcile when a metric has both sides.
- Team-season counts must reconcile exactly to team-game counts.
- Source ambiguity is not coerced into a production value when evidence is insufficient.
- `yardsToGoal=0` is excluded only from field-position-dependent metrics; it does not alter Success-v1 eligibility.

---

## Play efficiency metrics

### Success Rate v1

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season  
**Locked eligible corpus:** **1,122,987 plays**  
**Locked successful plays:** **478,515**

**Definition:** Existing Success-v1 clean-play definition used throughout the repository. Success is evaluated from down, distance, and canonical analytics yardage using the repository's locked success rules.

**Production family includes:**
- overall success rate
- rush success rate
- pass success rate
- offense and defense/allowed mirrors

**Reconciliation:** offense and defense eligible/successful counts reconcile at team-game and team-season levels.

### Standard vs Passing Downs

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season  
**Parent corpus:** Success-v1 eligible plays

**Definition:**
- Standard down = 1st down; 2nd-and-7 or less; 3rd/4th-and-4 or less.
- Passing down = 2nd-and-8+; 3rd/4th-and-5+.

**Locked corpus:**
- Standard downs: **771,009**
- Standard-down successes: **369,375**
- Passing downs: **351,978**
- Passing-down successes: **109,140**
- Unclassified eligible plays: **0**

**Reconciliation:** standard + passing = Success-v1 eligible corpus exactly.

### Third/Fourth-Down Conversions

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season

**Definition:** clean Success-v1 eligible 3rd/4th-down attempt converts when canonical yardage reaches/exceeds distance OR the offensive play is a touchdown.

**Locked corpus:**
- Third-down attempts: **227,848**
- Third-down conversions: **92,882**
- Fourth-down attempts: **28,189**
- Fourth-down conversions: **15,408**

**Known adjudication:** 24 late-down touchdowns had recorded yards below distance; forensic review supported treating offensive TD as a conversion.

### Red-Zone / Goal-to-Go Play Efficiency

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season  
**Parent corpus:** Success-v1 eligible plays

**Field-position eligibility:** `1 <= yardsToGoal <= 100`. `yardsToGoal=0` is treated as a source-state artifact for field-position-dependent metrics only.

**Definitions:**
- Red zone = `1 <= yardsToGoal <= 20`.
- Goal-to-go = red-zone snap with `distance >= yardsToGoal`.

**Locked corpus:**
- Field-position eligible plays: **1,122,857**
- Field-state exclusions: **130**
- Red-zone plays: **160,523**
- Red-zone successes: **71,057**
- Goal-to-go plays: **65,962**
- Goal-to-go successes: **30,780**

---

## Negative-play / disruption metrics

### Tackles for Loss v1

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season

**Definition:** clean negative rush or completed-pass play, excluding sacks and excluding only high-confidence structural kneels.

**Locked corpus:**
- Structural TFL candidates: **69,544**
- High-confidence kneels excluded: **1,089**
- Production non-sack TFLs: **68,455**
- Rush TFLs: **57,429**
- Completed-pass TFLs: **11,026**

**Kneel policy:** only HIGH-confidence sequence-supported kneels are excluded. Medium-confidence and terminal-only candidates remain TFL candidates unless stronger evidence exists.

### Havoc v1

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season

**Definition:** unique clean scrimmage play containing at least one of:
- non-sack TFL
- sack
- validated interception
- validated fumble lost

Validated turnover events are anchored to the possession-ending offensive scrimmage snap. Each canonical play counts at most once.

**Locked corpus:**
- Eligible scrimmage plays: **1,145,091**
- Unique havoc plays: **115,877**
- Corpus havoc rate: **10.12%**
- Non-sack TFL component: **68,455**
- Sack component: **33,368**
- Validated turnover component: **15,532**
  - interceptions: **10,875**
  - fumbles lost: **4,657**
- Multi-component overlap plays: **1,478**
- Unresolved turnover anchors: **0**
- Turnover anchor collisions: **0**

**Important:** component raw sums may exceed unique havoc plays because overlapping components count once in Havoc.

---

## Turnover metrics

### Validated Turnovers

**Status:** PARTIAL  
**Level:** Possession/event foundation already used in Havoc and derived corpus

**Locked corpus:**
- Giveaways: **15,532**
- Takeaways: **15,532**
- Interceptions: **10,875**
- Fumbles lost: **4,657**
- Turnover-unresolved possessions: **2,489**

**Production guarantees already present:** giveaway/takeaway reconciliation, interception reconciliation, fumble reconciliation, and turnover-margin sum-to-zero checks.

**Still needed:** explicit registry/production review of exposed team-facing turnover rate fields and any per-possession denominator semantics.

---

## Possession / drive metrics

### Validated Possession Corpus

**Status:** LOCKED FOUNDATION  
**Validated possessions:** **208,725**

This corpus underpins drive efficiency, red-zone possession efficiency, field position, turnover attribution, possession yardage, and other possession-level metrics.

### Drive Efficiency v1

**Status:** LOCKED  
**Level:** Possession -> team-game -> team-season

**Locked corpus:**
- Possessions: **208,725**
- Touchdowns: **54,626**
- Field goals: **19,673**
- Empty possessions: **134,139**
- Other scoring: **287**
- Point-resolved possessions: **208,046**
- Unresolved point possessions: **679**
  - unresolved TD score: **392**
  - ambiguous safety: **287**
- Adjudicated possession points: **436,613**
- Corpus points per resolved possession: **2.099**

**Rate semantics:** TD/scoring rates use all validated possessions. Points per possession uses only point-resolved possessions unless unresolved points can be adjudicated without coercion.

### Red-Zone Possession Efficiency v1

**Status:** LOCKED  
**Level:** Possession -> team-game -> team-season

**Definition:** validated possession that reaches opponent field position `1..20`, using locked Finishing Drives v2 outcome/point adjudication.

**Locked corpus:**
- Red-zone possessions: **62,740**
- Touchdowns: **37,622**
- Field goals: **14,118**
- Empty: **10,997**
- Other scoring: **3**
- TD rate: **59.96%**
- Scoring rate: **82.47%**
- Point-resolved red-zone possessions: **62,491**
- Unresolved point possessions: **249**
- Adjudicated red-zone points: **302,507**
- Points per resolved red-zone possession: **4.841**

### Possession Yardage v1

**Status:** LOCKED  
**Level:** Possession -> team-game -> team-season

**Definition:** sum of clean canonical `isOffensivePlay` analytics yardage within each validated possession, attributed to the adjudicated drive offense. This is **not** net physical field-position advancement.

**Locked corpus:**
- Yardage possessions: **208,725**
- Offensive possession-play yards: **6,730,747**
- Corpus yards per possession: **32.247**
- Exact drive-to-builder reconciliations: **208,725**
- Drive-to-builder mismatches: **0**

**Known source-label discrepancy:** raw offense-label-aligned yards differ from adjudicated-drive attribution by **1,045 yards** across **97 drives / 198 plays**. Production follows the validated drive-builder attribution.

---

## Possession sequence metrics

### Three-and-Out v1

**Status:** COUNT ONLY  
**Level:** Possession -> team-game -> team-season

**Chronology:** canonical `driveNumber -> playNumber -> play ID` ordering is mandatory.

**Strict event definition:** validated possession with exactly three clean offensive scrimmage snaps, exact down sequence `1 -> 2 -> 3`, no first-down reset, affirmative punt evidence, no turnover, and no scoring outcome.

**Locked corpus count:** **42,782**

**Production fields:**
- `threeAndOuts`
- `threeAndOutsForced`

**Intentionally not produced:** three-and-out rate.

**Reason:** no denominator is production-locked. Start-first-down possession eligibility is contaminated by short possessions, end-of-period/game state, scoring/turnover terminations, and incomplete possession-exit evidence. The positive event count is safe; an inferred opportunity denominator is not.

### First-Down Generation v1

**Status:** COUNT ONLY  
**Level:** Play event -> team-game -> team-season

**Chronology:** canonical chronology required for the reset-evidence branch.

**Event definition:** a clean offensive scrimmage snap generates a first down when **any** of the following are true:
1. canonical analytics yardage reaches/exceeds pre-snap distance;
2. the play is an offensive touchdown;
3. the chronology-locked next clean offensive snap resets to down 1.

**Locked corpus count:** **364,597**

**Evidence audit totals:**
- Structural line-to-gain evidence: **345,475**
- Touchdown evidence: **54,642**
- Observed next-snap first-down reset: **299,359**
- Multiple evidence signals: **334,546**
- Structural-only events: **10,932**
- Reset-only events: **19,045**
- TD-only events: **74**

**Production fields:**
- `firstDownsGenerated`
- `firstDownsAllowed`

**Intentionally not produced:** first-down generation rate.

**Reason:** the numerator is locked, but the denominator has not been separately defined and audited. Possible interpretations such as all plays, series opportunities, or another exposure measure are not interchangeable and must not be selected implicitly.

---

## Other locked derived corpus totals

These totals are already reconciled in the derived team-game and team-season corpus and may support additional production metrics or future registry entries.

- Explosive eligible plays: **1,123,371**
- Explosive plays: **135,981**
- Successful-play yards: **5,948,558**
- Scoring opportunities: **104,648**
- Adjudicated opportunity points: **383,991**
- Unresolved point opportunities: **338**
- Field-position eligible possessions: **208,725**

**Checkpoint note:** the presence of reconciled corpus totals does not automatically mean every associated team-facing metric family is fully documented or production-complete. Those families should receive explicit registry entries as they are reviewed.

---

## Remaining core roadmap

### Explosiveness

**Status:** PARTIAL / NEEDS CHECKPOINT REVIEW

The derived corpus already reconciles **1,123,371 explosive-eligible plays** and **135,981 explosive plays**, so explosiveness is not truly "not started." Before adding new logic, review the existing explosive definition, thresholds, rush/pass splits, allowed mirrors, and exposed team-game/team-season fields. If the current definition is satisfactory, document and lock it rather than rebuilding it.

### Team-Facing Turnover Metrics

**Status:** PARTIAL

The turnover event foundation is strong. Review what is already exposed in team-game/team-season outputs and lock useful fields such as giveaways, takeaways, interceptions, fumbles lost, and turnover margin. Define rate denominators separately if rates are desired.

### Sack / Dropback Metrics

**Status:** NOT FULLY LOCKED AS A FAMILY

Validated sacks already exist as a Havoc component (**33,368**). Needed work is denominator semantics: sacks, sacks allowed, and sack rates should use a validated dropback denominator rather than all pass plays unless explicitly defined otherwise.

### Basic Yardage Efficiency

**Status:** NEEDS CHECKPOINT REVIEW

Review current team-game/team-season fields for yards/play, rush yards/play, pass yards/play, and allowed mirrors before implementing duplicates. Any rates must be tied to a documented eligible-play denominator.

### Situational / Short-Yardage Metrics

**Status:** NOT STARTED OR NOT YET REGISTRY-LOCKED

Potential families:
- early-down success
- stuff rate
- power/short-yardage success
- field-position starts
- plays per possession
- drive duration, only if clock state is sufficiently reliable

### Deferred Rate Denominators

**Status:** FORENSIC ONLY

- three-and-out rate
- first-down generation rate

Do not add these until the opportunity denominator is explicitly defined and independently audited.

### EPA Layer

**Status:** NOT STARTED

EPA should come only after the non-EPA production corpus is stable. It requires an expected-points model with trustworthy field position, down, distance, clock, score state, and game context. EPA should be treated as a modeling project, not a simple derived column.

---

## Change-control rule

Whenever a production metric is added or its definition changes:

1. Run a forensic audit before propagation when the source semantics are not trivially safe.
2. Lock the corpus total or denominator where appropriate.
3. Propagate to team-game and team-season.
4. Require offense/defense reconciliation when applicable.
5. Require team-season totals to reconcile to team-game totals.
6. Record the metric's definition version in output where practical.
7. Update this registry in the same change set or immediately afterward.
8. Never silently change a denominator or semantic definition under an existing version label.

This file is a checkpoint contract, not a wishlist. A metric marked LOCKED should be reproducible from the repository and should retain its documented meaning until deliberately versioned.
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

**Production family includes:** overall, rush, pass, and offense/defense allowed mirrors.

**Reconciliation:** offense and defense eligible/successful counts reconcile at team-game and team-season levels.

### Explosiveness v1

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season

**Definition:** eligible canonical offensive scrimmage play is explosive when:
- rush gains **10+ yards**; or
- pass gains **20+ yards**.

Eligible plays require usable canonical analytics yardage. Modified/no-play contexts are excluded. Sacks remain in the pass family but cannot satisfy the positive-yard explosive threshold.

**Locked corpus:**
- Explosive-eligible plays: **1,123,371**
- Explosive plays: **135,981**
- Corpus explosive-play rate: **12.10%**
- Rush eligible: **584,220**
- Rush explosive: **83,353** (**14.27%**)
- Pass eligible: **539,151**
- Pass explosive: **52,628** (**9.76%**)

**Production family includes:** overall/rush/pass eligible counts, explosive counts, rates, and offense/defense allowed mirrors.

**Production-lock audit guarantees:** overall and rush/pass locked corpus totals match materialized team-game output; rush + pass reconciles to overall; offense/defense mirrors reconcile; team-season counts reconcile to team-game counts; and all team-game/team-season offensive and defensive rates recompute exactly from their stored counts.

### Basic Yardage Efficiency v1

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season  
**Definition version:** `basic-yardage-v1`

**Definition:** Basic Yardage v1 measures classified offensive scrimmage efficiency using the union of validated rush attempts and locked Dropbacks v1. Clean standalone source-artifact records that are not part of either family are excluded rather than silently entering the denominator.

**Locked corpus:**
- Basic Yardage plays: **1,146,848**
- Basic Yardage yards: **6,739,101**
- Corpus yards/play: **5.876**
- Rush attempts: **592,949**
- Rush yards: **3,061,968**
- Rush yards/attempt: **5.164**
- Dropbacks: **553,899**
- Net pass yards: **3,677,133**
- Net pass yards/dropback: **6.639**
- Recovered residual interception dropbacks: **1,854**

**Recovered interception policy:** validated residual interception possessions with zero standard Dropbacks-v1 evidence contribute one recovered interception dropback when explicit interception evidence exists. These recovered attempts are **denominator-only** for passing-yard efficiency. Their source `yardsGained` values represent interception-return movement, not validated offensive passing yardage, and therefore contribute **zero** yards to the passing numerator.

**Explicit exclusions:**
- **74** standalone `FUMBLE` scrimmage records totaling **465 yards** are excluded from rush/pass classification.
- **20** `TWO_POINT_PASS` records and **3** `PASS_UNSPECIFIED` records totaling **7 yards** are excluded from Dropbacks v1.
- Modified/no-play contexts remain excluded according to the underlying clean-play rules.

**Production family includes:** overall Basic Yardage plays/yards/yards-per-play, rush attempts/yards/yards-per-attempt, dropbacks/net-pass-yards/net-pass-yards-per-dropback, recovered interception dropback counts, and offense/defense allowed mirrors.

**Production-lock audit guarantees:** team-game corpus is **17,020 rows**; team-season corpus is **1,438 rows**; all locked corpus totals above reproduce exactly; offense/defense mirrors reconcile for plays, yards, rush attempts, rush yards, dropbacks, net pass yards, and recovered interception dropbacks; team-season totals reconcile to team-game totals; and definition-version fields are present at both levels.

### Dropbacks / Sack Rate v1

**Status:** LOCKED  
**Level:** Play/validated interception possession -> team-game -> team-season  
**Definition version:** `dropbacks-v1`

**Definition:** a Dropbacks-v1 event is a canonical `PASS_COMPLETION`, `PASS_INCOMPLETE`, `PASS_TD`, `INTERCEPTION`, or `SACK`, plus exactly one recovered interception attempt for a validated interception possession with zero standard dropback evidence and explicit interception source text. No-play and two-point contexts are excluded, and `PASS_UNSPECIFIED` is not promoted.

**Locked corpus:**
- Dropbacks: **553,899**
- Sacks: **33,368**
- Corpus sack rate: **6.02%**
- Recovered residual interception dropbacks: **1,854**

**Production family includes:** `dropbacks`, `sacksAllowed`, `sackRate`, `defensiveDropbacks`, `sacks`, `defensiveSackRate`, and `dropbacksDefinitionVersion`.

**Production-lock audit guarantees:** team-game and team-season corpus sizes match shared production invariants; dropbacks and sacks reproduce the locked corpus; offense/defense counts reconcile; team-season counts reconcile exactly to team-game counts; offensive and defensive sack rates recompute from stored counts at both levels; zero denominators produce null rates; and the definition version is present everywhere.

### Standard vs Passing Downs

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season  
**Parent corpus:** Success-v1 eligible plays

**Definition:** Standard down = 1st down; 2nd-and-7 or less; 3rd/4th-and-4 or less. Passing down = 2nd-and-8+; 3rd/4th-and-5+.

**Locked corpus:** standard **771,009** / successes **369,375**; passing **351,978** / successes **109,140**; unclassified **0**.

### Third/Fourth-Down Conversions

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season

**Definition:** clean Success-v1 eligible 3rd/4th-down attempt converts when canonical yardage reaches/exceeds distance OR the offensive play is a touchdown.

**Locked corpus:** third attempts **227,848**, conversions **92,882**; fourth attempts **28,189**, conversions **15,408**.

### Red-Zone / Goal-to-Go Play Efficiency

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season

Field-position eligibility is `1 <= yardsToGoal <= 100`; `yardsToGoal=0` is excluded as a source-state artifact for field-position metrics.

**Locked corpus:** field-position eligible **1,122,857**; exclusions **130**; red-zone plays **160,523**, successes **71,057**; goal-to-go plays **65,962**, successes **30,780**.

---

## Negative-play / disruption metrics

### Tackles for Loss v1

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season

**Definition:** clean negative rush or completed-pass play, excluding sacks and only high-confidence structural kneels.

**Locked corpus:** candidates **69,544**; kneels excluded **1,089**; production TFLs **68,455**; rush **57,429**; completed-pass **11,026**.

### Havoc v1

**Status:** LOCKED  
**Level:** Play -> team-game -> team-season

**Definition:** unique clean scrimmage play containing non-sack TFL, sack, validated interception, or validated fumble lost. Turnovers are anchored to the possession-ending offensive scrimmage snap and each play counts once.

**Locked corpus:** eligible **1,145,091**; havoc **115,877** (**10.12%**); TFL **68,455**; sacks **33,368**; validated turnovers **15,532** (INT **10,875**, fumbles lost **4,657**); multi-component overlaps **1,478**; unresolved anchors **0**; collisions **0**.

---

## Turnover metrics

### Team-Facing Turnovers v1

**Status:** LOCKED  
**Level:** Possession/event -> team-game -> team-season

**Locked corpus:** giveaways **15,532**; takeaways **15,532**; interceptions **10,875**; fumbles lost **4,657**; turnover-unresolved possessions **2,489**; resolved turnover-classification possessions **206,236**.

**Production fields:** `giveaways`, `interceptionsThrown`, `fumblesLost`, `turnoverResolvedPossessions`, `turnoverUnresolvedPossessions`, `takeaways`, `interceptionsMade`, `fumblesRecovered`, `takeawayResolvedPossessions`, `takeawayUnresolvedPossessions`, `turnoverMargin`, plus `turnoversDefinitionVersion`.

**Definition:** direct interceptions and interception-return-only possessions are giveaways; opponent fumble recoveries/fumble-return TDs are fumbles lost; own recoveries are not giveaways; modified/nullified turnover contexts are excluded; unresolved fumble/miscellaneous/multiple-signal records remain unresolved rather than coerced.

**Production-lock audit guarantees:** giveaways/takeaways, interceptions, fumbles, and unresolved counts match the locked corpus; offense/defense mirrors reconcile; team-season totals reconcile exactly to team-game totals; aggregate turnover margin sums to zero; and each team-game/team-season row recomputes `turnoverMargin` exactly as `takeaways - giveaways`.

**Rate policy:** no turnover rate is locked by this family. Any future turnover-rate metric must document and independently validate its denominator; unresolved possessions must not be silently counted as non-turnovers.

---

## Possession / drive metrics

### Validated Possession Corpus

**Status:** LOCKED FOUNDATION  
**Validated possessions:** **208,725**

### Drive Efficiency v1

**Status:** LOCKED  
**Level:** Possession -> team-game -> team-season

**Locked corpus:** possessions **208,725**; TD **54,626**; FG **19,673**; empty **134,139**; other scoring **287**; resolved **208,046**; unresolved **679**; adjudicated points **436,613**; points/resolved possession **2.099**.

### Red-Zone Possession Efficiency v1

**Status:** LOCKED  
**Level:** Possession -> team-game -> team-season

**Locked corpus:** red-zone possessions **62,740**; TD **37,622**; FG **14,118**; empty **10,997**; other **3**; TD rate **59.96%**; scoring rate **82.47%**; point-resolved **62,491**; unresolved **249**; points **302,507**; points/resolved RZ possession **4.841**.

### Possession Yardage v1

**Status:** LOCKED  
**Level:** Possession -> team-game -> team-season

**Definition:** sum of clean canonical `isOffensivePlay` analytics yardage within each validated possession, attributed to adjudicated drive offense; not net physical field-position advancement.

**Locked corpus:** possessions **208,725**; yards **6,730,747**; yards/possession **32.247**; exact builder reconciliations **208,725**; mismatches **0**.

---

## Possession sequence metrics

### Three-and-Out v1

**Status:** COUNT ONLY  
**Level:** Possession -> team-game -> team-season

**Strict event definition:** validated possession with exactly three clean offensive scrimmage snaps, exact `1 -> 2 -> 3`, no first-down reset, affirmative punt evidence, no turnover, and no scoring outcome.

**Locked count:** **42,782**. Production fields: `threeAndOuts`, `threeAndOutsForced`. Rate intentionally absent because no opportunity denominator is locked.

### First-Down Generation v1

**Status:** COUNT ONLY  
**Level:** Play event -> team-game -> team-season

**Definition:** clean offensive scrimmage snap generates a first down when canonical yardage reaches/exceeds distance, OR it is an offensive TD, OR the chronology-locked next clean offensive snap resets to down 1.

**Locked count:** **364,597**. Production fields: `firstDownsGenerated`, `firstDownsAllowed`. Rate intentionally absent because denominator semantics are not locked.

---

## Other reconciled derived corpus totals

These totals may support future registry entries but are not automatically production-locked metric families:

- Successful-play yards: **5,948,558**
- Scoring opportunities: **104,648**
- Adjudicated opportunity points: **383,991**
- Unresolved point opportunities: **338**
- Field-position eligible possessions: **208,725**

---

## Remaining core roadmap

### Situational / Short-Yardage Metrics
Potential families: early-down success, stuff rate, power/short-yardage success, field-position starts, plays per possession, drive duration if clock state is sufficiently reliable.

### Deferred Rate Denominators
**FORENSIC ONLY:** three-and-out rate, first-down generation rate, and turnover rates without an independently validated opportunity denominator.

### EPA Layer
**NOT STARTED.** Treat EPA as a later modeling project requiring trustworthy field position, down, distance, clock, score state, and game context.

---

## Change-control rule

Whenever a production metric is added or its definition changes:

1. Run a forensic audit before propagation when source semantics are not trivially safe.
2. Lock the corpus total or denominator where appropriate.
3. Propagate to team-game and team-season.
4. Require offense/defense reconciliation when applicable.
5. Require team-season totals to reconcile to team-game totals.
6. Record the metric definition version where practical.
7. Update this registry in the same change set or immediately afterward.
8. Never silently change a denominator or semantic definition under an existing version label.

This file is a checkpoint contract, not a wishlist. A metric marked LOCKED should be reproducible from the repository and retain its documented meaning until deliberately versioned.
# Build to Beat 2019 LSU

**Status:** CONCEPT / PRODUCT DESIGN  
**Purpose:** define the fan-facing SOAR Analytics roster-building game before player-data acquisition, model research, or implementation begins.  
**Implementation status:** documentation only; no game code or player-based prediction model exists yet.

## Product goal

Create a simple, highly replayable college-football game that can attract fans to SOAR Analytics.

The fan builds a custom team from randomly selected historical college-football teams and players. When the roster is complete, SOAR evaluates that roster against the 2019 LSU Tigers and returns one headline result:

```text
YOUR CHANCE TO BEAT 2019 LSU

14.7%
```

The game does **not** simulate a final score or randomly decide a winner.

The SOAR model's estimated win probability is the score of the game.

```text
Win probability < 50.0%  -> LSU wins
Win probability >= 50.0% -> user beats LSU
```

Crossing 50% should be intentionally difficult. The goal is to make 2019 LSU feel like the final boss rather than an average opponent.

## Fan-first design principle

The game must be understandable without knowing advanced football analytics.

Fans should interact with:

- recognizable teams and seasons;
- recognizable players;
- football positions and position groups;
- a wheel / random-team mechanic;
- roster-building decisions;
- one large win-probability result;
- an obvious 50% target.

The statistical model should operate underneath the experience rather than forcing the user to understand model features.

The intended reaction is:

```text
"What chance did you get?"
"I got 46.8%."
"No way. I only got 31%."
"I finally got over 50%."
```

The percentage is therefore both the prediction and the player's score.

## Core game loop

The working flow is:

```text
START
  |
  v
Spin historical team + season
  |
  v
See eligible players / units from that team
  |
  v
Choose one for an open roster slot
  |
  v
Lock selection
  |
  v
Repeat until roster is complete
  |
  v
SOAR evaluates roster vs 2019 LSU
  |
  v
Display win probability
  |
  +--> < 50%: LSU wins
  |
  +--> >= 50%: user beats LSU
  |
  v
Build again / share
```

The user does not freely search for any player in history. Randomness from the team-season wheel is central to the challenge.

Once a selection is assigned to a roster slot, it should be locked for that build.

## Proposed roster structure

The first version should favor recognizable football decisions over a full 22-player depth chart.

### Offense

```text
QB
RB
WR1
WR2
TE
OL unit
```

### Defense

The defensive roster should use position groups where individual historical data is not reliable enough to support fair player-level evaluation.

Working structure:

```text
DL / pass-rush unit
LB unit
Secondary
```

The exact defensive split remains an open design decision and should be driven by player-data feasibility.

Possible later expansion:

```text
EDGE
DT
LB
CB
S
```

but only if the underlying historical data can support those distinctions credibly.

### Coaching

A head-coach / coaching slot is a possible additional roster decision, but it should not be included until there is a defensible way to represent coaching value in the player-based prediction framework.

## Example turn

The wheel lands on:

```text
2022 Georgia
```

Depending on the final data source and roster design, the fan may be offered choices such as:

```text
Brock Bowers -> TE
2022 Georgia OL -> OL
2022 Georgia DL -> DL
2022 Georgia LB -> LB
2022 Georgia Secondary -> Secondary
```

The user chooses one eligible open slot.

Example:

```text
2022 Georgia Secondary -> Secondary
```

That slot is now filled and the next spin begins.

The strategic tension comes from not knowing which team-season will appear next.

## Why the wheel matters

If fans can simply draft any players they want, most users will converge toward the same obvious all-star roster.

The wheel creates:

- scarcity;
- risk;
- regret;
- strategy;
- replayability;
- bad-luck stories;
- great-luck stories;
- shareable roster combinations.

The wheel should not contain only national champions and elite teams. A healthy distribution of elite, good, average, and weak team-seasons is necessary to keep the game difficult.

A bad spin should sometimes force an uncomfortable decision.

Example:

```text
The user still needs QB and OL.
The wheel lands on a poor passing team with an excellent offensive line.
The fan must decide whether to use the OL now or risk waiting for something better.
```

## Boss: 2019 LSU

The initial boss is the 2019 LSU Tigers.

The product premise is:

> Build a college-football roster strong enough that SOAR Analytics gives it at least a 50% chance to beat 2019 LSU.

The LSU opponent should be fixed and evaluated consistently. The game should not secretly weaken LSU or boost the user's team based on progress.

The difficulty should come from:

- the strength of the 2019 LSU benchmark;
- the roster construction rules;
- the wheel population;
- the rarity of elite team-seasons;
- position and unit interactions;
- weaknesses in the user's final roster.

## Result contract

The main result is a win probability, not a simulated score.

Example loss:

```text
YOUR CHANCE TO BEAT 2019 LSU

14.7%

LSU WINS
You need 50.0% to beat the Tigers.
```

Example near miss:

```text
YOUR CHANCE TO BEAT 2019 LSU

48.6%

NOT ENOUGH
1.4 percentage points away.
```

Example victory:

```text
YOUR CHANCE TO BEAT 2019 LSU

51.3%

YOU BEAT 2019 LSU
Your roster is favored by the SOAR model.
```

The percentage should be the dominant visual element on the result screen.

## Difficulty target

Winning should be rare.

The game should be calibrated so that an ordinary completed build has little chance of reaching 50%.

A conceptual distribution might look like:

```text
Poor build          very low probability
Average build       clearly below 50%
Good build          meaningful underdog
Great build         approaches 40%+
Exceptional build   approaches 50%
Winner              50%+
```

Exact thresholds and the target percentage of winning builds must be determined empirically after the player-based model and wheel pool exist.

Do **not** impose an artificial probability cap merely to force difficulty. The model, data, roster rules, and wheel distribution should create the difficulty naturally.

## Player-based prediction model

This game requires a new prediction framework separate from the current team-game Prediction v2 model.

The current SOAR Prediction v2 architecture should remain untouched unless future research independently justifies changes to it.

The game model should answer a different question:

> Given a synthetic roster assembled from players and position groups across different historical teams, what is that roster's estimated probability of defeating 2019 LSU on a neutral field?

Conceptually:

```text
Historical player / unit statistics
        |
        v
Position-specific ratings
        |
        v
Synthetic roster profile
        |
        v
Offense-defense matchup interactions
        |
        v
Expected team strength / margin
        |
        v
Win probability vs 2019 LSU
```

This model must be researched and validated before it is presented as SOAR analytics.

## Position modeling principles

Different positions require different evidence.

### QB

Potential inputs may include passing efficiency, completion performance, yards per attempt, touchdown creation, interception avoidance, sack avoidance, rushing contribution, explosiveness, and opponent adjustment.

### RB

Potential inputs may include rushing efficiency, success, explosiveness, receiving contribution, volume, and opponent adjustment.

### WR / TE

Potential inputs may include receiving efficiency, production, explosiveness, touchdown contribution, volume / target share where available, and opponent adjustment.

### Offensive line

OL should initially be treated as a **team-season unit** unless reliable historical individual offensive-line data is available.

A unit model may use team rushing support, sack / pressure prevention where available, line-related efficiency measures, and opponent-adjusted performance.

### Defense

Defensive evaluation should not be built from tackles and sacks alone.

Coverage players can be valuable precisely because opponents avoid throwing at them. Defensive position design must therefore be based on the data that can actually be acquired and validated.

If individual historical coverage / pressure evidence is insufficient, defensive team-season units are preferable to invented individual precision.

## Player-data feasibility is the first research gate

Before building the model, determine what historical college-football player and unit data can be acquired consistently.

Required feasibility categories:

```text
QB
RB
WR
TE
OL
EDGE / DL
LB
CB
S
```

For each category, document:

```text
available seasons
data source
fields available
coverage completeness
player identifiers
team / season linkage
opponent context
missing-data behavior
licensing / usage constraints
```

The final roster structure should follow the evidence.

Do not force a position into the game if the available statistics cannot support a credible rating for it.

## Model interaction requirement

The final roster should not be evaluated by simply averaging player ratings.

Matchups should matter.

Conceptually:

```text
Passing strength
  = QB
  + WR / TE receiving ability
  + OL protection
  + interactions

Passing matchup
  = synthetic passing strength
  vs LSU pass rush + coverage

Rushing strength
  = RB
  + OL rushing support
  + interactions

Rushing matchup
  = synthetic rushing strength
  vs LSU front / run defense
```

The exact model architecture remains research work.

## Neutral-field contract

The game should evaluate the synthetic team against 2019 LSU on a neutral field.

This avoids making the challenge dependent on an arbitrary home-field assignment and gives every build the same benchmark environment.

## No account requirement for initial version

The first version should not require:

```text
account creation
email
subscription
profile
persistent roster history
private leagues
```

The goal is low-friction traffic and replayability.

A fan should be able to arrive at SOAR Analytics and begin building immediately.

## Traffic and sharing loop

The game should be designed as an acquisition surface for SOAR Analytics rather than a hidden utility.

Core loop:

```text
Fan discovers game
  -> builds roster
  -> receives win probability
  -> wants a better percentage
  -> plays again
  -> shares result / challenge
  -> friend visits SOAR
```

A shareable result should emphasize:

```text
roster
win probability
50% target
whether the user beat LSU
SOAR Analytics branding
```

Example:

```text
MY TEAM HAD A 47.8% CHANCE TO BEAT 2019 LSU

I was 2.2 points away.
Can you beat my build?
```

## Same-spin friend challenge

A high-value future feature is a share link that reproduces the same sequence of team-season spins for another fan.

Both users receive identical luck but may make different roster decisions.

This changes the challenge from:

```text
Who got luckier?
```

into:

```text
Who built the better roster from the same choices?
```

This can support viral sharing without requiring accounts.

## Daily challenge

Another future traffic mechanic is a daily deterministic wheel sequence.

All fans receive the same spins for the day.

Possible display:

```text
SOAR DAILY BUILD
Everyone gets the same teams.
Can you reach 50%?
```

This creates a reason to return to the website without requiring account persistence.

Anonymous aggregate analytics could later support statistics such as daily win rate or average build probability, but those are not required for the initial concept.

## Future bosses

2019 LSU should be the initial challenge and product identity.

The architecture should eventually allow additional historical bosses if appropriate player / team data is available.

Possible future concept:

```text
Beat 2019 LSU
Beat 2020 Alabama
Beat 2021 Georgia
Beat 2023 Michigan
```

Historical teams outside the supported player-data corpus should not be added until their data can be evaluated under the same methodology.

## Initial product scope

The smallest meaningful version is:

```text
1. Historical team-season wheel
2. Roster slots
3. Player / unit choices for the spun team
4. Locked selections
5. Completed synthetic roster
6. Player-based SOAR evaluation vs 2019 LSU
7. Large win-probability result
8. 50% victory threshold
9. Build-again action
10. Shareable result
```

No accounts or Supabase user system are required for this concept.

## Research before implementation

Before game implementation begins, complete these research steps:

1. player-data feasibility audit;
2. final roster-slot contract;
3. position / unit rating definitions;
4. 2019 LSU player and unit benchmark construction;
5. synthetic-roster interaction design;
6. leakage-safe training dataset design;
7. probability calibration and validation;
8. wheel population and difficulty calibration;
9. verification that 50%+ builds are rare but genuinely attainable.

## Non-goals

This document does not authorize changes to:

- Prediction v2;
- existing CFB metrics;
- current feature stores;
- canonical data definitions;
- team-game research benchmarks;
- production website code.

The game is a separate product/research track until its data and model are validated.

## Working product statement

> Spin historical college-football teams. Build your roster one player or unit at a time. Then let SOAR Analytics tell you the one number that matters: your chance to beat the 2019 LSU Tigers. Reach 50% and you win.

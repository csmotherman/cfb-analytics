# SOAR Analytics Website Vision

**Status:** Product/design source of truth  
**Audience:** Codex, human contributors, future design/engineering work  
**Product:** SOAR Analytics  
**Scope:** Public college-football analytics website

---

# 1. Mandate

The website has graduated from a functional pilot into a real product.

The old prototype optimized for validating data flows and fan questions. That was the correct first step. The next step is different: **SOAR Analytics must feel like a product people remember, explore, share, and return to.**

The website should not feel like:

- a school project;
- a BI dashboard;
- a table viewer with nicer CSS;
- a generic AI-generated SaaS page;
- a betting-picks site;
- a collection of disconnected charts.

The website should feel like:

> **a premium sports broadcast product fused with flight/telemetry instrumentation.**

The SOAR name should influence the visual language without becoming a literal airplane theme. Think altitude, trajectory, signal, velocity, separation, navigation, vectors, and dimensional space.

The emotional target is:

> “I have never seen college-football data presented like this before.”

The analytical target is:

> “I understand this team better after using SOAR than I did before.”

The product must accomplish both.

---

# 2. North-star product promise

SOAR Analytics helps a fan answer four questions quickly:

1. **How good is this team?**
2. **What kind of team is it?**
3. **What makes it different from other teams?**
4. **What happens when I compare or match it against another team?**

Everything on the site should support one or more of these questions.

A useful working description is:

> **SOAR Analytics turns college-football performance into an explorable map of team strength, identity, matchup edges, and historical similarity.**

Do not hard-code a marketing tagline until one is deliberately chosen, but all public copy should reinforce this product promise.

---

# 3. Product principles

## 3.1 Explanation beats raw volume

The underlying repository contains a large amount of data. The website should not respond by showing all of it.

Every major section should answer:

- What matters?
- Why does it matter?
- How unusual is it?
- What is the comparison point?

A fan should be able to understand the page before opening a metric glossary.

## 3.2 Exploration beats static reporting

SOAR should reward curiosity.

Users should be able to:

- search any historical team-season;
- move from a team to similar teams;
- jump from rankings into a profile;
- compare eras;
- explore archetypes;
- inspect matchup edges;
- traverse the Team DNA space;
- see how a team changed over a season.

Pages should connect to one another instead of ending in dead ends.

## 3.3 Visualization must encode meaning

Do not add a chart because dashboards are expected to have charts.

Every visualization must encode a meaningful relationship such as:

- rank;
- distribution;
- distance;
- trajectory;
- advantage;
- similarity;
- change over time;
- composition;
- uncertainty.

If a visualization is not doing analytical work, remove it.

## 3.4 Advanced math, fan-first language

The analytical engine can be complex. The public language should not be.

Good:

> “Elite passing efficiency against opponent-adjusted defenses.”

Bad:

> “Current OA pass efficiency percentile derived from contextual iterative fitting.”

Methodology should remain available, but it should not dominate the primary experience.

## 3.5 No invented confidence

SOAR must remain more credible than the average sports site.

Never fabricate:

- metrics;
- rankings;
- historical comparisons;
- simulation outputs;
- probabilities;
- missing grades;
- model explanations.

If a feature lacks sufficient data, say so intentionally or hide the unsupported element.

---

# 4. Brand and visual language

## 4.1 Core idea

The global visual system should feel like:

- modern sports broadcast graphics;
- aerospace/telemetry instrumentation;
- premium editorial data visualization;
- an interactive research lab built for fans.

Avoid copying ESPN, The Athletic, Apple, Stripe, or any single existing product. Borrow principles, not layouts.

## 4.2 Color direction

The application should use a dark, high-contrast base so team colors and analytical signals can become meaningful accents.

Suggested initial tokens:

```css
--soar-bg: #070b12;
--soar-bg-raised: #0b111b;
--soar-surface: #101925;
--soar-surface-2: #152131;
--soar-border: rgba(255,255,255,.10);
--soar-text: #f5f8fc;
--soar-text-muted: #95a2b5;
--soar-sky: #66b8ff;
--soar-indigo: #7d8cff;
--soar-signal: #d7ff68;
--soar-danger: #ff6b72;
--soar-warning: #ffc857;
```

These are a starting point, not immutable brand law. If official SOAR brand assets later define different colors, migrate the tokens rather than scattering replacements throughout components.

### Accent discipline

- SOAR blue/indigo = navigation, selection, focus, neutral analytics.
- Signal lime = rare/high-value emphasis only.
- Team colors = contextual identity accents.
- Red/orange = actual warnings, poor outcomes, or negative matchup edges.

Do not turn every stat into a rainbow.

## 4.3 Team colors

A selected team should influence its page without taking over the entire application.

Use team color for:

- a hero-edge glow;
- chart traces;
- selected nodes;
- comparison accents;
- subtle section rules;
- identity halo/background texture.

Do not set the full page background to a team color.

## 4.4 Typography

The typography should support three voices:

1. **Editorial/display** — strong page titles and hero statements.
2. **Interface/body** — highly readable explanatory text.
3. **Telemetry/numeric** — rankings, grades, coordinates, percentages, model outputs.

Use a clean sans-serif family and a mono or tabular-number treatment for data. Numbers must align cleanly in rankings and comparison layouts.

Large numbers should feel like broadcast graphics, not oversized admin-dashboard KPIs.

## 4.5 Texture and depth

Use depth sparingly and intentionally:

- subtle grid/vector lines;
- orbit/trajectory traces;
- light bloom around active 3D nodes;
- layered dark surfaces;
- barely visible topographic or telemetry patterns;
- masked gradients that reinforce section focus.

Avoid:

- constant blur everywhere;
- glass cards on every section;
- random gradient blobs;
- fake stars that add no information;
- decorative football stock photography.

## 4.6 Icons

Use a consistent icon set. Do not use emoji as navigational icons.

Icons should assist scanning, not replace clear labels.

---

# 5. Motion language

Motion should make SOAR feel alive, but it must communicate meaning.

Use motion for:

- selected-team transitions;
- rankings changing position;
- comparison advantages expanding;
- trajectory paths drawing into view;
- 3D camera focus;
- filters updating a dataset;
- simulation distributions resolving;
- revealing a team’s nearest historical neighbors.

Avoid animation for:

- every card entering the screen;
- constant background movement;
- looping effects that compete with reading;
- decorative counters that delay information.

Transitions should generally feel fast and controlled.

Always respect `prefers-reduced-motion`.

---

# 6. Global application shell

The current prototype nav should become a real application shell.

## Desktop

Recommended structure:

```text
SOAR Analytics      Search teams, seasons, metrics…       [Rankings] [Explore] [Compare] [Matchup]
───────────────────────────────────────────────────────────────────────────────────────────────
page content
```

The header should:

- remain visually light;
- support global search;
- make core product modes obvious;
- avoid seven equal-weight text links.

## Mobile

Use a compact header with:

- SOAR mark/name;
- search trigger;
- menu or compact bottom navigation for core actions.

Do not crush the desktop nav into two wrapped rows.

---

# 7. Global command search

A signature usability feature should be a universal search/command palette.

Trigger:

- click search;
- `/` shortcut where appropriate;
- `Cmd/Ctrl + K`.

Search targets:

- team;
- team-season;
- metric;
- archetype;
- ranking route;
- compare action;
- matchup action.

Example:

```text
> 2019 LSU

2019 LSU                         Team season
Compare 2019 LSU                 Action
Simulate 2019 LSU                Action
Teams most similar to 2019 LSU   Exploration
```

Search should become the fastest way to move around SOAR.

---

# 8. Site information architecture

Recommended public structure:

```text
/
/teams
/teams/[team]/[season]
/rankings
/compare
/simulator         existing URL; public label can become “Matchup Lab”
/archetypes
/universe          new Team DNA experience
/metrics
/methodology       future or merged with metrics
```

Existing URLs should not be casually broken during redesign work.

---

# 9. Homepage: make the product undeniable

The homepage should stop explaining that files are ready and start demonstrating what SOAR can do.

## 9.1 Hero

The first screen should contain:

- SOAR Analytics brand;
- one strong product statement;
- global team search;
- a live or lightweight Team DNA visual;
- one obvious CTA to explore teams;
- one CTA to open the full Team DNA Universe.

Possible structure:

```text
SOAR ANALYTICS
See what a team really is.

Search any team-season across modern college football…
[ Search 2019 LSU, 2023 Michigan, 2020 Alabama... ]

                         interactive Team DNA field
                         ●     ●
                   ●                    ●
                              ●

[Explore Team DNA]     [View Rankings]
```

The visual should react to hover/search if feasible.

## 9.2 Featured insight strip

Below the hero, show several real data-driven editorial hooks, for example:

- strongest historical team currently in dataset;
- most unusual identity;
- strongest rushing team;
- strongest pass defense;
- closest historical twins;
- largest offense/defense imbalance.

These should come from real artifacts, not hard-coded copy.

## 9.3 “Choose your question” section

Keep the useful intent-based framing from the prototype, but present it as richer product modes:

- **Who is best?** → Rankings Lab
- **What is this team?** → Team profiles
- **Who would win?** → Matchup Lab
- **Who are they like?** → Team DNA Universe
- **How are they different?** → Compare

Each tile should have a mini visualization or meaningful visual state, not merely a white box with text.

## 9.4 Remove developer readiness from primary homepage

Artifact readiness, build commands, and local source paths do not belong in the normal fan homepage.

If needed, expose status in:

- development mode;
- a methodology/status page;
- internal diagnostics.

---

# 10. Team page: SOAR Team HQ

The team-season page should become the most important reusable page on the site.

A fan landing on `2023 Michigan`, `2019 LSU`, or `2021 Georgia` should immediately understand:

- historical strength;
- identity;
- strongest traits;
- weaknesses;
- historical neighbors;
- how the team evolved;
- how it compares to the field.

## 10.1 Team hero

The hero should include:

- year + team;
- team color accent;
- historical rank;
- model strength / field win rate;
- identity name;
- 2–4 strongest tags;
- Compare and Matchup actions.

Do not render three generic KPI boxes. Compose the section like a broadcast matchup graphic.

Example hierarchy:

```text
2023 MICHIGAN
CONTROLLED POWER

#8 historical power      96th percentile overall      +18.4 neutral-field edge

Methodical offense • elite pass defense • low volatility

[Compare] [Matchup Lab] [Find Similar Teams]
```

## 10.2 Team DNA fingerprint

Introduce a distinctive visual summary of team identity.

Possible forms:

- custom multi-axis profile;
- radial fingerprint;
- horizontal signed trait field;
- compact 2D projection around nearest teams.

Avoid default radar-chart styling unless it is substantially customized.

Core dimensions should reflect mature identity metrics only.

## 10.3 Strength stack

Show offense, defense, and style as a coherent visual stack rather than dozens of equal cards.

Example:

```text
OFFENSE                         DEFENSE
Pass efficiency    94           Pass defense      98
Run efficiency     87           Run defense       92
Explosiveness      91           Explosive prevent 95
Finishing          96           Finishing defense 90
```

Use percentile tracks, ranks, or distribution context.

## 10.4 Historical neighbors

Every team page should eventually answer:

> “Who is this team most like?”

Display 5–8 nearest team-seasons from the Team DNA embedding.

Each neighbor should show:

- season/team;
- similarity score or distance translated into understandable language;
- one reason they are similar;
- one major difference;
- link to profile.

This becomes one of SOAR’s most shareable features.

## 10.5 In-season trajectory

If snapshot data is available, show how a team’s identity moved across the season.

This can be represented as:

- a 2D mini trajectory;
- a sparkline-like identity path;
- a 3D path launch into the Universe;
- before/after trait comparison.

The goal is not merely “Week 4 vs Week 12.” It is:

> “How did this team become the team we remember?”

## 10.6 Signature strengths and pressure points

Translate the statistical profile into several high-signal bullets/cards:

- signature strength;
- second-order strength;
- biggest vulnerability;
- style constraint;
- consistency/volatility;
- late-season trajectory.

These must be derived from actual profile data.

## 10.7 Situational explorer

The existing situational explorer can become a premium interactive section rather than a utility panel.

Improve it with:

- clearer football-field visualization;
- animated line-of-scrimmage/first-down updates;
- percentile comparison;
- contextual leaderboard;
- “this team vs national baseline” mode;
- compact filter chips for down/distance/field position.

---

# 11. Team DNA Universe: signature SOAR experience

This should become the product feature users cannot find on a typical rankings site.

## 11.1 Concept

Every historical team-season is a point in learned football identity space.

The user should be able to rotate, zoom, search, filter, select, and follow relationships through that space.

## 11.2 Data contract

The coordinates must come from a documented modeling artifact.

V1 direction:

```text
opponent-adjusted identity snapshot features
  -> standardized feature vector
  -> compact learned embedding or validated dimensionality reduction
  -> 3D coordinates
```

Never use random coordinates or arbitrary x/y/z assignments simply to make a cool scene.

## 11.3 Default universe

Default point:

> final available snapshot for each team-season.

This keeps the first view legible.

Optional modes:

- all snapshots;
- selected season;
- selected conference;
- selected archetype;
- elite teams only;
- offense-heavy / defense-heavy filters.

## 11.4 Visual encoding

Potential encodings:

- position = Team DNA embedding;
- point size = historical strength;
- color = archetype/family or selected comparison mode;
- glow = selected/highlighted;
- trail = in-season movement;
- connection line = nearest-neighbor relationship or games played, depending on mode.

Do not encode too many variables simultaneously.

## 11.5 Selection experience

Selecting a team should:

1. smoothly focus the camera;
2. dim irrelevant nodes;
3. highlight nearest historical neighbors;
4. open an information rail;
5. show identity + rank + key traits;
6. allow “open team page,” “compare,” or “follow season trajectory.”

## 11.6 Search behavior

Typing `2019 LSU` should immediately locate and focus the node.

## 11.7 Trajectory mode

For a selected team-season:

- render chronological snapshot points;
- connect them with a path;
- allow a week scrubber;
- show which traits changed the most.

This is one of the most differentiated SOAR experiences.

## 11.8 Technical direction

Prefer a custom scene using:

- Three.js;
- React Three Fiber;
- Drei helpers.

Do not make Plotly the final signature experience if it visually constrains the product. Plotly remains acceptable for model exploration or rapid research, but the production experience should feel native to SOAR.

## 11.9 Performance

The Universe must progressive-load.

Requirements:

- core app shell renders without waiting on Three.js;
- dynamic import the heavy scene;
- send only fields required for the current visualization;
- use instancing for many nodes when appropriate;
- avoid thousands of independent React DOM labels;
- render labels selectively;
- offer lower-detail mode on mobile/low-power contexts.

## 11.10 Mobile

Do not force desktop 3D controls onto a phone.

Mobile may use:

- simplified 3D;
- 2D projection;
- searchable neighbor map;
- swipeable focused-team mode.

The analytical idea must survive even if the rendering changes.

---

# 12. Rankings Lab

The rankings page should become an exploration tool, not merely a sortable table.

## 12.1 Primary structure

```text
Rankings controls
Season / era / metric / identity filters

Top-level distribution visualization

Rank | Team | Year | Power | Field win | Offense | Defense | Identity
```

## 12.2 Features

- search;
- filter by season/era;
- filter by identity/archetype;
- sort by overall/offense/defense/style metric;
- percentile filters;
- sticky headers;
- quick compare selection;
- hover/focus preview;
- “show in Team DNA Universe.”

## 12.3 Visual companion

Add one strong chart above or alongside the table, such as:

- offense vs defense scatter;
- historical strength distribution;
- selected metric distribution;
- era comparison.

Selecting points should synchronize with table rows.

## 12.4 Ranking movement

When current-season data becomes live, support movement/change indicators. Do not fabricate movement for historical static datasets.

---

# 13. Compare experience

Comparison should feel like a matchup graphic, not two columns of copied cards.

## 13.1 Header

Use a split visual with:

- team colors;
- year/team names;
- historical ranks;
- identity labels;
- overall model strength.

## 13.2 Advantage map

For each key category, show a signed advantage toward one team.

Example:

```text
Passing offense      ←──────●────────→
Rushing offense      ←──────────●────→
Pass defense         ←──●────────────→
Explosiveness        ←────────●──────→
Finishing            ←─────●─────────→
```

The center is parity. Direction shows the advantage.

## 13.3 Similarity vs difference

Comparison should answer both:

- where are these teams similar?
- where are they fundamentally different?

Add a concise “What separates them” explanation based on largest standardized trait gaps.

## 13.4 Team DNA relationship

Show the two teams together in embedding space and report their distance/similarity.

---

# 14. Matchup Lab

Keep the existing simulator URL for compatibility if useful, but publicly frame the experience as **Matchup Lab**.

The page should make model uncertainty visible instead of pretending one score is destiny.

## 14.1 Matchup presentation

```text
2019 LSU                              2021 GEORGIA
         61% win probability
          projected 31–27

[ distribution / simulation density ]
```

## 14.2 Explain why

Below the result, surface the strongest matchup edges:

- pass offense vs pass defense;
- rush offense vs rush defense;
- explosiveness;
- finishing;
- field position;
- style conflict;
- pace/possession implications when supported.

## 14.3 Distribution, not fake certainty

If simulation outputs support it, show:

- win probability;
- expected margin;
- expected score;
- simulated margin distribution;
- upset tail;
- likely scoring ranges.

## 14.4 Replayability

Let users quickly swap:

- home/away/neutral;
- team-season;
- selected model mode if legitimate;
- reset/random historical matchup.

Do not turn this into a gambling interface unless the product direction explicitly changes in the future.

---

# 15. Identity / Archetype Explorer

The existing archetype research is a strong product differentiator and should become visual.

## 15.1 Explorer goals

Users should understand:

- what each archetype means;
- what teams exemplify it;
- what traits define it;
- how common it is;
- what archetypes sit nearby in Team DNA space.

## 15.2 Archetype page/card

Each identity should have:

- fan-facing name;
- concise description;
- signature traits;
- exemplar team-seasons;
- strength distribution;
- style spectrum;
- nearest related identity.

## 15.3 Avoid false taxonomy certainty

Archetypes are discovered from data. The UI should not imply the labels are eternal football laws.

Use language such as:

- “identity family”;
- “closest archetype”;
- “profile resembles...”

when uncertainty is material.

---

# 16. Metrics and methodology

The metrics page should become a trust surface.

Instead of a plain glossary, each metric can include:

- fan definition;
- why it matters;
- higher/lower direction;
- unit/denominator;
- example historical teams;
- distribution;
- current maturity status where appropriate;
- link to deeper methodology.

This is where SOAR can prove it is rigorous without forcing methodology onto every team page.

---

# 17. Editorial insight layer

SOAR should eventually produce small, shareable, automatically derived insights.

Examples:

- “2019 LSU’s closest offensive neighbor is 2020 Alabama.”
- “2023 Michigan is more defense-driven than 94% of elite historical teams.”
- “This team improved more in passing identity than any other top-20 team over its final six games.”

Rules:

- derive from actual metrics;
- preserve uncertainty;
- do not use LLM-generated prose as a substitute for deterministic ranking/comparison logic;
- optional LLM wording can sit on top of verified structured facts later.

---

# 18. Shareable graphics

Traffic will improve if SOAR creates outputs fans want to send to each other.

Future share formats:

- team DNA card;
- matchup result card;
- side-by-side comparison card;
- historical-neighbor card;
- ranking snapshot;
- “how this team changed” season path.

Cards should include:

- SOAR Analytics branding;
- team/year;
- 2–4 meaningful stats;
- one signature visual;
- URL/deep link.

Do not prioritize this before core pages are excellent.

---

# 19. Future product ideas

These are later-stage opportunities, not immediate requirements.

## 19.1 Season flight path

A dedicated page showing a team’s weekly movement through strength and identity space.

## 19.2 Historical twin finder

User selects a team and receives nearest team-season matches with explanations.

## 19.3 “Build your profile” fan quiz

Fans choose preferences such as explosive vs methodical, run vs pass, offense vs defense, and SOAR returns historical teams matching the chosen identity.

This can become a traffic feature without requiring user accounts.

## 19.4 Era explorer

Visualize how college-football styles shift over time.

Questions:

- Is passing identity becoming more homogeneous?
- Are elite defenses changing shape?
- Which archetypes disappear or emerge?

## 19.5 Conference identity map

Compare the distribution of team styles across conferences and eras.

## 19.6 Team lineage

Show how one program’s identity changes across coaches/seasons.

## 19.7 Live-season pulse

When current-season ingestion is production-ready:

- weekly movers;
- emerging identities;
- teams becoming more/less explosive;
- playoff-profile comparisons;
- current team vs historical comps.

---

# 20. Data architecture rules for the website

The Python side is authoritative.

The frontend should consume explicit generated artifacts through a stable adapter layer.

Preferred pattern:

```text
Python artifact
  -> website/lib data adapter
  -> typed view model
  -> React component
```

Do not do:

```text
Python artifact
  -> component manually reinterprets raw field names
  -> component reimplements metric math
```

## 20.1 View models

Create reusable UI models for concepts such as:

- TeamSummary;
- TeamIdentityProfile;
- RankingRow;
- MatchupResult;
- TeamNeighbor;
- TeamDNANode;
- TeamTrajectoryPoint;
- MetricDefinition.

This reduces coupling between raw JSON shape and UI composition.

## 20.2 Missing data

Use intentional states:

- feature unavailable;
- historical coverage unavailable;
- model not produced for this season;
- insufficient sample.

Do not show internal build instructions to fans.

---

# 21. Frontend component direction

The current frontend is intentionally small. As the product grows, move toward a structure like:

```text
website/
  app/
    universe/
    teams/
    rankings/
    compare/
    simulator/
    archetypes/
    metrics/
  components/
    shell/
      AppHeader.tsx
      MobileNav.tsx
      GlobalSearch.tsx
    ui/
      Button.tsx
      Pill.tsx
      Tooltip.tsx
      SegmentedControl.tsx
      MetricValue.tsx
    visualizations/
      PercentileBar.tsx
      AdvantageAxis.tsx
      DistributionPlot.tsx
      TeamDNAFingerprint.tsx
    universe/
      TeamDNAUniverse.tsx
      UniverseCanvas.tsx
      UniverseControls.tsx
      UniverseDetails.tsx
    team/
      TeamHero.tsx
      TeamStrengthStack.tsx
      TeamNeighbors.tsx
      TeamTrajectory.tsx
    matchup/
      MatchupHeader.tsx
      MatchupDistribution.tsx
      MatchupEdges.tsx
  lib/
    data.ts
    view-models/
    formatting/
```

Do not reorganize everything at once simply to match this tree. Migrate when a feature justifies the boundary.

---

# 22. Dependency strategy

The current site is intentionally dependency-light. Keep discipline while adding the tools required for a premium product.

Reasonable additions when needed:

- `three`
- `@react-three/fiber`
- `@react-three/drei`
- `motion`
- `lucide-react`
- `@tanstack/react-table`
- Playwright for browser/visual testing

For ordinary charts, first consider:

- custom SVG;
- CSS;
- focused D3 utilities.

Do not install a massive component system and inherit its look wholesale.

---

# 23. Performance requirements

Extraordinary does not mean heavy.

Priorities:

1. app shell and text content appear quickly;
2. heavy 3D loads progressively;
3. ranking/search interactions stay responsive;
4. mobile does not download unnecessary desktop-only visualization work;
5. selected-team changes do not trigger full-page reloads unnecessarily;
6. large datasets are trimmed to the fields required by the browser.

For Team DNA:

- prefer GPU instancing;
- avoid DOM labels for every point;
- use LOD or label culling;
- dynamically import the 3D bundle;
- keep selection state lightweight.

---

# 24. Accessibility requirements

SOAR should remain usable without perfect pointer/3D interaction.

Requirements:

- semantic headings;
- keyboard navigation;
- visible focus;
- high contrast;
- data not communicated by color alone;
- text alternatives for visual summaries;
- reduced-motion mode;
- non-3D access to selected Team DNA relationships;
- tables remain navigable and readable.

---

# 25. Public copy style

SOAR copy should be:

- confident;
- concise;
- football-aware;
- explanatory;
- skeptical of false precision.

Avoid:

- “revolutionary AI-powered insights”;
- “unlock the power of data”;
- generic startup slogans;
- unexplained acronyms in headlines;
- marketing claims the data cannot prove.

Prefer:

- “Elite against the pass.”
- “Wins with efficiency, not volume.”
- “Closest historical teams.”
- “Where the matchup tilts.”
- “How this team changed.”

---

# 26. What must disappear from the current pilot experience

As the redesign is implemented, remove or relocate these patterns:

- public “CFB Analytics Pilot” branding;
- white-page/admin-dashboard visual treatment;
- public data-readiness/build-path content on the homepage;
- identical bordered cards for every concept;
- developer-oriented missing-artifact instructions in fan-facing flows;
- dense pages with no visual hierarchy;
- arbitrary inline styles repeated throughout pages;
- navigation where every route has equal weight;
- generic metric tables without distribution/context.

Do not delete useful underlying functionality merely because its current presentation is weak.

---

# 27. Implementation roadmap for Codex

Do **not** ask an agent to “redesign the entire site” in one uncontrolled task.

Use these phases.

## Phase 0 — Foundation and brand reset

Goal: make every subsequent feature look like the same product.

Deliverables:

- rename public brand to SOAR Analytics;
- replace global light prototype theme;
- establish CSS variables/design tokens;
- build new application header/navigation;
- establish typography hierarchy;
- create reusable button/pill/metric primitives;
- remove public development diagnostics from homepage;
- build responsive shell;
- preserve existing route functionality.

Acceptance:

- Home, Teams, Rankings, Compare, Simulator, Archetypes, Metrics all share the SOAR shell.
- No public “CFB Analytics Pilot” branding remains.
- Desktop/mobile layouts are intentional.
- `npm run typecheck` and `npm run build` pass.

## Phase 1 — Extraordinary homepage

Goal: first-time users immediately understand SOAR is not a normal stats site.

Deliverables:

- premium hero;
- global team-season search;
- lightweight Team DNA visual/preview;
- featured real-data insights;
- richer intent-based product navigation;
- strong responsive composition;
- no developer readiness panel.

Acceptance:

- user can reach a team in one search action;
- homepage has one unmistakable signature visualization;
- no section looks like a default SaaS card grid;
- meaningful interactions work with keyboard and mobile.

## Phase 2 — Team HQ redesign

Goal: team pages become the core destination.

Deliverables:

- new team hero;
- identity/fingerprint visualization;
- strength stack;
- improved grade presentation;
- signature strengths/weaknesses;
- improved situational explorer presentation;
- placeholders/contracts for historical neighbors and trajectory if embedding data is not yet available.

Acceptance:

- fan understands team quality + identity within the first viewport or two;
- page is not a sequence of generic panels;
- unsupported metrics are not fabricated.

## Phase 3 — Team DNA model artifact + Universe

Goal: launch SOAR’s signature exploratory product.

Analytics deliverables:

- versioned embedding artifact;
- documented feature inputs;
- baseline comparison against PCA or other simple method;
- nearest-neighbor validation;
- stable IDs for team-season nodes;
- final-snapshot coordinates;
- optional in-season trajectory coordinates.

Frontend deliverables:

- `/universe` route;
- 3D scene;
- search;
- filters;
- selection rail;
- nearest neighbors;
- camera focus;
- Team HQ deep link;
- mobile/reduced-motion fallback.

Acceptance:

- coordinates are data-derived;
- selecting a team reveals sensible nearby teams;
- interaction stays performant with full historical node count;
- heavy 3D code is lazy-loaded.

## Phase 4 — Matchup Lab + Compare

Goal: make head-to-head exploration visual and explainable.

Deliverables:

- premium split-team header;
- probability/distribution visualization;
- projected margin/score presentation;
- matchup edge chart;
- compare advantage axes;
- Team DNA relationship between selected teams;
- fast team swapping.

Acceptance:

- result explains why, not just who;
- uncertainty is visible where supported;
- no gambling-style dark patterns.

## Phase 5 — Rankings Lab + Identity Explorer

Goal: make discovery addictive.

Deliverables:

- filterable ranking exploration;
- synced scatter/distribution chart;
- compare selection;
- show-in-Universe action;
- redesigned archetype explorer;
- exemplars and signature traits;
- strong cross-linking to team pages.

Acceptance:

- ranking page remains useful with thousands of rows;
- filters do not overwhelm the first screen;
- archetypes have understandable fan-facing explanations.

## Phase 6 — Polish, sharing, and product hardening

Deliverables:

- shareable team/matchup cards;
- metadata/social previews;
- browser regression tests;
- visual regression baseline;
- loading/skeleton/error states;
- performance audit;
- accessibility audit;
- mobile-specific refinements;
- analytics instrumentation if/when a product analytics provider is chosen.

---

# 28. Codex task prompts

These are intentionally scoped examples.

## Foundation

```text
Implement Phase 0 from docs/SOAR_ANALYTICS_WEBSITE_VISION.md.
Read AGENTS.md and website/AGENTS.md first. Preserve existing routes and data behavior. Rebrand the public UI as SOAR Analytics, establish the design system and application shell, and remove public prototype/developer presentation patterns. Run typecheck and build. Visually inspect desktop and mobile if browser tooling is available.
```

## Homepage

```text
Implement Phase 1 from docs/SOAR_ANALYTICS_WEBSITE_VISION.md on top of the current SOAR shell. Use real existing data adapters only. Build a visually distinctive homepage with global team search and a lightweight Team DNA preview. Do not invent data. Run typecheck/build and visually inspect 1440px and 390px layouts.
```

## Team page

```text
Implement Phase 2 for website/app/teams/[team]/[season]. Read the team profile and metric docs before changing presentation. Preserve all valid metrics, but redesign the page around team quality, identity, strength stack, and clear fan interpretation rather than equal card grids. Do not add unsupported metrics.
```

## Team DNA analytics

```text
Design and implement the versioned Team DNA embedding artifact described in Phase 3. Reuse the existing opponent-adjusted identity snapshot inputs. Build a simple baseline alongside the neural approach, validate nearest-neighbor stability and reconstruction/neighborhood preservation, and document the artifact contract before integrating it into the website.
```

## Universe

```text
Implement the /universe frontend from Phase 3 using the existing Team DNA artifact. Use a lazy-loaded custom React Three Fiber scene, search, selection, filtering, nearest-neighbor highlighting, and an accessible non-3D fallback. The scene must derive all coordinates from the artifact and remain performant with the complete historical dataset.
```

---

# 29. Review checklist for every major SOAR UI change

Before calling a UI task complete, ask:

### Product

- Does this help answer a real fan question?
- Is the strongest insight visually dominant?
- Does the page lead naturally to another useful action?

### Design

- Does this look authored or generated from a template?
- Are there too many equal-weight cards?
- Is motion communicating something?
- Is the hierarchy obvious without reading every label?

### Data

- Is every displayed value backed by an artifact?
- Did we preserve metric direction and meaning?
- Are missing states honest?

### Interaction

- Does keyboard use work?
- Does mobile feel intentionally designed?
- Is there accidental horizontal scroll?
- Are filters fast and understandable?

### Engineering

- Did we keep analytics logic out of React?
- Did we avoid unnecessary dependencies?
- Did typecheck pass?
- Did build pass?
- Did we visually inspect the changed route?

---

# 30. Final standard

SOAR should not try to beat other college-football analytics sites by displaying more columns.

It should win by making the underlying football structure visible.

The signature loop should eventually feel like this:

```text
Search a team
   ↓
Understand its identity
   ↓
See what makes it elite / flawed
   ↓
Discover historical neighbors
   ↓
Follow it into Team DNA space
   ↓
Compare it to another team
   ↓
Run the matchup
   ↓
Share the result
```

That is the product.

The website becomes extraordinary when the analytics, visual system, and interactions reinforce that loop—not when more decoration is added to the existing pilot.

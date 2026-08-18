# SOAR Analytics Frontend Instructions

These instructions apply to everything under `website/`.

## Read before editing

The product/design source of truth is:

- `../docs/SOAR_ANALYTICS_WEBSITE_VISION.md`

Also inspect the existing route/component/data-adapter implementation before replacing it. Preserve working user flows and data contracts unless the task explicitly changes them.

## Brand

The public product name is **SOAR Analytics**.

Do not use these as public brand names:

- CFB Analytics Pilot
- prediction-models
- College Football Analytics Pilot

The intended feel is **premium sports broadcast + flight/telemetry instrumentation**: precise, fast, dimensional, cinematic, and data-first. It must not look like a default component-library dashboard or an AI-generated crypto/SaaS landing page.

## Frontend architecture

- Keep football calculations in Python/generated artifacts.
- Treat `website/lib/` as the UI/data-adapter boundary.
- Build reusable view models when several routes need the same interpretation.
- Do not duplicate metric formulas in React components.
- Do not invent placeholder rankings, grades, win probabilities, or historical comparisons in production paths.
- Gracefully handle missing optional artifacts.

## Visual implementation rules

- Establish design tokens as CSS custom properties rather than scattering hard-coded colors.
- Prefer a small set of meaningful surface levels instead of dozens of bordered white cards.
- Make typography, spacing, contrast, and composition carry the hierarchy before adding decoration.
- Team colors are accents/context; SOAR’s global shell remains coherent across teams.
- Use one strong visualization per section rather than several weak mini-charts.
- Avoid gratuitous glassmorphism, neon cyberpunk effects, giant blurred gradients, decorative stock-photo football imagery, and emoji-as-icons.
- Use real icon components when icons are needed.
- Motion should explain state change, selection, ranking movement, trajectory, or spatial relationship.
- Respect `prefers-reduced-motion`.

## 3D / Team DNA

The Team DNA Universe is a signature experience, not background decoration.

- Default node = final historical team-season identity.
- In-season snapshots become an optional trajectory/trail mode.
- Spatial distance must come from a documented embedding/projection artifact, never random coordinates.
- Selection must expose meaningful nearest-neighbor/team details.
- Provide filtering and search outside the canvas.
- Provide a performant non-3D fallback for reduced-motion, low-power, or narrow-screen contexts when necessary.
- Progressive-load heavy 3D code so the core site remains usable quickly.

## Public-content rules

Normal users should not see messages such as:

- “run this Python command”
- “build this JSON”
- raw repository paths
- internal readiness/debug labels unless they are part of an explicit methodology/status surface

Turn those into intentional product empty states. Keep developer diagnostics available in development where useful.

## Responsive behavior

Every changed public route must be deliberately checked at approximately:

- desktop: 1440×900
- tablet: 1024×768
- mobile: 390×844

Do not merely stack desktop cards vertically. Recompose hierarchy for mobile, especially charts, tables, matchup layouts, and 3D controls.

## Accessibility

- Semantic landmarks and heading order.
- Visible keyboard focus.
- Keyboard-accessible controls.
- Useful text labels for visual-only controls.
- Adequate contrast.
- Do not rely on color alone to communicate ranking/advantage/status.
- Honor reduced motion.

## Performance

- Prefer server components for static/data-heavy shells when client state is not required.
- Isolate client components around interaction.
- Lazy-load expensive visualization code.
- Avoid shipping entire data corpora to the browser when a smaller view model will do.
- Virtualize or paginate very large ranking lists if needed.
- Do not add a dependency merely because it makes a demo faster to write; justify it against bundle and maintenance cost.

## Recommended dependency direction

Add only when the feature requires it:

- `three`, `@react-three/fiber`, `@react-three/drei` for the custom Team DNA Universe.
- `motion` for purposeful interface transitions.
- `lucide-react` for consistent icons.
- `@tanstack/react-table` if rankings/filtering complexity warrants it.
- Playwright as a dev dependency for route/visual regression checks when browser QA is being formalized.

Do not install a full UI kit and accept its default visual language as SOAR’s design system.

## Validation before finishing

At minimum:

```bash
npm run typecheck
npm run build
```

For visual work, use browser inspection/screenshots if available. Confirm there is no accidental horizontal scrolling, clipped controls, unreadable text, or layout breakage at the target widths.

## Implementation strategy

For large redesigns, follow the phases in `../docs/SOAR_ANALYTICS_WEBSITE_VISION.md`. Finish and validate a phase before sprawling into later ones unless the user explicitly asks for a cross-cutting implementation.

---
name: app-ui-alignment
description: Restyle a web application's interface (shell, toolbars, docked panels, forms, data grids, charts, maps, dialogs) so it follows a reference UI and a brand's palette, typography, and grid language, from an audit of the app's styling through owner decisions, a recorded spec, design tokens with tested contrast, third-party component theming, and browser verification in every theme. Use when someone asks to align, restyle, or re-theme a web app, dashboard, admin panel, or product demo (including desktop apps built on web technology, such as Electron or Tauri) to a design spec, a reference screenshot, or a sister site whose look the app should take (for example an MkDocs site styled with wiki-ui-alignment); to apply a design system or brand palette to an app; or to make a UI fix in such an app consistent with its recorded spec, drafting the spec first if none exists. For restyling MkDocs documentation sites themselves use wiki-ui-alignment instead.
---

# App UI alignment

Restyle a web application to a reference UI and a brand palette, without renaming the app, without changing what it
does, and without breaking any of its checks. An app is not a document: it is dense, stateful, themed at runtime, and
draws much of its interface through third-party components and canvases. The work runs in eight phases; do not skip
phase 3 (decisions) or phase 7 (verification).

The method extends `wiki-ui-alignment` (the same visual family, worked out on MkDocs sites) to applications. It was
tried on a React + Vite workbench (FlexLayout docking, AG Grid, ECharts, MapLibre, React Flow, React Aria Components,
six runtime appearances), once with the app's own design rules winning every conflict and once with the reference
winning; the pitfalls and library notes come from those runs. Re-check every library API against the versions the app
pins.

## Inputs to collect

- **The reference UI**: a screenshot, a URL, a sister site, or its design spec. It governs surfaces, framing, tab and
  label treatment, control shape, typography, and density.
- **The palette source of truth**: usually the sister site's live CSS. A spec's hex values are a snapshot, and values
  tested on a documentation page can fail on an app's surfaces.
- **The app's own design rules**: design guidelines, decision records, a design-alignment record, a token or appearance
  module. They are often stricter than the reference (fewer borders, fewer type sizes, several curated themes) and
  someone owns them.
- **The app's working rules**: `AGENTS.md`/`CLAUDE.md`, contribution guide, commit format and trailers, package policy,
  which files are generated or owner-maintained, and the checks that must pass before a commit.

## Hard rules

1. Keep the app's identity: name, logo, favicon, and wording stay unless the owner says otherwise. The EnergyAtlas
   mark (`references/brand/`) replaces a missing logo or favicon only when the owner chooses it (intake question 3a),
   and is never recoloured or redrawn.
2. Change appearance, not behaviour. No feature, data, workflow, or keyboard change rides along with a restyle; record
   any you find necessary and ask. Change case with CSS (`text-transform`), never by rewriting strings.
3. Settle precedence before implementing: where the reference conflicts with the app's own design rules, the owner
   decides which wins, conflict by conflict (phase 3). Never edit a document the project marks as owner-maintained;
   propose amendments in the record instead.
4. Every colour, font, size, radius, and shadow comes from a token. No literals in components; canvas renderers read the
   resolved tokens.
5. Contrast is tested, not eyeballed: text 4.5:1, large text and control borders 3:1, in every theme the app ships.
   That holds in every state, not only at rest: a hovered, selected, pressed, or focused tab, handle, button, row, or
   menu item keeps its label at 4.5:1 against the state's own background and shows the state with an indicator (edge,
   underline, outline, or fill boundary) of at least 3:1 against what surrounds it, so each state is told apart from
   rest and from the others. A colour change alone, or a tint a step away from the strip, is not enough.
   Control kinds are told apart too: text fields, selects, and buttons differ in at least two of fill, edge, and
   content (`references/translation.md`, "Controls"), so a square, flat reference does not turn them into one box.
6. Labels are set through label tokens (font, case, size, tracking, weight), and by default as written in the
   interface sans; the reference's mono caps are an opt-in the owner sees on the running app. Labels that carry units,
   identifiers, or data keep their case whatever the style: uppercase turns `m²` into `M²` and `kWh` into `KWH`.
   Titles are not labels: page, panel, card, form, dialog, and section titles inside a panel's content keep the app's
   title style and sit on the pane without a backdrop strip, unless the owner asks for strips.
7. No runtime requests to font hosts or CDNs: fonts come from the app's own bundle. Data services the app already uses
   (map tiles, APIs) are not part of this rule.
8. The app's own checks pass before every commit you hand back: typecheck, lint, format, unit, browser, and
   accessibility tests, whatever the project defines.
9. Follow the project's commit rules over any tool default (format, scope, and whether trailers or attribution are
   allowed). Push, merge, tag, and release only with the owner's explicit yes for each.
10. Ask before each decision in `references/intake-questions.md` that the owner has not settled; record every answer.

## Phase 1: read the app

- Stack and styling method: framework, bundler, CSS modules, Sass, Tailwind, CSS-in-JS, a component library and its
  theming API.
- The token system: where colours, fonts, and sizes are defined; how themes switch (a `data-theme` attribute, a class,
  JavaScript writing custom properties, a theme provider); how the first frame avoids a flash; where the preference is
  stored.
- **How each token role is used.** Grep each surface token: which one paints the content panes, which the gutters
  behind them, which hover and headers. The reference's surfaces are mapped onto these uses, not onto token names.
- Third-party surfaces and how each is themed now: docking or layout manager, data grid, charts, maps, flow diagrams,
  code editors, date pickers. List what renders to canvas or WebGL: those cannot read CSS variables.
- Fonts: how they load (npm font packages, vendored files, a font host) and their fallbacks; whether the project limits
  its monospace to code.
- The app's checks and how to run them; the browser tests, their fixtures (network stubs, seeded data), and whether they
  include accessibility checks.
- The review surfaces: every page, panel, dialog, menu, and empty, loading, warning, and error state. Most of a
  workbench is empty until a workflow runs, so plan a **populated state** you can reproduce (a seed, a fixture, a saved
  project, a Playwright storage state) before taking screenshots.
- Start the dev server in the background, on a port no other checkout uses, and open the app in a browser you can
  drive.

## Phase 2: audit

- Run `scripts/style_audit.py` over the source, with the token files passed as `--tokens` and generated or spike code
  excluded. It counts colour literals outside the tokens, font sizes and families (with locations of sizes that are not
  tokens), borders, radii, elevation and edge shadows, uppercase labels, letter spacing, motion, `!important`, and
  font-host URLs: the factual "observed gaps" table. Run it on the stylesheets of the docking and grid libraries too, to
  list the radii and transitions the app will have to override.
- Take baseline screenshots of the review surfaces, populated, in every theme at the app's minimum supported desktop
  size and one large size (`references/verification.md`, "Screenshot matrix").
- Fill the translation table (`references/translation.md`): for each element of the reference, its app equivalent and
  whether to keep, adapt, or drop it. Mark every conflict with the app's own design rules.
- Compute contrast for the reference palette on the app's surfaces with `scripts/contrast.py check --suggest`,
  including derived tints, the selection tint, and any outline drawn on a fill.

## Phase 3: settle the decisions

Ask the owner the questions in `references/intake-questions.md` that the inputs leave open, each with a recommendation
and the evidence from phase 2. Precedence comes first: for each conflict, does the app's rule or the reference win?
Typical conflicts: border density, the number of type sizes, a second monospace family, the theme set (a reference
light/dark pair against several curated appearances), and corner radii. The label style is decided separately from
precedence: the reference may win on where labels go and still lose on how they are set.

If the owner cannot choose without seeing it, build the options as variants: one branch (or worktree) per option from
the same base, the same review surfaces screenshotted in each, presented side by side. Merge none of them until the
owner picks.

## Phase 4: record the spec

- Record it where the project records design decisions. With a decision record and an alignment record, put the
  decisions and values in the decision record, and the audit, translation table, deviations, status, and evidence in
  the alignment record. Without them, write a spec outside any published folder (`design/ui-design-spec.md`). Use
  `references/spec-decisions-template.md`.
- Separate observed facts (with file paths and counts from the audit) from decisions and from recommendations.
- If the reference wins over owner-maintained guidelines, write the amendments those guidelines would need into the
  record for the owner; do not edit the guidelines.
- If the reference image may not be committed, describe it in words.
- Add one rule to the project's agent instructions, unless the owner declines: UI changes follow the recorded spec.
- Commit the record before the styling, marked as decided before implementation; its deviations section is filled at
  the end (phase 8).

## Phase 5: tokens and contrast

Follow `references/token-recipes.md`:

- One semantic token set with the same names in every theme: surfaces (pane, background, raised, overlay), text, muted
  text, split borders (`border-subtle` for decorative rules, `border-interactive` for controls, at least 3:1 on every
  surface a control sits on), accent, accent text, text on accent, focus, selection, and tone pairs (success, info,
  warning, danger, neutral: text and tint). New roles go into every theme, curated ones included.
- A separate data palette for charts and maps (categorical, sequential, no-data, de-emphasis, selection), each mark at
  least 3:1 against the chart surface.
- A contrast test in the app's own test runner that iterates every theme and every pair, so a later token change cannot
  regress it.
- Map every third-party theme onto the tokens, never onto literals.

## Phase 6: implement

In layers, checking the app after each one (`references/third-party-theming.md` for the libraries):

1. **Fonts**: from the bundle (npm font packages, or vendored WOFF2 with licences); one family token per role; tabular
   numerals where numbers align. **Brand mark**, if chosen: the favicons in the bundler's public folder, linked from
   `index.html` under the base path, and the mark before the product name in the title bar
   (`references/brand/README.md`, "Web applications").
2. **Tokens**: palette values per theme; the first-frame fallback; the theme switch writes the same names. A shared
   rule token (`--rule: 1px solid var(--color-border-subtle)`) keeps framing edits to one word each, and the label
   tokens keep the label style one decision.
3. **Shell chrome**: title bar, menu bar or ribbon, tab strips, status bar, pane boundaries and splitters. This is where
   most of the reference's identity lands: the active-tab treatment, label typography, rules. Check after this layer
   that every tab still fits at the minimum size with side panels open.
4. **Controls**: buttons (primary, secondary, quiet, destructive), inputs, selects, checkboxes, radios, switches,
   sliders, split buttons; hover, focus-visible, pressed, selected, disabled-with-reason, and invalid states. Apply the
   control grammar (fields are wells, buttons are raised blocks) through control tokens.
5. **Panels and docking**: panel headers, toolbars, trees and lists, the docking library's tabs, borders, popouts, and
   drop indicators. Full-bleed header strips inside padded panels need negative margins equal to the padding.
6. **Data surfaces**: data grid, charts (scaffolding, labels, tooltips, legends), map (basemap colours, overlays,
   legend, popups, controls), diagrams.
7. **Overlays and states**: menus, popovers, tooltips, dialogs, command palette, toasts, notices, empty, loading, and
   error states. On a black surface a shadow does nothing: overlays need a lighter surface and a rule.
8. **Motion**: short transitions on colour only; none under `prefers-reduced-motion: reduce`, libraries' own
   transitions included.

Keep each layer a reviewable commit. Run `scripts/style_audit.py` again at the end: literals outside tokens should be
zero or each one explained. Counts are evidence, not goals: a grid-framed alignment adds borders on purpose.

## Phase 7: verify in a browser

Run the project's checks, then the checks in `references/verification.md`:

- every theme, at the minimum and a large desktop size (and phone width only if the app supports it);
- fonts load from the app's own origin; no request to a font host or CDN;
- no horizontal page overflow; panes scroll inside themselves; no clipped or ellipsized labels in tab strips, ribbons,
  headers, or grid headers;
- focus is visible on every control in tab order, including inside docked panels and the grid;
- every interactive kind (tabs, side handles, buttons, menu items, rows, tree items) is hovered, selected, and pressed
  in every theme, and each state passes the state check in `verification.md`;
- in a greyscale screenshot of a form and a toolbar, every field, select, and button is identified without colour;
- switching theme at runtime restyles every surface, canvases included, without a reload or a stale colour;
- the first frame after a reload shows the stored theme, not a flash of the default (check against a production build);
- accessibility checks (axe or the project's equivalent) report no serious or critical violation in any theme; a
  finding that the base branch already had is logged, not silently fixed or ignored;
- before and after screenshots of the review surfaces, compared by eye (the priority subset in `verification.md`).

Fix and re-verify before reporting. Read `references/pitfalls.md` when a check fails in a confusing way.

## Phase 8: hand back and ship

- Commit in the project's format, in reviewable steps: record, tokens and contrast test, fonts, each layer, each fix.
- Update the alignment record with what was built, deviations and why, verification evidence (commands, counts, test
  totals), and remaining gaps.
- When the owner will merge: fetch first, since the base branch often moves during a restyle; merge it in, re-run every
  check, and look at the base branch's new surfaces in the new design.
- Push, merge, and tag only with the owner's yes for each. A restyle is not a release.
- Report what changed, every deviation from the reference and why, the screenshots the owner should look at, and what
  remains.

## References

- `references/intake-questions.md`: decision questions, precedence first, with recommended defaults.
- `references/spec-decisions-template.md`: the decisions section of the spec or decision record.
- `references/translation.md`: reference elements and their app equivalents, the label style, and pane mapping.
- `references/token-recipes.md`: token layers, runtime themes, the contrast test, the family palette tested for apps.
- `references/third-party-theming.md`: docking layouts, data grids, charts, maps, diagrams, component libraries.
- `references/verification.md`: checks, browser snippets, a screenshot matrix, and a populated state.
- `references/pitfalls.md`: failures met in practice and their fixes.
- `references/brand/`: the EnergyAtlas mark (white-E and knockout SVGs, favicons) and its README: use, placement, and
  the MkDocs and web-app recipes.
- `scripts/brand_assets.py`: renders the PNG and ICO favicons from the mark's SVG with a headless browser.
- `scripts/style_audit.py`: styling inventory (`python style_audit.py SRC --tokens GLOB ... --exclude GLOB ...`).
- `scripts/contrast.py`: contrast of token pairs per theme with suggestions (`check PAIRS.json --suggest
  [--failures-only]`), one pair (`ratio FG BG`), tints (`mix A B AMOUNT`), and stylesheet tokens (`css-tokens FILE`).

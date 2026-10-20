---
name: app-ui-alignment
description: Restyle a web application's interface (shell, toolbars, docked panels, forms, data grids, charts, maps, dialogs) so it follows a reference UI and a brand's palette, typography, and grid language, from an audit of the app's styling through owner decisions, a recorded spec, design tokens with tested contrast, third-party component theming, and browser verification in every theme. Use when someone asks to align, restyle, or re-theme a web app, dashboard, or product demo to a design spec, a reference screenshot, or a sister site (for example a documentation site styled with wiki-ui-alignment), to apply a design system or brand palette to an app, or to keep later UI fixes consistent with the app's recorded spec. For MkDocs documentation sites use wiki-ui-alignment instead.
---

# App UI alignment

Restyle a web application to a reference UI and a brand palette, without renaming the app, without changing what it
does, and without breaking any of its checks. An app is not a document: it is dense, stateful, themed at runtime, and
draws much of its interface through third-party components and canvases. The work runs in eight phases; do not skip
phase 3 (decisions) or phase 7 (verification).

The method extends `wiki-ui-alignment` (the same visual family, worked out on MkDocs sites) to applications, and was
tried on a React + Vite workbench with docked panels, a data grid, canvas charts, and a WebGL map. Recipes are in
`references/`; re-check every library API against the versions the app pins.

## Inputs to collect

- **The reference UI**: a screenshot, a URL, a sister site, or its design spec. It governs surfaces, framing, tab and
  label treatment, control shape, typography, and density.
- **The palette source of truth**: usually the sister site's live CSS. A spec's hex values are a snapshot.
- **The app's own design rules**: design guidelines, decision records, a design-alignment record, a token or appearance
  module. They are often stricter than the reference (fewer borders, fewer type sizes, several curated themes) and
  someone owns them.
- **The app's working rules**: `AGENTS.md`/`CLAUDE.md`, contribution guide, commit format and trailers, package policy,
  which files are generated or user-maintained, and the checks that must pass before a commit.

## Hard rules

1. Keep the app's identity: name, logo, favicon, and wording stay unless the owner says otherwise.
2. Change appearance, not behaviour. No feature, data, workflow, or keyboard change rides along with a restyle; record
   any you find necessary and ask.
3. Settle precedence before implementing: where the reference conflicts with the app's own design rules, the owner
   decides which wins, conflict by conflict (phase 3). Never edit a document the project marks as owner-maintained.
4. Every colour, font, size, radius, and shadow comes from a token. No literals in components; canvas renderers read the
   resolved tokens.
5. Contrast is tested, not eyeballed: text 4.5:1, large text and control borders 3:1, in every theme the app ships.
6. No runtime requests to font hosts or CDNs: fonts come from the app's own bundle. Data services the app already uses
   (map tiles, APIs) are not part of this rule.
7. The app's own checks pass before every commit you hand back: typecheck, lint, format, unit, browser, and
   accessibility tests, whatever the project defines.
8. Follow the project's commit rules over any tool default (format, scope, and whether trailers or attribution are
   allowed). Push, merge, tag, and release only with the owner's explicit yes for each.
9. Ask before each decision in `references/intake-questions.md` that the owner has not settled; record every answer.

## Phase 1: read the app

- Stack and styling method: framework, bundler, CSS modules, Sass, Tailwind, CSS-in-JS, a component library and its
  theming API.
- The token system: where colours, fonts, and sizes are defined; how themes switch (a `data-theme` attribute, a class,
  JavaScript writing custom properties, a theme provider); how the first frame avoids a flash; where the preference is
  stored.
- Third-party surfaces and how each is themed now: docking or layout manager, data grid, charts, maps, flow diagrams,
  code editors, date pickers. List what renders to canvas or WebGL: those cannot read CSS variables.
- Fonts: how they load (npm font packages, vendored files, a font host) and their fallbacks.
- The app's checks and how to run them; the browser tests and whether they include accessibility checks and
  screenshots.
- Start the dev server in the background and open the app in a browser you can drive. Record the surfaces to review:
  every page, panel, dialog, menu, and empty, loading, warning, and error state you can reach.

## Phase 2: audit

- Run `scripts/style_audit.py` over the source, with the token files passed as `--tokens` and generated or spike code
  excluded. It counts colour literals outside the tokens, font sizes and families, borders, radii, shadows, motion,
  `!important`, and font-host URLs: the factual "observed gaps" table.
- Take baseline screenshots of the review surfaces in every theme at the app's minimum supported desktop size and one
  large size (`references/verification.md`, "Screenshot matrix"). Keep them outside the repository unless the project
  stores screenshots.
- Fill the translation table (`references/translation.md`): for each element of the reference, its app equivalent and
  whether to keep, adapt, or drop it. Mark every conflict with the app's own design rules.
- Compute contrast for the reference palette on the app's surfaces with `scripts/contrast.py`.

## Phase 3: settle the decisions

Ask the owner the questions in `references/intake-questions.md` that the inputs leave open, each with a recommendation
and the evidence from phase 2. Precedence comes first: for each conflict, does the app's rule or the reference win?
Typical conflicts: border density, the number of type sizes, a second monospace family, the theme set (a reference
light/dark pair against several curated appearances), uppercase mono labels at high density, and corner radii.

If the owner cannot choose without seeing it, build the options as variants: one branch (or worktree) per option from
the same base, the same review surfaces screenshotted in each, presented side by side. Merge none of them until the
owner picks.

## Phase 4: record the spec

- Record it where the project records design decisions: a decision record and an alignment record if it keeps them
  (`docs/decisions/`, `docs/design-alignment.md`), otherwise a spec outside any published folder
  (`design/ui-design-spec.md`). Use `references/spec-decisions-template.md` for the decisions section, which wins over
  the rest.
- Separate observed facts (with file paths and counts from the audit) from decisions and from recommendations.
- If the reference image may not be committed, describe it in words.
- Add one rule to the project's agent instructions, unless the owner declines: UI changes follow the recorded spec.
- Commit the record before the styling, so review can start from it.

## Phase 5: tokens and contrast

Follow `references/token-recipes.md`:

- One semantic token set with the same names in every theme: surfaces, text, muted text, split borders
  (`border-subtle` for decorative rules, `border-interactive` for controls, at least 3:1), accent, accent text, text on
  accent, focus, selection, and tone pairs (success, info, warning, danger, neutral: text and tint).
- A separate data palette for charts and maps (categorical, sequential, no-data, de-emphasis, selection), each mark at
  least 3:1 against the chart surface.
- A contrast test in the app's own test runner that iterates every theme and every pair, so a later token change cannot
  regress it.
- Map every third-party theme onto the tokens, never onto literals.

## Phase 6: implement

In layers, checking the app after each one (`references/third-party-theming.md` for the libraries):

1. **Fonts**: from the bundle (npm font packages, or vendored WOFF2 with licences); one family token per role; tabular
   numerals where numbers align.
2. **Tokens**: palette values per theme; the first-frame fallback; the theme switch writes the same names.
3. **Shell chrome**: title bar, menu bar or ribbon, tab strips, status bar, pane boundaries and splitters. This is where
   most of the reference's identity lands: the active-tab treatment, label typography, rules.
4. **Controls**: buttons (primary, secondary, quiet, destructive), inputs, selects, checkboxes, radios, switches,
   sliders, split buttons; hover, focus-visible, pressed, selected, disabled-with-reason, and invalid states.
5. **Panels and docking**: panel headers, toolbars, trees and lists, the docking library's tabs, borders, popouts, and
   drop indicators.
6. **Data surfaces**: data grid, charts (scaffolding, labels, tooltips, legends), map (basemap colours, overlays,
   legend, popups), diagrams.
7. **Overlays and states**: menus, popovers, tooltips, dialogs, command palette, toasts, notices, empty, loading, and
   error states.
8. **Motion**: short transitions on colour only; none under `prefers-reduced-motion: reduce`.

Keep each layer a reviewable commit. Run `scripts/style_audit.py` again at the end: literals outside tokens should be
zero or each one explained.

## Phase 7: verify in a browser

Run the project's checks, then the checks in `references/verification.md`:

- every theme, at the minimum and a large desktop size (and phone width only if the app supports it);
- fonts load from the app's own origin; no request to a font host or CDN;
- no horizontal page overflow; panes scroll inside themselves; no clipped labels in tab strips, ribbons, or headers;
- focus is visible on every control in tab order, including inside docked panels and the grid;
- switching theme at runtime restyles every surface, canvases included, without a reload or a stale colour;
- the first frame after a reload shows the stored theme, not a flash of the default;
- accessibility checks (axe or the project's equivalent) report no serious or critical violation in any theme;
- before and after screenshots of every review surface, compared by eye.

Fix and re-verify before reporting. Read `references/pitfalls.md` when a check fails in a confusing way.

## Phase 8: hand back and ship

- Commit in the project's format, in reviewable steps: record, tokens and contrast test, fonts, each layer, each fix.
- Update the project's alignment record with what was built, deviations and why, verification evidence (commands,
  counts, test totals), and remaining gaps.
- Before merging, fetch: the base branch often moves during a restyle. Merge it in, re-run every check, and look at the
  base branch's new surfaces in the new design.
- Push, merge, and tag only with the owner's yes for each. A restyle is not a release.
- Report what changed, every deviation from the reference and why, the screenshots the owner should look at, and what
  remains.

## References

- `references/intake-questions.md`: decision questions, precedence first, with recommended defaults.
- `references/spec-decisions-template.md`: the decisions section of the spec or decision record.
- `references/translation.md`: reference elements and their app equivalents, with defaults per precedence.
- `references/token-recipes.md`: token layers, runtime themes, the contrast test, an example family palette.
- `references/third-party-theming.md`: docking layouts, data grids, charts, maps, diagrams, component libraries.
- `references/verification.md`: checks, browser snippets, and a screenshot matrix.
- `references/pitfalls.md`: failures met in practice and their fixes.
- `scripts/style_audit.py`: styling inventory (`python style_audit.py SRC --tokens GLOB ... --exclude GLOB ...`).
- `scripts/contrast.py`: contrast of token pairs per theme, with suggestions (`python contrast.py check PAIRS.json
  --suggest`; `python contrast.py css-tokens FILE.css` to seed the themes).

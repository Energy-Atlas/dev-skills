---
name: wiki-ui-alignment
description: Restyle an MkDocs (Material for MkDocs) documentation site so it follows a reference UI and a brand's palette, typography, and grid language, from intake questions through a recorded design spec, implementation, browser verification, and merge. Use when someone hands over a UI design spec, a reference screenshot, or a sister site whose look an MkDocs wiki or docs site should adopt; when they ask to "align the UI", "restyle the docs", "make the wiki look like X", or to apply a design system to MkDocs; and when later UI fixes on such a site must stay consistent with its recorded spec.
---

# Wiki UI alignment

Restyle an MkDocs + Material site to a reference UI and a brand palette, without renaming the site, without touching
generated content, and without breaking `mkdocs build --strict`. The work runs in eight phases; do not skip phase 2
(decisions) or phase 7 (verification).

The method was worked out on the BEMGen documentation site (Material 9.7, MkDocs 1.6), aligned to the EnergyAtlas Wiki
palette and an editorial, grid-framed reference UI. Its recipes are in `references/`; re-check selectors against the
Material version the target site pins.

## Inputs to collect

- **The reference UI**: a screenshot, a URL, or both. It governs grid framing, borders, card construction, typography
  hierarchy, spacing, and navigation character.
- **The palette source of truth**: usually a live sister site's CSS (`assets/css/main.css` or similar). A Markdown spec's hex
  values are a snapshot; the live CSS wins when they diverge, except where contrast fixes override it.
- **A design spec**, if the owner has one (often a Markdown file). If not, write one in phase 3.
- **The site's own rules**: its `AGENTS.md`/`CLAUDE.md`, which files are generated (never hand-edit those), the commit
  format, and who may push.

## Hard rules

1. Keep the site's identity. Visual-family alignment is not a rename: keep the site name, logo, and favicon unless the
   owner says otherwise.
2. Never commit the reference image if the owner says not to. Describe it in words in the spec instead (phase 3).
3. Never hand-edit generated pages. Style them through CSS only; change layout only on hand-written pages.
4. `mkdocs build --strict` passes before every commit you hand back. Keep the site's `validation:` block.
5. No runtime requests to font hosts or CDNs: self-host fonts (phase 5).
6. Push, merge, tag, and release only with the owner's explicit yes for that action. A yes to push is not a yes to tag.
7. Ask before each decision in `references/intake-questions.md` that the owner has not settled; record every answer.

## Phase 1: read the site

- `mkdocs.yml`: `theme.features`, `palette`, `font`, `custom_dir`, `extra_css`, `plugins`, `markdown_extensions`
  (`attr_list` and `md_in_html` are required by the recipes), `nav`, `validation`.
- `requirements.txt`: the pinned MkDocs and Material versions. Find the installed theme's CSS and templates
  (`<venv>/Lib/site-packages/material/templates/`) and grep the rules you will override; selectors and breakpoints
  change between Material versions.
- The hand-written pages that will change layout: the landing page and the section index pages.
- Existing stylesheets and overrides; keep anything that encodes a recorded decision.
- Set up a local server you can keep running (`mkdocs serve`, ideally through the project's serve script) and open it
  in a browser you can drive.

## Phase 2: settle the decisions

Review the spec and reference, then ask the owner the questions in `references/intake-questions.md` that the inputs
leave open. Typical gaps: a "provided reference" that was never attached, a palette source named but not linked, brand
(rename or family alignment), default theme, font hosting, hero scope, numbered strips scope, contrast failures, width
exceptions, breadcrumbs, and the role of the brand's red. Recommend an option for each; do not implement before the
answers arrive if the owner asked for review first.

Compute contrast before asking: run the script in `references/verification.md` over every text/background and
border/background pair of the palette. Report failures with ratios.

## Phase 3: record the spec

- Save the spec in the repository but outside `docs_dir` (for example `design/ui-design-spec.md`), so it is versioned and
  never published.
- Open it with a **section 0, implementation decisions**, that wins over the rest. Use
  `references/spec-decisions-template.md`. Update the token blocks of the body to the adjusted values, so the document
  never contradicts itself.
- If the reference image may not be committed, write section 0.x "The reference, described": surface colours, page frame,
  header, section strips, hero, cell rows, buttons, and what is deliberately *not* adopted.
- Add one rule to the project's agent instructions (`AGENTS.md` or equivalent): UI and visual styling changes must follow
  the spec; its section 0 wins; the design folder is not part of the site. Add new hand-maintained asset folders (fonts) to
  any ownership table.
- Commit the spec as received first, then the decisions, as two commits.

## Phase 4: tokens and contrast

- Define tokens with one neutral prefix (`--ui-` in the recipes; pick one per site) per Material scheme:
  `[data-md-color-scheme="slate"]` and `[data-md-color-scheme="default"]`.
- Give light and dark surfaces the same token names in the same order of emphasis, so components never branch on theme.
- Split borders: `--ui-border-subtle` for decorative grid rules (may stay below 3:1) and `--ui-border-interactive` for
  controls (at least 3:1). Darken muted text until it reaches 4.5:1 on every surface it sits on. A deep brand colour that
  fails on dark backgrounds becomes a fill only.
- Map Material's variables onto the tokens (`references/material-recipes.md`, "Tokens"). Set `primary: custom` and
  `accent: custom` in the palette, keep the system-preference toggle unless told otherwise.

## Phase 5: implement

Follow `references/material-recipes.md` section by section. In order:

1. **Fonts**: vendor the WOFF2 subsets (Latin, Latin Extended) with their OFL licences into `docs/assets/fonts/`,
   declare them in `fonts.css`, set `theme.font: false`, and preload the two most-used files from
   `overrides/main.html`. Do not rely on Material's `privacy` plugin on Windows: it creates symbolic links, Windows refuses
   them, and its warning fails the strict build.
2. **Page frame**: wider `.md-grid`, the content column bounded by two thin vertical rules, `scrollbar-gutter: stable`.
3. **Gutter and insets**: one `--ui-gutter` variable equal to Material's article margin, and `--ui-inset-left/right`
   equal to a hidden sidebar's width, so a page that hides its sidebars (the landing page) keeps their width as empty
   margins and its text lines up with every other page.
4. **Chrome**: header, tabs (mono uppercase; active tab inverted in a thin accent outline), progress bar, search,
   breadcrumbs (`navigation.path`), sidebars, table of contents, footer, back-to-top.
5. **Content**: typography in `rem` (Material scales its root font size at breakpoints), prose measure, links, code,
   tables, admonitions (semantic edge colours), buttons, content tabs.
6. **Overview components**: numbered section strips on `##` headings via `attr_list`; Material's `grid cards` markup
   restyled as one shared-border grid with clickable cells; a restrained hero with a container-query-sized headline.
7. **Stable navigation**: `navigation.instant` and `navigation.instant.progress`, so page changes do not reload fonts,
   sidebars, and scrollbars.
8. **Reduced motion**: drop transitions under `prefers-reduced-motion: reduce`.

Then change the hand-written overview pages (`references/material-recipes.md`, "Markup"): hero and grid on the landing
page, strips and grids on the section index pages. Keep every heading anchor that other pages link to (grep for
`page.md#anchor` before renaming headings); prefer styling an existing `##` heading as a strip over replacing it.

## Phase 6: build

Run the strict build after each step that changes `mkdocs.yml` or templates. Restart the dev server after changing
`custom_dir`, `plugins`, or `theme.features`; its live reload does not always pick them up.

## Phase 7: verify in a browser

Run the checklist and snippets in `references/verification.md`:

- dark and light (clear Material's stored palette choice first), desktop width (1440), and phone width (375);
- fonts load from the site's own origin and no request leaves it;
- no horizontal page overflow; wide tables scroll inside their own container;
- text alignment: hero, strip labels, cell text, and paragraphs share one left edge on pages with and without sidebars;
- strips and grid rules run from frame to frame; every clickable cell is closed on all four sides;
- clickable cells: the empty area navigates to the title's target, inner links keep their own;
- instant navigation: clicking a link keeps the same document and does not re-request fonts;
- search, breadcrumbs, admonitions, and a generated reference page with wide tables.

Fix and re-verify before reporting. Read `references/pitfalls.md` when a check fails in a confusing way.

## Phase 8: hand back and ship

- Commit in the project's format, in reviewable steps: spec, styling system, page layouts, then each fix.
- Before merging, fetch: the base branch often moved while the redesign was in progress. Merge it in, resolve conflicts
  by keeping the new layout and folding in the base branch's content edits, re-run the build and tests, and check the
  base branch's new pages in the new design.
- Push, merge, and tag only with the owner's yes for each. A redesign is not a product release: if the project reserves
  version tags for releases, ask what to tag, or whether to tag at all.
- Report what changed, every deviation from the spec and why, and what the owner should look at.

## References

- `references/intake-questions.md`: the decision questions, with recommended defaults.
- `references/spec-decisions-template.md`: the section 0 template for the spec.
- `references/material-recipes.md`: configuration, template override, CSS recipes, and Markdown markup.
- `references/verification.md`: contrast script, font vendoring script, and browser checks.
- `references/pitfalls.md`: failures met in practice and their fixes.

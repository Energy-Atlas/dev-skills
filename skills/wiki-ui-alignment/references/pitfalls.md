# Pitfalls

Failures met while aligning a Material for MkDocs site, with their causes and fixes.

## Fonts and loading

- **The `privacy` plugin fails the strict build on Windows.** It saves the extensionless Google Fonts CSS URL behind a
  symbolic link; Windows refuses symbolic links without developer mode, the plugin warns
  `Couldn't create symbolic link`, and `--strict` aborts. Vendor the fonts instead (`verification.md`). It also leaves a
  `.cache/` folder: delete it.
- **Text flickers and the layout jumps on every page change.** `mkdocs serve` sends no caching headers, so every full
  page load downloads the fonts again and swaps them in after the first paint; sidebars and tables show and hide their
  scrollbars while the layout settles. Fix all three causes: `navigation.instant` (no full reloads), preloaded fonts
  (`overrides/main.html`), and `html { scrollbar-gutter: stable; }` (short and long pages keep the same width).
- **`theme.font` loads Google Fonts.** Set it to `false` when the fonts are self-hosted, and set `--md-text-font` and
  `--md-code-font` in CSS.

## Theme and specificity

- **Light mode still shows dark.** Material stored the scheme it chose on an earlier visit in `localStorage`; clear the
  `__palette` key and reload (`verification.md`).
- **A rule has no effect.** Material's per-type and layout rules are specific: `.md-typeset .admonition.note`
  (admonition colours) and `[dir=ltr] .md-sidebar--primary:not([hidden])~.md-content>.md-content__inner` (article
  margins). Match or exceed their specificity (`[class]`, `[dir]`, extra classes) rather than using `!important`.
- **Sizes in `px` stop scaling.** Material changes the root font size at 100em and 125em; write `rem`.

## Grids and strips

- **Material's `grid cards` list is `display: contents`.** Its items are the grid items, so the grid cannot clip their
  outer rules. Make the outer `div` a block that draws the top and bottom rules, and the `ul`/`ol` the grid with
  `overflow: hidden`.
- **The gap-as-border trick** (a 1px gap on a border-coloured background) paints empty trailing cells in border colour.
  Draw each cell's right and bottom rule with `box-shadow` and let the list clip them instead.
- **A strip followed by a grid draws a double rule.** Drop the grid's top border after a strip (`h2.ui-strip + .grid`).
- **The strip index loses its space.** A trailing space in `content: attr(data-index) " / "` collapses inside a flex item;
  use a non-breaking space (`"\00a0/"`).
- **A page that hides its sidebars looks stretched.** Keep the sidebars' widths as empty margins (`--ui-inset-*`). Every
  full-bleed element (strips, grids) must then cancel gutter plus inset and pad them back, and grids must draw their own
  outer left and right rules at the margins, offset by 1px, or the outer cells stay open on one side.
- **The hero headline wraps after a layout change.** A `vw`-based size ignores the column width; size it with container
  query units on the hero (`container-type: inline-size`, `font-size: clamp(..., <n>cqi, ...)`).
- **A clickable cell swallows its inner links.** The stretched `::after` of the title link covers the cell; give every
  other link in the cell `position: relative; z-index: 1`.
- **Renaming a heading breaks a link.** Grep for `page.md#anchor` before changing heading text; prefer adding a strip
  class to an existing `##` heading.

## Tooling

- **Config changes do not appear.** Restart `mkdocs serve` after changing `custom_dir`, `plugins`, or `theme.features`.
- **Measurements return 0 and screenshots time out.** The browser pane is hidden or behind another window; emulate a
  viewport size, and use JavaScript measurements rather than screenshots.
- **A preview tool reports the server never became ready.** With a `site_url` path, `/` redirects (302) to the path;
  poll the full path (`http://127.0.0.1:8000/<path>/`) instead.
- **`LF will be replaced by CRLF` warnings** on Windows with `core.autocrlf` are harmless.

## Shipping

- **The base branch moved during the redesign.** Fetch before merging; a content release often lands meanwhile and
  edits the same hand-written index pages. Merge the base in, keep the new layout, fold in its content edits, rebuild,
  and look at its new pages in the new design.
- **Tagging the redesign as a version.** If version tags mark product releases, a site redesign is not one; ask whether
  and how to tag.

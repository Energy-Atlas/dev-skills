# Theming third-party surfaces

Most of an app's pixels are drawn by libraries. Each one has its own theming API; feed every API from the semantic
tokens (`token-recipes.md`) so a theme switch restyles it without code per theme. APIs below are as of the versions
named; grep the installed package (`node_modules/<package>/**/*.css`, its type definitions) before relying on a name.

Two questions decide the recipe for any library:

1. **Does it render to the DOM or to a canvas?** DOM renderers accept `var(--token)` and follow a theme switch for free.
   Canvas and WebGL renderers need resolved values and an explicit re-render on every theme change.
2. **Does it expose variables or parameters, or only class names?** Prefer its variables or parameters; override its
   classes only where no variable exists, scoped under the app's root class, and record those overrides (they break on
   upgrades).

Resolving a token for a canvas:

```ts
export function token(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}
```

Read a font family the same way, and wait for the web font before drawing text that is measured once:

```ts
await document.fonts.load(`12px ${token('--font-sans').split(',')[0]}`)
```

## Docking and layout managers

- **FlexLayout (`flexlayout-react`).** Named CSS variables, `--flexlayout-color-*`, `--flexlayout-font-family`,
  `--flexlayout-font-size`, `--flexlayout-splitter-size`; map each onto a token in one stylesheet. The tab label
  treatment (mono uppercase, active-tab block) needs class overrides: `.flexlayout__tab_button`,
  `.flexlayout__tab_button--selected`, `.flexlayout__border_button`, `.flexlayout__border_button--selected`,
  `.flexlayout__tabset_tabbar_outer`. Tab bars clip overflow: draw the active outline inset (`outline-offset: -1px` or
  an inset `box-shadow`), not outside the tab. `.flexlayout__tabset-selected` marks the focused tab set, so the active
  edge can be the accent there and a quieter colour elsewhere.
- **FlexLayout's font variable is also the content font.** `--flexlayout-font-family` sets the font of
  `.flexlayout__tabset`, so every docked pane inherits it: keep it the interface sans and put a mono label font on
  `.flexlayout__tab_button` and `.flexlayout__border_button` only.
- **FlexLayout hard-codes radii and some motion** (0.11): `border-radius` on `.flexlayout__tab_button`,
  `__border_button`, `__tab_toolbar_button`, `__popup_menu`, `__popup_menu_item`, `__drag_rect`, `__outline_rect`,
  `__edge_rect` needs overrides for square corners; drop indicators use `--flexlayout-color-drag1`,
  `--flexlayout-color-drag1-background`, and the drag-rect and edge-marker variables; the splitter's `:hover` rule sets
  its own `transition`, which survives reduced motion unless overridden on `:hover` too.
- **Dockview.** `--dv-*` variables on a theme class (`.dockview-theme-*`); create the app's own theme class from the
  tokens rather than editing a shipped one.
- **Splitters:** a 1 px rule at rest with a wider hit area; the accent on hover and drag.

## Data grids

- **AG Grid (v33+ Theming API).** `themeQuartz.withParams({...})` accepts CSS variable strings, so the grid follows the
  theme without re-creation: `backgroundColor`, `foregroundColor`, `borderColor`, `headerBackgroundColor`,
  `headerTextColor`, `headerFontFamily`, `headerFontSize`, `headerFontWeight`, `oddRowBackgroundColor`,
  `rowHoverColor`, `selectedRowBackgroundColor`, `accentColor`, `fontFamily`, `fontSize`, `rowHeight`, `headerHeight`,
  `borderRadius`, `wrapperBorderRadius`, `columnBorder`, `rowBorder`. Numeric parameters (font size, heights) do not
  take variables, and a prefixed size such as `headerFontSize` is easy to miss: use the token's pixel value. Uppercase
  mono headers need a class override (`.ag-header-cell-text`) and are wider than the sans: set
  `defaultColDef: { wrapHeaderText: true, autoHeaderHeight: true }` rather than truncating or widening columns. Drop
  zebra rows with `oddRowBackgroundColor` equal to the pane. The focused cell is drawn with a border, not an outline:
  check it by its border colour or a screenshot.
- **TanStack Table and plain tables.** The app owns the markup: style with tokens; `font-variant-numeric:
  tabular-nums` on numeric columns; sticky headers on `surface-raised`.

## Charts

- **ECharts.** Canvas (or SVG) renderer: no CSS variables inside options. Build options from resolved tokens and the
  data palette: `textStyle.fontFamily` (the resolved family list), axis `axisLine`, `axisTick`, `splitLine` from the ink
  tokens, `tooltip` (`backgroundColor`, `borderColor`, `textStyle`; or `className` and CSS for the HTML tooltip).
  Re-run `setOption(option, { notMerge: true })` on every theme change and once after the web font loads; otherwise
  labels keep the fallback font's measurements. Bars (`itemStyle.borderRadius`) and the tooltip (`borderRadius`,
  default 4) round their corners until set to 0. ECharts canvases are transparent: the pane behind them shows through,
  so a pixel sample of a corner proves nothing about the theme.
- **Chart.js.** `Chart.defaults.color`, `Chart.defaults.borderColor`, `Chart.defaults.font.family`, per-scale `grid` and
  `ticks` colours; `chart.update()` after a theme change.
- **Plotly.** `layout.font`, `paper_bgcolor`, `plot_bgcolor`, axis `gridcolor` and `linecolor`; `Plotly.relayout` on a
  theme change.
- **Vega and Vega-Lite.** A `config` object (`background`, `axis`, `legend`, `title`, `range.category`) built from the
  tokens; re-embed on a theme change.

Scaffolding (grid, axes, ticks) stays quieter than the data: grid lines at `border-subtle`, axis labels at
`text-muted`, data at the data palette.

## Maps

- **MapLibre GL and Mapbox GL.** WebGL. Colours live in the style JSON: build the style per theme from the tokens, or
  call `map.setPaintProperty(layer, property, value)` for each recoloured layer on a theme change. The map background,
  water, land, roads, and labels need the theme's surfaces and muted inks; data overlays need the data palette.
- **Map labels use glyph files** (`glyphs` URL, PBF ranges), not web fonts: the app's font does not apply unless glyphs
  are generated for it. Accept the basemap's font, or record a glyph decision.
- **Controls and popups are DOM:** `.maplibregl-ctrl-group`, `.maplibregl-ctrl-attrib`, `.maplibregl-popup-content`
  (and the `mapboxgl-` equivalents) take token-based CSS. Legends the app draws itself are ordinary components. The
  control group has its own radius and shadow, and its buttons focus with a fixed blue glow
  (`box-shadow: 0 0 2px 2px rgb(0 150 255)`): replace it with the app's ring (`box-shadow: none; outline: 2px solid
  var(--color-focus); outline-offset: -2px`).
- **Sky, fog, light, and terrain** (globe and 3D views) are style properties too; give each theme its own values rather
  than reusing the dark ones in light themes.

## Diagrams and flows

- **React Flow (`@xyflow/react` v12).** `colorMode` (`light`, `dark`, `system`) plus `--xy-*` CSS variables
  (`--xy-node-background-color`, `--xy-node-border`, `--xy-edge-stroke`, `--xy-background-pattern-color`, ...): map them
  onto tokens; variables set on an ancestor override the `colorMode` defaults. Node components are the app's own and use
  tokens directly. The attribution link is a fixed `#999` (2.84:1 on white): once its background is opaque, axe
  reports it; give `.react-flow__attribution a` the muted text token.
- **Layout engines (dagre, elk)** have no styling; they only move nodes.

## Component libraries

- **React Aria Components.** Unstyled. Style states through data attributes: `[data-hovered]`, `[data-pressed]`,
  `[data-focus-visible]`, `[data-selected]`, `[data-disabled]`, `[data-invalid]`, `[data-placement]` on popovers.
  Native inputs stay visually hidden; draw checkboxes, radios, and switches from tokens.
- **Radix and shadcn/ui.** `data-state` attributes; shadcn's CSS variables (`--background`, `--foreground`,
  `--primary`, `--border`, `--ring`, ...) are the semantic layer: set them from the palette.
- **MUI.** One theme object built from the tokens, with CSS variables enabled so a theme switch does not re-render the
  tree; component `styleOverrides` for shapes and label case.
- **Tailwind.** Point the theme's colours and fonts at the CSS variables (v4 `@theme`, v3 `theme.extend`), so utility
  classes resolve to tokens; ban arbitrary colour values in review.

## Editors

- **Monaco.** `monaco.editor.defineTheme(name, { base, inherit, rules, colors })` needs hex values: define one theme per
  app theme from the resolved tokens and call `monaco.editor.setTheme` on a switch.
- **CodeMirror 6.** DOM-based: `EditorView.theme({...}, { dark })` accepts `var(--token)`.

## Native and incidental surfaces

- `color-scheme` per theme (native controls, scrollbars), `accent-color` for native checkboxes and ranges,
  `scrollbar-color: <thumb> <track>` from muted tokens, `::selection` from the selection tint.
- Icon sets that draw with `currentColor` (lucide, heroicons) inherit text tokens: keep one size and one stroke width per
  context.
- Toasts, tooltips, and portals render outside the app root: make sure they sit under the element that carries the
  theme attribute and tokens (usually `<html>`), or they keep the fallback theme.

# Verification

Checks for phases 2 and 7. Run the project's own checks first; they are the gate. The browser snippets run in a page
you drive (a browser tool, or `page.evaluate` in a Playwright script). Save long scripts to files rather than inlining
them in a shell; quoting breaks on Windows.

## The project's checks

Run every check the project defines before each commit you hand back, for example `typecheck`, `lint`,
`format:check`, unit tests, browser tests, a production build, and a preview of the build under its deployed base path.
Report the totals (tests passed, files checked) in the alignment record. If a browser test fails because a label, role,
or colour it asserts changed with the restyle, update the test only when the change is a decided restyle; never
weaken an accessibility assertion.

Local-only files (a Playwright config on another port, a screenshot harness) must not break these checks or be
committed: put them in a folder the project already ignores for git, lint, format, and typecheck, or pass ignore
patterns and record that the exception is local.

## Audit before and after

```bash
python <skill>/scripts/style_audit.py src --tokens "<token file globs>" --exclude "<generated or spike globs>"
```

Run it in phase 2 (record the counts with the commit) and again at the end. Expect zero colour literals outside the token
files, or each one explained; font sizes from the type-scale tokens, or each literal explained; font families only from
tokens; no font-host URLs; at least one `prefers-reduced-motion` rule if the app has transitions. Read the uppercase
list for labels that carry units or data. Counts that rise by decision (borders in a framed design, edge shadows for
inset tab edges) are not regressions.

## Contrast

```bash
python <skill>/scripts/contrast.py check pairs.json --suggest --failures-only
```

`pairs.json` lists every theme's tokens (or names a JSON dump of the app's token module) and the pairs to check; the
script's docstring has the format, and `mix(...)` expressions describe tints. Check text on every surface and tint it
sits on, control borders on every surface a control sits on, and any outline drawn on a fill. Then keep the result in
the app's own contrast test (`token-recipes.md`).

## A populated state

Most surfaces of a workbench are empty until data exists: a grid with no rows, a dashboard with no results, a map with
no layers. Before the baseline, build a populated state once and reuse it:

- through the app's own seed, fixture, or demo data, if it has one;
- otherwise with a Playwright setup project that drives the app (run the workflow, create the objects), saves the
  project the way the app does, and writes `storageState` to a file the screenshot project loads.

Use the project's own test fixture (network stubs, mocked services) so screenshots stay offline and repeatable.

## Screenshot matrix

Baseline in phase 2, comparison in phase 7. A throwaway Playwright script that walks the review surfaces in every theme
at two sizes. Keep it where it can import `@playwright/test` and the app's fixtures: in an ignored folder inside the
repository (often `tmp/`), or outside it with the repository's `node_modules` linked in (`mklink /J node_modules
<repo>\node_modules` on Windows) and the fixtures imported by absolute path.

```ts
import { test } from '<repo>/e2e/test'            // the project's fixture, or '@playwright/test'

test.describe.configure({ mode: 'parallel' })     // one file otherwise runs serially in one worker
test.use({ storageState: 'tmp/populated.json' })  // from the setup project

const THEMES = ['light', 'dark']                  // every theme the app ships
const SIZES = [{ width: 1280, height: 800 }, { width: 1920, height: 1080 }]
const SURFACES = [                                 // the review surfaces from phase 1
  { name: 'home', open: async (page) => page.goto('/') },
  // { name: 'settings', open: async (page) => { await page.goto('/'); /* open it through the app's own command */ } },
]

for (const theme of THEMES)
  for (const size of SIZES)
    for (const surface of SURFACES)
      test(`${surface.name} ${theme} ${size.width}`, async ({ page }) => {
        await page.setViewportSize(size)
        // Store the theme the way the app does, once: init scripts run again on every reload.
        await page.addInitScript((t) => {
          if (!sessionStorage.getItem('seeded')) {
            localStorage.setItem('<theme key>', t)
            sessionStorage.setItem('seeded', '1')
          }
        }, theme)
        await surface.open(page)
        await page.evaluate(() => document.fonts.ready)
        await page.waitForTimeout(500)             // canvases settle
        await page.screenshot({ path: `shots/${surface.name}-${theme}-${size.width}.png` })
      })
```

Run it with the project's Playwright configuration (dev server, browser channel, worker cap), on a port no other
checkout uses. Hundreds of screenshots cannot all be reviewed by eye; compare at least:

- every surface in the light and the dark theme at the minimum size;
- the busiest surface (the one with grid, chart, and map) in every theme at both sizes;
- every overlay (menu, dialog, command palette) in the dark theme.

Look for clipped or ellipsized labels, lost focus rings, unreadable muted text, canvases in old colours, case changes on
units, and rules that doubled where two panes meet.

## Browser checks

### Fonts and requests

```js
await document.fonts.ready;
({
  loaded: [...document.fonts].filter(f => f.status === "loaded").map(f => `${f.family} ${f.weight}`),
  bodyFont: getComputedStyle(document.body).fontFamily,
  fontRequests: performance.getEntriesByType("resource").map(r => r.name)
    .filter(u => /\.(woff2?|ttf|otf)(\?|$)/.test(u) && !u.startsWith(location.origin)),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
})
```

Expect the app's families loaded, `fontRequests` empty, and `overflow` 0. Requests to the app's data services (tiles,
APIs) are expected; list them in the record if they are new.

### Theme switch without reload

Switch the theme through the app's own control, without a reload, and screenshot every surface that draws to a canvas
(charts, map, diagrams) next to the same surface loaded fresh in that theme; they must match. Pixel sampling is
unreliable: ECharts canvases are transparent, so a corner pixel is `rgba(0 0 0 0)` in every theme. If a chart library
exposes its options, compare the colours it was last given with the tokens instead:

```js
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
({ theme: document.documentElement.dataset.theme, text: css("--color-text"), border: css("--color-border") })
// then, for ECharts: echarts.getInstanceByDom(el).getOption().textStyle, .xAxis[0].axisLabel.color, ...
```

### First frame

Bundlers inject CSS from JavaScript in development, so the dev server shows an unstyled first frame whatever the theme
code does: check against the production build. Store a non-default theme, hold the app script back so only
`index.html` and its inline script run, and read the root:

```ts
await page.addInitScript(() => localStorage.setItem('<theme key>', 'dark'))
await page.route('**/assets/index-*.js', (route) => route.abort())
await page.goto('/', { waitUntil: 'domcontentloaded' })
// expect data-theme (or the class) and the body background of the stored theme
```

### Focus

Tab through the shell, a docked panel, the grid, a menu, and a dialog. Every focused element shows a ring that is not
clipped by its container. Some widgets show focus with a border rather than an outline (AG Grid cells), so compare all
three and confirm doubtful ones by screenshot:

```js
const el = document.activeElement, s = getComputedStyle(el);
({ tag: el.tagName, label: el.getAttribute("aria-label") || el.textContent.trim().slice(0, 40),
   outline: `${s.outlineStyle} ${s.outlineWidth} ${s.outlineColor}`, offset: s.outlineOffset,
   shadow: s.boxShadow, border: s.borderColor })
```

### States

Hover, select, and press each interactive kind (a tab, a side handle, a toolbar button, a menu item, a grid row, a tree
item) in every theme and measure the label against the state's background and the indicator against the strip. The
label's own colour must not come from a library's "selected" variable that the restyle repurposed.

```js
// Run while the pointer is over the element (Playwright: await locator.hover(), then page.evaluate).
const el = document.querySelector("<selector of the hovered element>");
const s = getComputedStyle(el);
let strip = el.parentElement;
while (strip && getComputedStyle(strip).backgroundColor === "rgba(0, 0, 0, 0)") strip = strip.parentElement;
({ label: s.color, background: s.backgroundColor, edge: s.boxShadow || s.borderColor || s.outlineColor,
   strip: strip && getComputedStyle(strip).backgroundColor })
// then: python contrast.py ratio <label> <background or strip>  (4.5)
//       python contrast.py ratio <edge colour> <strip>            (3)
```

Screenshot each state next to rest at the minimum size: hover must be visible at a glance, and hover and selected must
not be confused.

### Clipped labels

Find text that overflows its box, ellipsized text included (that is how grid headers truncate), and skip visually
hidden labels:

```js
[...document.querySelectorAll("button, [role=tab], [role=menuitem], [role=columnheader], th, h1, h2, h3, label, " +
  ".ag-header-cell-text")]
  .filter(el => el.clientWidth > 2 && getComputedStyle(el).clip === "auto" && el.scrollWidth > el.clientWidth + 1)
  .map(el => ({ text: el.textContent.trim().slice(0, 40), ellipsis: getComputedStyle(el).textOverflow === "ellipsis" }))
```

Also compare the tab bars' `scrollWidth` with their `clientWidth` at the minimum size with side panels open: a tab that
moved into an overflow menu is not clipped, it is gone.

### Reduced motion

Emulate `prefers-reduced-motion: reduce` (Playwright `page.emulateMedia({ reducedMotion: 'reduce' })`) and confirm
transitions are `0s` on a tab, a button, and a splitter, hovered as well as at rest.

### Accessibility

Run axe (or the project's checker) on every review surface in every theme; no serious or critical violations. Contrast
findings from axe on canvases are not reliable; the token test covers those. For each finding, check the base commit
(run the same check there): fix it inside the restyle if the restyle caused it or it is a colour finding the restyle
touches, otherwise log it as pre-existing with the base commit. After making a translucent library surface opaque, run
axe on it again: hard-coded colours that axe skipped on a translucent background become measurable.

## Checklist

- [ ] The project's checks pass; totals recorded; local-only files neither committed nor breaking a check.
- [ ] Audit counts before and after recorded; literals outside tokens zero or explained; uppercase list reviewed.
- [ ] Contrast test covers every theme and role, tints and outlines included; it passes.
- [ ] Screenshot matrix of a populated state reviewed before and after (the priority subset at least).
- [ ] Fonts from the app's origin; no font-host or CDN request; no page overflow.
- [ ] Theme switch restyles every surface, canvases and maps included, without a reload; no first-frame flash on the
      production build.
- [ ] Focus visible and unclipped in shell, panels, grid, menus, and dialogs; no clipped, ellipsized, or vanished labels.
- [ ] Hover, selected, and pressed states of every interactive kind measured in every theme: labels 4.5:1, indicators 3:1,
      states told apart.
- [ ] Titles inside panels keep the app's design unless the owner chose strips.
- [ ] Reduced motion honoured, libraries included; axe clean in every theme, pre-existing findings logged.

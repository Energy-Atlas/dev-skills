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

## Audit before and after

```bash
python <skill>/scripts/style_audit.py src --tokens "<token file globs>" --exclude "<generated or spike globs>"
```

Run it in phase 2 (record the counts with the commit) and again at the end. Expect zero colour literals outside the token
files, or each one explained; the font sizes reduced to the type scale tokens; font families only from tokens; no
font-host URLs; at least one `prefers-reduced-motion` rule if the app has transitions.

## Contrast

```bash
python <skill>/scripts/contrast.py check pairs.json --suggest
```

`pairs.json` lists every theme's tokens and the pairs to check (the script's docstring has the format;
`contrast.py css-tokens <file.css>` dumps a stylesheet's custom properties to start from). Then keep the result in the
app's own contrast test (`token-recipes.md`).

## Screenshot matrix

Baseline in phase 2, comparison in phase 7. A throwaway Playwright script (outside the repository, or a spec the project
agrees to keep) that walks the review surfaces in every theme at two sizes:

```ts
import { test } from '@playwright/test'

const THEMES = ['light', 'dark']                      // every theme the app ships
const SIZES = [{ width: 1280, height: 800 }, { width: 1920, height: 1080 }]
const SURFACES = [                                     // the review surfaces from phase 1
  { name: 'home', open: async (page) => page.goto('/') },
  // { name: 'settings', open: async (page) => { await page.goto('/'); /* open it through the app's own command */ } },
]

for (const theme of THEMES)
  for (const size of SIZES)
    for (const surface of SURFACES)
      test(`${surface.name} ${theme} ${size.width}`, async ({ page }) => {
        await page.setViewportSize(size)
        // Select the theme the way the app stores it, before the app starts:
        await page.addInitScript((t) => localStorage.setItem('<theme key>', t), theme)
        await surface.open(page)
        await page.evaluate(() => document.fonts.ready)
        await page.waitForTimeout(500)                 // canvases settle
        await page.screenshot({ path: `shots/${surface.name}-${theme}-${size.width}.png` })
      })
```

Use the app's own Playwright configuration (its dev server, browser channel, worker cap, and network stubs) by running
the script with `npx playwright test <file> -c <config>`, or copy the relevant settings. Compare before and after side by
side; look for clipped labels, lost focus rings, unreadable muted text, canvases still in old colours, and borders that
doubled where two panes meet.

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

Switch the theme through the app's own control, then sample the colours that canvases and libraries draw with:

```js
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
({
  theme: document.documentElement.dataset.theme,
  bg: css("--color-bg"),
  text: css("--color-text"),
  canvases: [...document.querySelectorAll("canvas")].map(c => {
    const ctx = c.getContext("2d", { willReadFrequently: true });
    if (!ctx) return "webgl";                          // check WebGL canvases by screenshot
    const [r, g, b] = ctx.getImageData(2, 2, 1, 1).data;
    return `rgb(${r} ${g} ${b})`;
  }),
})
```

A 2D canvas's corner should match the theme's chart surface; a WebGL map is checked by screenshot after the switch.

### First frame

Store a non-default theme, reload, and capture the first paint (a screenshot right after `goto` with
`waitUntil: "commit"`, or a performance trace). The stored theme must show from the first frame.

### Focus

Tab through the shell, a docked panel, the grid, a menu, and a dialog. Every focused element shows a ring that is not
clipped by its container:

```js
const el = document.activeElement, s = getComputedStyle(el);
({ tag: el.tagName, label: el.getAttribute("aria-label") || el.textContent.trim().slice(0, 40),
   outline: `${s.outlineStyle} ${s.outlineWidth} ${s.outlineColor}`, offset: s.outlineOffset, shadow: s.boxShadow })
```

### Clipped labels

Find text that overflows its box in tab strips, ribbons, headers, and buttons:

```js
[...document.querySelectorAll("button, [role=tab], [role=menuitem], th, h1, h2, h3, label")]
  .filter(el => el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).textOverflow !== "ellipsis")
  .map(el => el.textContent.trim().slice(0, 40))
```

### Reduced motion

Emulate `prefers-reduced-motion: reduce` (Playwright `page.emulateMedia({ reducedMotion: 'reduce' })`) and confirm
transitions are `0s` on a tab, a button, and a splitter.

### Accessibility

Run axe (or the project's checker) on every review surface in every theme; no serious or critical violations. Colour
contrast findings from axe on canvases are not reliable; the token test covers those.

## Checklist

- [ ] The project's checks pass; totals recorded.
- [ ] Audit counts before and after recorded; literals outside tokens zero or explained.
- [ ] Contrast test covers every theme and role; it passes.
- [ ] Screenshot matrix reviewed before and after, every theme, both sizes.
- [ ] Fonts from the app's origin; no font-host or CDN request; no page overflow.
- [ ] Theme switch restyles every surface, canvases and maps included, without a reload; no first-frame flash.
- [ ] Focus visible and unclipped in shell, panels, grid, menus, and dialogs; no clipped labels.
- [ ] Reduced motion honoured; axe clean in every theme.

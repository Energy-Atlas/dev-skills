# Token recipes

How to structure an app's design tokens so one definition drives every surface, every theme, and every renderer, and
how to test their contrast. Adapt names to the app's existing prefix; do not rename tokens the app already uses unless
the owner wants the churn.

## Layers

1. **Palette:** the raw values of each theme (hex). Live only in the token module or token stylesheet.
2. **Semantic tokens:** roles with the same names in every theme. Components use only these.
3. **Library mappings:** each third-party theme API fed from the semantic tokens (`third-party-theming.md`).

Components never pick a palette value; a renderer that cannot read CSS (canvas, WebGL) reads the resolved semantic
token, not a copy of the value.

## Semantic chrome tokens

The minimum set; add roles only when a component needs one that the set cannot express.

| Token | Role | Contrast target |
| --- | --- | --- |
| `bg` | App background, behind panes | — |
| `surface` | Pane and content surface | — |
| `surface-raised` | Headers, toolbars, hover, stat tiles | — |
| `surface-overlay` | Menus, popovers, dialogs (may equal `surface-raised`) | — |
| `text` | Primary text | 4.5:1 on every surface and on `selected-bg` |
| `text-muted` | Secondary text, metadata, labels | 4.5:1 on every surface it sits on |
| `border-subtle` | Decorative rules: pane boundaries, row rules, dividers | none (decorative) |
| `border-interactive` | Edges of inputs, buttons, checkboxes | 3:1 on the surfaces they sit on |
| `accent` | Fills of primary controls, focus, active indicators | 3:1 as a UI indicator |
| `accent-text` | Links and accent-coloured text | 4.5:1 on surfaces |
| `on-accent` | Text on an accent fill | 4.5:1 on `accent` |
| `focus` | Focus ring | 3:1 on every surface |
| `selected-bg` | Selection tint in lists, grids, trees | `text` 4.5:1 on it |
| `tone-{success,info,warning,danger,neutral}-text` | State text and icons | 4.5:1 on its tint and on surfaces |
| `tone-{...}-bg` | State tints | — |
| `shadow-overlay` | The one elevation the app keeps | — |

Font tokens: `font-sans`, `font-mono` (and `font-serif` only if a surface uses it), `font-size-small`, `-base`, `-title`,
and `font-size-label` if a mono caps label style needs a smaller size than the app's smallest. Label tokens:
`label-font`, `label-case`, `label-size`, `label-tracking`, `label-weight`, read by every label rule so the label style
is decided in one place (`translation.md`, "Label style").
Shape tokens: `radius` (one value), `rule` (`1px solid var(--color-border-subtle)`, so framing edits are one word),
`transition` (150 ms ease, `0s` under reduced motion).

A custom property reads back as declared: `getPropertyValue('--font-size-small')` returns `0.75rem`, not `12px`.
Renderers that need numbers (canvas charts, grid parameters) take the pixel value from the token module, or convert
rem with the root font size.

## Data palette

Charts and maps need their own roles, separate from chrome: `categorical[n]` (a colour follows its entity, not its
rank), `sequential[]` (low to high; flip the anchor in dark themes so low values recede), `diverging[]` if used,
`no-data`, `de-emphasis`, `selection`, chart `ink` (primary, secondary, muted, grid, axis, surface), and `status`
(always with an icon and a label). Every mark colour needs 3:1 against the chart surface.

## Runtime themes

Choose the mechanism the app already has; the recipes below are the usual two.

**Attribute and stylesheet.** Each theme is a CSS block; the switch sets an attribute.

```css
:root,
[data-theme="light"] {
  color-scheme: light;
  --color-bg: #ffffff;
  /* ... */
}

[data-theme="dark"] {
  color-scheme: dark;
  --color-bg: #000000;
  /* ... */
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    color-scheme: dark;
    --color-bg: #000000;
    /* ... the dark block again, for the first frame before the script runs */
  }
}
```

**Token module and script.** Each theme is an object in TypeScript; a function writes the semantic tokens onto the root
element (`root.style.setProperty(name, value)`) and sets `data-theme` and `color-scheme`. Canvas renderers read the same
objects. Keep a light fallback block in CSS for the first frame and for pages that do not run the script.

Either way:

- Apply the stored preference before the first paint: an inline script in `index.html` that reads storage and sets the
  attribute, or the CSS media-query fallback above. Otherwise the default theme flashes on every reload.
- Set `color-scheme` per theme so native controls, scrollbars, and form widgets follow.
- Store the preference under one key; read it defensively (storage can be blocked).
- When a theme changes, every canvas renderer must re-read its colours: subscribe to the app's theme state, or observe
  the root attribute with a `MutationObserver`.

## Example: the EnergyAtlas family palette, tested for apps

The family's values come from the `wiki-ui-alignment` sites (dev-skills, BEMGen docs), where they were tested on
documentation pages. On app surfaces some fail: the dark interactive border is 2.69:1 on the raised surface, and the
tone colours fall below 4.5:1 on their own tints. The table gives the values that passed in the trial apps, with the
family's value in brackets where it changed, mapped onto app roles (`translation.md`, "Surfaces").

| App role | Dark | Light |
| --- | --- | --- |
| Pane (family base) | `#000000` | `#ffffff` |
| Background behind panes, strips, status bar (surface 1) | `#1a1a1a` | `#f8fafc` |
| Raised: headers, toolbars, hover (surface 2) | `#2a2a2a` | `#f4f7fb` |
| Overlay: menus, popovers, dialogs (with a rule) | `#1a1a1a` | `#ffffff` |
| Non-text fill only (surface 3) | `#3a3a3a` | `#e7edf5` |
| Text | `#e5e5e5` | `#18202c` |
| Secondary text | `#b0b0b0` | `#3f4b5b` |
| Muted text | `#999999` | `#5f6b7a` |
| Border, decorative | `#404040` | `#cfd8e5` |
| Border, interactive | `#747474` (`#6b6b6b`) | `#768599` |
| Accent, accent text, focus | `#4da3ff` | `#125dae` |
| Text on accent | `#000000` | `#ffffff` |
| Selection tint | `#112438` | `#e3ecf5` |
| Success | `#31ab4c` (`#28a745`) | `#187d37` (`#188038`) |
| Warning | `#ffc107` | `#956400` (`#9a6700`) |
| Danger | `#f65d52` (`#f44336`) | `#c5221f` |
| Success / info / warning / danger tint | `#1d3322` / `#233343` / `#433817` / `#41211f` | `#e8f2eb` / `#e7eff7` / `#f5f0e6` / `#f9e9e9` |
| Brand fill (fills only) | `#003978` | `#003978` |

Every text colour above passes 4.5:1 on the pane, the background, the raised surface, and its own tint; the interactive
border passes 3:1 on those three surfaces; none of them is meant for surface 3. The tints are roughly 16–22 % of the
tone over the dark pane and 8–10 % over the light one; derive others with `contrast.py mix` and check them.

Fonts: Geist (interface and, by default, labels), Geist Mono (code, identifiers, and labels only with mono caps), Cormorant Garamond italic 500 (sparse editorial accent). The
brand fill fails as text on dark (1.86:1 on black): fills only, with white or `#e5e5e5` text on it. Red only for
errors, destructive actions, and failures.

The family's inverted active tab puts a `#e5e5e5` (`#18202c` in light) fill next to the accent: 2.08:1 in dark, 2.50:1
in light. Draw the outline on the strip colour behind a gap, never on the fill (pitfalls).

## Contrast test

Write the test in the app's own runner so it runs with the other checks. The shape, for a TypeScript token module and
Vitest:

```ts
import { describe, expect, it } from 'vitest'
import { THEMES } from './themes'           // the app's token module

function luminance(hex: string): number {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function ratio(a: string, b: string): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (hi + 0.05) / (lo + 0.05)
}

const SURFACES = ['bg', 'surface', 'surfaceRaised', 'surfaceOverlay', 'selectedBg'] as const

describe.each(Object.values(THEMES))('$id', (theme) => {
  it.each(SURFACES)('text and muted text pass 4.5:1 on %s', (surface) => {
    expect(ratio(theme.text, theme[surface])).toBeGreaterThanOrEqual(4.5)
    expect(ratio(theme.textMuted, theme[surface])).toBeGreaterThanOrEqual(4.5)
  })
  it('interactive borders and focus pass 3:1', () => {
    for (const surface of SURFACES) {
      expect(ratio(theme.borderInteractive, theme[surface])).toBeGreaterThanOrEqual(3)
      expect(ratio(theme.focus, theme[surface])).toBeGreaterThanOrEqual(3)
    }
  })
  it('text on accent passes 4.5:1', () => {
    expect(ratio(theme.onAccent, theme.accent)).toBeGreaterThanOrEqual(4.5)
  })
  it('tone text passes 4.5:1 on its tint', () => {
    for (const tone of ['Success', 'Info', 'Warning', 'Danger'] as const) {
      expect(ratio(theme[`tone${tone}Text`], theme[`tone${tone}Bg`])).toBeGreaterThanOrEqual(4.5)
    }
  })
  // Only with an inverted active tab: its outline sits on the strip, never on the fill.
  it('the active-tab outline passes 3:1 on the strip', () => {
    expect(ratio(theme.accent, theme.surfaceStrip)).toBeGreaterThanOrEqual(3)
  })
})
```

If the app already has such a test, extend it with the new roles rather than writing a second one. Use
`scripts/contrast.py check --suggest` while choosing values; the app's test keeps them honest afterwards.

## No literals

After the restyle, `scripts/style_audit.py` should report no colour literals outside the token files, or each one
explained in the record (for example a translucent overlay derived from black, which is the same in every theme). Prefer
`color-mix()` with a token over a new literal for tints and translucent overlays.

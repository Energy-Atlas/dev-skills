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

Font tokens: `font-sans`, `font-mono` (and `font-serif` only if a surface uses it), `font-size-small`, `-base`, `-title`.
Shape tokens: `radius` (one value), `rule` (1 px), `transition` (150 ms ease).

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

## Example: the EnergyAtlas family palette

The values the `wiki-ui-alignment` sites use after their contrast pass (dev-skills, BEMGen docs). Use them when the
reference is that family; re-check them on the app's surfaces.

| Role | Dark | Light |
| --- | --- | --- |
| `bg` | `#000000` | `#ffffff` |
| `surface` | `#1a1a1a` | `#f8fafc` |
| `surface-raised` | `#2a2a2a` | `#f4f7fb` |
| `surface-overlay` | `#3a3a3a` | `#e7edf5` |
| `text` | `#e5e5e5` | `#18202c` |
| `text-secondary` | `#b0b0b0` | `#3f4b5b` |
| `text-muted` | `#999999` | `#5f6b7a` |
| `border-subtle` | `#404040` | `#cfd8e5` |
| `border-interactive` | `#6b6b6b` | `#768599` |
| `accent` | `#4da3ff` | `#125dae` |
| `success` | `#28a745` | `#188038` |
| `warning` | `#ffc107` | `#9a6700` |
| `danger` | `#f44336` | `#c5221f` |
| brand fill | `#003978` | `#003978` |

Fonts: Geist (interface), Geist Mono (labels and code), Cormorant Garamond italic 500 (sparse editorial accent). The
brand fill fails as text on dark (1.86:1 on black): fills only, with white or `#e5e5e5` text on it. Red only for
errors, destructive actions, and failures. The family has no tint values: derive tone tints for an app (for example
the tone colour at 12–16 % over the surface, `color-mix(in srgb, <tone> 14%, <surface>)`) and test tone text on them.

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

const SURFACES = ['bg', 'surface', 'surfaceRaised'] as const

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
})
```

If the app already has such a test, extend it with the new roles rather than writing a second one. Use
`scripts/contrast.py check --suggest` while choosing values; the app's test keeps them honest afterwards.

## No literals

After the restyle, `scripts/style_audit.py` should report no colour literals outside the token files, or each one
explained in the record (for example a translucent overlay derived from black, which is the same in every theme). Prefer
`color-mix()` with a token over a new literal for tints and translucent overlays.

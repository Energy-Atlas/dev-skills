# EnergyAtlas brand mark

The EnergyAtlas mark: a hexagon in a navy-to-red gradient (`#003978` to `#f1392a`) with an E in its lower right face.
It is the favicon and logo of [energyatlas.io](https://energyatlas.io) and the mark of EnergyAtlas products and
sites. This folder is the same in `wiki-ui-alignment` and `app-ui-alignment`.

Use it only for EnergyAtlas sites and products, and only when the owner has chosen it (the brand question in
`intake-questions.md`). Never recolour, redraw, crop, outline, or animate it; never put it on a coloured or patterned
fill other than the page's own surface.

## Files

| File | Use |
| --- | --- |
| `energyatlas-mark.svg` | The mark with a white E. The default on every surface, light or dark: header logo, about pages, the vector favicon |
| `energyatlas-mark-knockout.svg` | The mark with the E cut out, as energyatlas.io draws it. Only on surfaces known to be light (white or near white), where the E shows the page; on a dark surface the E disappears |
| `favicon.svg` | A copy of `energyatlas-mark.svg`, the vector favicon |
| `favicon.ico` | 16, 32, and 48 px, for browsers and tools that ask for `/favicon.ico` |
| `favicon-32.png` | 32 px PNG favicon |
| `apple-touch-icon.png` | 180 px on white, for iOS home screens |

Source: `public/assets/img/EnergyAtlasIcon.svg` of the EnergyAtlas website (knockout) and `docs/assets/images/icon.svg`
of the energy-atlas.github.io site (white E), as of 2026-10-20; the files here are the same drawing with Illustrator
metadata and non-ASCII ids removed and a `<title>`. Regenerate the rasters from the SVG with
`python scripts/brand_assets.py references/brand/energyatlas-mark.svg references/brand` (headless Chrome or Edge,
and Pillow); then copy `energyatlas-mark.svg` to `favicon.svg`.

## Placement

- **Header:** the mark at the left of the site or app name, about 1.3 times the name's font size tall and centred on
  it, with a gap of about a third of its height; the name keeps its own font and colour. The mark is never the only content of a link to home: keep the name, or give the link an accessible name.
- **Alt text:** the mark beside the name is decorative (`alt=""`); alone, it is `alt="EnergyAtlas"`.
- **Favicon:** the SVG first, then the PNG and the ICO as fallbacks, and the apple touch icon.
- **Colour:** the mark keeps its gradient in every theme. It is an image, not a UI colour, so the rule that red marks
  only errors does not apply to it, and its navy corner may fall below 3:1 on black; the white E and the red corner
  carry it there.
- Reference the files as images (`<img>`, CSS backgrounds, `<link rel="icon">`). Inlining the SVG twice in one page
  duplicates its gradient id.

## MkDocs (Material)

Copy the files to `docs/assets/brand/` and set:

```yaml
theme:
  logo: assets/brand/energyatlas-mark.svg
  favicon: assets/brand/favicon.svg
```

Add the fallbacks in `overrides/main.html`, inside the `extrahead` block:

```jinja
<link rel="icon" href="{{ 'assets/brand/favicon.ico' | url }}" sizes="48x48">
<link rel="icon" href="{{ 'assets/brand/favicon-32.png' | url }}" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{{ 'assets/brand/apple-touch-icon.png' | url }}">
```

Size the logo to the header in the site stylesheet, so it lines up with the title:

```css
.md-header__button.md-logo {
  margin: 0.2rem 0.2rem 0.2rem 0.4rem;
  padding: 0.4rem 0.2rem;
}

.md-header__button.md-logo img {
  height: 1.2rem;
  width: auto;
}
```

Material repeats `theme.logo` in the drawer of the mobile navigation; check it at phone width.

## Web applications

Put the files where the bundler copies them unchanged (Vite and most bundlers: `public/brand/`) and reference them from
`index.html` with root-relative paths; the bundler prefixes the deployed base path:

```html
<link rel="icon" href="/brand/favicon.svg" type="image/svg+xml" />
<link rel="icon" href="/brand/favicon-32.png" type="image/png" sizes="32x32" />
<link rel="icon" href="/brand/favicon.ico" sizes="48x48" />
<link rel="apple-touch-icon" href="/brand/apple-touch-icon.png" />
```

Check the built `index.html` for the prefixed paths when the app is served under a sub-path (GitHub Pages). In the
title bar, import the mark as a URL so it is fingerprinted with the bundle, and draw it before the app name:

```tsx
import markUrl from './assets/brand/energyatlas-mark.svg'

<span className={styles.brand}>
  <img className={styles.brandMark} src={markUrl} alt="" />
  EnergyAtlas UI
</span>
```

## Checks

- The favicon at 16 and 32 px in a light and a dark browser tab bar, and the header in every theme at the minimum and a
  phone width.
- Every brand file is requested from the site's own origin, under its base path, with status 200.
- The knockout mark appears only on known-light surfaces; a dark theme shows the white-E mark.

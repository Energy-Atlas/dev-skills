# Spec section 0 template

Put this at the top of the site's design spec (for example `design/ui-design-spec.md`, outside `docs_dir`). Replace the
angle-bracket placeholders; delete what does not apply. Keep the numbering stable once other text refers to it; add new
sections at the end of section 0 rather than renumbering.

```markdown
# <Site name> — UI Design Specification

This specification restyles the <site name> into the visual family of <brand or sister site>. Section 0 records the
decisions taken for this site. **Where section 0 and a later section disagree, section 0 wins.**

---

## 0. Implementation Decisions

Decided by <owner> on <YYYY-MM-DD>. These are implementation rules, not one-off clarifications.

### 0.1 Brand

- The site stays **<site name>**. This is a visual-family alignment with <brand>, not a rename.
- Keep the title, identity, logo, and favicon. Do not add "<brand>" branding to the header, title, footer, or pages.

### 0.2 Sources of truth

- **Reference UI:** <what it is>. <It is / It is not> kept in this repository; section 0.11 describes it.
- **Palette:** <live CSS URL>. If it diverges from this document, it is authoritative, except where section 0.6 adjusts a
  value for contrast. The values here match it as of <date>.

### 0.3 Theme behaviour

- The default theme follows the system preference; the light/dark toggle stays. Never force a scheme.
- Dark mode receives the strongest version of the reference; light mode keeps the same grid, typography, and framing.

### 0.4 Fonts

- Families: <sans> (primary), <mono> (technical labels), <serif> (sparse editorial accent).
- Self-hosted in `docs/assets/fonts/` with their licences, declared in `docs/assets/stylesheets/fonts.css`;
  `theme.font: false`. The browser contacts no font host.

### 0.5 Colour roles

| Role | Dark | Light | Use |
| --- | --- | --- | --- |
| Info / interactive accent | `<hex>` | `<hex>` | links, navigation, information, active and selected states |
| Success | `<hex>` | `<hex>` | success states |
| Warning | `<hex>` | `<hex>` | warnings |
| Error | `<hex>` | `<hex>` | errors, destructive actions, failures |
| Primary (brand) | `<hex>` | `<hex>` | deep branded fill or background only |

- Red only for error, destructive, and failure states; never a decorative accent.
- Admonitions: `note`, `info`, `abstract`, `tip`, `question` blue; `success` green; `warning` amber; `danger`, `failure`,
  `bug`, `error` red; `example`, `quote` muted.

### 0.6 Contrast

Targets (WCAG 2.2 AA): text below 24 px (18.66 px bold) at least 4.5:1 on every surface it sits on; large text 3:1;
borders of controls and state indicators 3:1; decorative grid rules may stay lighter.

| Token | Theme | Spec value | Used value | Contrast of used value |
| --- | --- | --- | --- | --- |
| `--ui-text-muted` | dark | `<hex>` (<ratio> on <bg>) | `<hex>` | <ratios> |
| `--ui-text-muted` | light | `<hex>` | `<hex>` | <ratios> |
| `--ui-border-subtle` | both | `<hex>` | unchanged | decorative only |
| `--ui-border-interactive` | dark | — | `<hex>` | <ratios> |
| `--ui-border-interactive` | light | — | `<hex>` | <ratios> |

### 0.7 Landing page

- A restrained hero followed immediately by the shared-border grid; not a marketing page.
- Headline: `<first phrase>` in <sans>, `<serif phrase>` in <serif> italic; one or two sentences of supporting copy.
- The landing page hides both sidebars but keeps their widths as empty margins, without their rules, so its text starts
  where every other page's text starts. Strips and grid rules still run from frame to frame.
- The headline is sized to the hero's width (container query units) so its first phrase stays on one line on desktop.

### 0.8 Numbered section strips

Only on the landing page, section index pages, and other deliberately designed overview pages. Never automatic on the
`##` headings of ordinary pages.

### 0.9 Content width

Prose is capped at about <760–900 px>. Reference pages, large diagrams, data matrices, and wide tables are exempt; wide
tables scroll inside a bounded container; the page never overflows horizontally.

### 0.10 Breadcrumbs

`navigation.path` on; small mono, muted, `/` separators, no bar, background, or border.

### 0.11 The reference, described

- **Surface:** <...>
- **Page frame:** <vertical rules, horizontal rules, registration marks>
- **Header:** <height, labels, dividers, active item, primary action>
- **Section strip:** <height, left index, right annotation>
- **Hero:** <scale, weight, serif word, supporting copy>
- **Cell row:** <columns, shared borders, index letter, title, description, button>
- **Not adopted:** <decoration that conflicts with the motion or documentation rules>

### 0.12 Stable page changes

- `navigation.instant` and `navigation.instant.progress` are on.
- `html` reserves the scrollbar's width (`scrollbar-gutter: stable`).
- `overrides/main.html` preloads the two most-used font files.

### 0.13 Grid cells

- A cell whose title is a link is clickable as a whole; other links in it keep their own targets.
- Cell text is padded by the article gutter, so it lines up with strips and prose.
- Every cell is closed on all four sides; where an empty sidebar margin moves a grid in from the frame, the grid draws its
  own outer rules.
```

Also update the body of the spec where it would otherwise contradict section 0: the colour token blocks (adjusted values,
split borders, semantic colours, no decorative red), example headlines, the strip scope, the width rule, button and search
borders (interactive), and the light theme's token names.

# Decisions section template

Put this where the project records design decisions: as a decision record (`docs/decisions/NNNN-ui-alignment.md`) with
the audit and status in its alignment record, or as section 0 of a spec outside any published folder
(`design/ui-design-spec.md`). Replace the angle-bracket placeholders; delete what does not apply. Keep the numbering
stable once other text refers to it.

```markdown
# <NNNN or 0>: UI alignment with <reference>

Date: <YYYY-MM-DD>

Status: decided by <owner> on <date>, before implementation; section 10 records what changed while building. Where this
record and the reference disagree, this record wins. Where it and the app's design guidelines disagree, section 1 says
which wins.

## Context

- **Reference:** <what it is: a sister site, its spec, a screenshot>. <It is / It is not> kept in this repository;
  section 9 describes it.
- **Palette source:** <file or URL>, as of <date>.
- **The app's own rules:** <guidelines, decision records, token module> (<paths>).
- **Audit:** <the counts from style_audit.py at <commit>>, and the conflicts in section 1.

## 1. Precedence

| Conflict | Reference | App rule | Decision |
| --- | --- | --- | --- |
| Borders | <every section ruled> | <fewer borders, grouping by spacing> | <app / reference / mix: ...> |
| Type sizes | <display and editorial sizes> | <N sizes> | <...> |
| Monospace | <label font> | <code font> | <...> |
| Theme set | <light and dark> | <the app's themes> | <...> |
| Label style | <mono caps labels> | <the interface sans> | <as written / mono caps, with the label token values> |
| <...> | | | |

## 2. Brand

- The app stays **<app name>**: name, logo, favicon, and wording unchanged.

## 3. Themes and surfaces

- Themes that take the reference palette: <list>. Others: <keep palette, take structure / unchanged>.
- Default: <system preference>; the switch stays; never forced. First frame: <inline script / CSS fallback>.
- Surface mapping: panes <reference base>, background behind panes <...>, raised <...>, overlay <...>.

## 4. Fonts

- Families: <sans> (interface, labels), <mono> (code, identifiers; labels only with mono caps), <serif?> (<where, or not used>).
- Delivered by <package and version / vendored files with licences and their source>; no font host at runtime.
  <Package-policy note if files are vendored rather than installed.>
- Tabular numerals in <grids, meters, axes>.

## 5. Type scale

| Token | Size | Roles |
| --- | --- | --- |
| `<--font-size-small>` | <12px> | metadata, labels, table headers |
| `<--font-size-base>` | <13px> | content, controls |
| `<--font-size-title>` | <15px> | page, panel, and dialog titles |
| `<--font-size-label>` | <11px> | <only with mono caps labels> |

## 6. Colour roles and contrast

| Role | Dark | Light | Use |
| --- | --- | --- | --- |
| Accent | `<hex>` | `<hex>` | links, focus, active and selected states |
| Success / Info / Warning / Danger | `<hex>` | `<hex>` | state only, always with an icon or label |
| Brand fill | `<hex>` | `<hex>` | fills only, never text on dark |

| Token | Theme | Reference value | Used value | Contrast of used value |
| --- | --- | --- | --- | --- |
| `<--color-text-muted>` | <theme> | `<hex>` (<ratio>) | `<hex>` | <ratios on each surface> |
| `<--color-border-interactive>` | <theme> | — | `<hex>` | <ratios> |

New tokens this alignment adds, defined in every theme (curated ones included, with contrast-fixed values):

| Token | Role | Values |
| --- | --- | --- |
| `<--color-border-interactive>` | edges of controls, 3:1 on every surface | <per theme> |
| `<--color-surface-overlay>` | menus, popovers, dialogs | <per theme> |
| `<--rule>`, `<--transition>` | <...> | <...> |
| `<--label-font>`, `<--label-case>`, `<--label-size>`, `<--label-tracking>`, `<--label-weight>` | the label style | <values> |

The contrast test is `<path>`; it covers every theme, tone text on its tint, and any outline drawn on a fill.

## 7. Shapes, borders, and elevation

- Radii: <0 / 2px>. Borders: <where>. Elevation: <one overlay shadow / borders only>.

## 8. Component treatments

- **Tab strips** (shell and docked panels): <label style; active tab treatment>.
- **Titles** (page, panel, card, form, dialog, section): <the app's design / strips, with what changes>.
- **States** per interactive kind (tab, side handle, button, menu item, row): <rest / hover / selected / pressed /
  focus / disabled, with the label colour and the indicator of each>.
- **Buttons:** <primary, secondary, quiet, destructive; case and font>.
- **Inputs and selection controls:** <...>.
- **Data grid:** <header style, rules, row hover and selection>.
- **Charts:** <scaffolding, labels, tooltip>. **Map:** <basemap, overlays, legend>.
- **Overlays:** <menus, popovers, dialogs, toasts>.
- **States:** <empty, loading, warning, error>.

## 9. The reference, described

- **Surface:** <...> **Framing:** <...> **Header:** <...> **Labels:** <...> **Active item:** <...>
- **Not adopted:** <hero, editorial display type, decoration that does not suit a dense app>.

## 10. Deviations during implementation

- <what differs from the above and why; library overrides and limits accepted>. Filled by the last commit.

## 11. Amendments the app's guidelines would need

Only when the reference wins over owner-maintained guidelines. The owner decides whether to make them.

- <section>: <current text, in short> → <proposed text>.
```

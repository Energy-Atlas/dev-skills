# Translating a reference UI into an application

A reference UI is usually a page: a documentation site, a marketing site, a screenshot of one. An application has
different parts. Fill this table in phase 2 for the actual reference and app, mark every conflict with the app's own
design rules, and take the conflicts to the owner (phase 3).

The two right-hand columns are defaults for the two usual precedence decisions: **app wins** (the app's design rules
stand; the reference supplies palette, typography, and treatments where they leave room) and **reference wins** (the
reference's language applies across the app; the app's rules are amended by their owner).

## Elements

The rows use the grid-framed editorial family of `wiki-ui-alignment` as the example reference.

| Reference element | App equivalent | App wins | Reference wins |
| --- | --- | --- | --- |
| Near-black page surface, off-white text, mid-grey secondary text | App background, pane surfaces, text tokens | Adopt in the dark theme; light theme keeps its structure with the family's light palette | Same |
| Raised surfaces in steps (`surface-1`, `-2`, `-3`) | Pane, raised (header, toolbar, hover), and overlay surfaces | Map onto the app's existing surface roles | Same |
| Content column framed by two vertical rules | The shell's outer edge and pane boundaries | Pane boundaries and splitters only, in `border-subtle` | Shell framed; every pane and tab strip ruled; panel sections ruled |
| Horizontal rules between sections, meeting the frame | Rules under tab strips, toolbars, panel headers | Under tab strips and the shell's bars only; inside panels group by spacing and surface tone | Also between panel sections and dashboard rows |
| `+` registration marks at rule intersections | Shell corners | Drop | Optional, at the shell's outer corners only; never inside data views |
| Low one-line header with a bottom rule | Title bar, menu bar, ribbon | Keep the app's bar; adopt the bottom rule and label style | Same, and flatten the ribbon to one line where the app allows |
| Nav labels: small uppercase, widely tracked mono | Shell tabs, docked panel tabs, ribbon tab names | Shell and panel tabs in the app's mono, 11–12 px, uppercase, tracked 0.06–0.1 em | Same, in the reference's mono |
| Thin vertical dividers between nav groups | Toolbar separators | Adopt (1 px `border-subtle`) | Same |
| Active nav item: inverted block in a thin accent outline | Selected tab in tab strips | Selected tab: text colour and an accent underline or inset edge (works inside overflow containers) | Inverted block (text-coloured fill, background-coloured label) with a 1 px accent outline drawn inset |
| Primary action: full-height inverted block | Primary command (Run, Save, Submit) | Accent fill, square, compact | Inverted block (text-coloured fill) with accent on hover and focus |
| Section strip `02 / OWNERSHIP` with a right-aligned note | Panel header with title and a right-aligned status or count | Panel titles in the app's title size and weight; a right-aligned muted note where useful | Panel headers as strips: mono uppercase muted label, optional index, right-aligned note, ruled above and below |
| Hero: very large bold headline with a serif italic phrase | Welcome or empty start screen | Drop | One welcome or empty state at most; never in working views |
| Feature row: equal cells with shared borders, letter index, bold title | Dashboard tiles, stat tiles, cards | Tiles grouped by spacing and surface tone, no outlines | Shared-border grid of tiles, closed on all four sides |
| Small square outlined button, mono uppercase label | Secondary and quiet buttons | Square, `border-interactive`, sentence case in the sans | Square, mono uppercase for toolbar buttons; sentence case in dialogs and forms |
| Data-sheet tables: mono uppercase headers, thin rules, accent tint on hover | Data grid | Header labels small and muted; thin row rules; accent-tint hover; selection tint | Mono uppercase headers, column rules, accent-tint hover |
| Admonitions with a coloured left edge | Notices, banners, validation summaries, toasts | Left edge or icon in the tone colour on a tint | Same, with a mono uppercase title |
| Code blocks in the mono | Logs, identifiers, operation history, expressions | The app's code font | The reference's mono, if the owner adopts it |
| Breadcrumbs: small muted mono | Location or path indicator, selection path | Only if the app has one | Same |
| Muted page footer with meta line | Status bar | Status bar text muted, small; tone colours only for state | Status bar labels mono uppercase |
| Square corners, no shadows | All controls and surfaces | Radii 0–2 px; one overlay shadow for menus and dialogs | Radii 0; overlays separated by a border and the raised surface |
| 150 ms colour transitions | Hover and focus | Adopt; none under reduced motion | Same |
| Scroll ruler, oversized outline section names, page decoration | — | Drop | Drop |

## What only an app has

The reference does not say how to style these; derive them from its tokens and treatments and record the result in the
spec's section 8.

- **Selection** in grids, trees, lists, maps, and charts: one selection tint and one selection outline colour, shared.
- **Focus** inside composite widgets (grid cells, tree items, tabs, menu items): a visible 2 px accent ring, inset where
  an outer ring would be clipped.
- **Disabled with a reason:** reduced contrast still readable (it is exempt from 4.5:1, but should stay legible) and a
  tooltip or inline text that says why.
- **Invalid fields:** danger edge and a message, not colour alone.
- **Running and pending states:** progress indicators in the accent; no colour that reads as success before it is one.
- **Drag and drop:** drop indicators and drag previews in the accent, the docking library's included.
- **Splitters and resize handles:** a hairline at rest, a wider hit area, the accent on hover and drag.
- **Scrollbars:** `scrollbar-color` from the tokens, or the library's own scroll indicators themed.
- **Canvas and WebGL:** chart and map colours from the resolved tokens; text in canvases in the app's family once it has
  loaded.

## Density

A documentation page is read; an app is worked. Keep the app's row heights, control heights, and paddings unless the
owner asks for a looser layout. Adopt the reference's typography by role (label, content, title), not its sizes.

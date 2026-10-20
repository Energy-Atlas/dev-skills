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
| Near-black page surface, off-white text, mid-grey secondary text | App background, pane surfaces, text tokens | Adopt in the dark theme; light theme takes the family's light palette | Same |
| Raised surfaces in steps (`surface-1`, `-2`, `-3`) | Gutters, strips, raised headers, hover, overlays | See "Surfaces" below | Same |
| Content column framed by two vertical rules | The shell's outer edge and pane boundaries | Pane boundaries and splitters only, in `border-subtle` | Shell framed; every pane and tab strip ruled; panel sections ruled |
| Horizontal rules between sections, meeting the frame | Rules under tab strips, toolbars, panel headers | Under tab strips and the shell's bars only; inside panels group by spacing and surface tone | Also between panel sections and dashboard rows |
| `+` registration marks at rule intersections | Shell corners | Drop | Optional, at the shell's outer corners only; never inside data views |
| Low one-line header with a bottom rule | Title bar, menu bar, ribbon | Keep the app's bar; adopt the bottom rule | Same, with mono uppercase menu names |
| Nav labels: small uppercase, widely tracked | Shell tabs, docked panel tabs, ribbon tab names | Uppercase in the app's interface family (or its mono, only if the app allows mono outside code), 11–12 px, tracked 0.04–0.08 em | Uppercase in the reference's mono, tracked 0.04–0.1 em |
| Thin vertical dividers between nav groups | Toolbar separators | Adopt (1 px `border-subtle`) | Same |
| Active nav item: inverted block in a thin accent outline | Selected tab in tab strips | Selected tab: text colour and an inset accent edge (works inside overflow containers) | Inverted block (text-coloured fill, background-coloured label) with the accent outline drawn inset behind a strip-coloured gap; the accent never touches the fill (see pitfalls) |
| Primary action: full-height inverted block | Primary command (Run, Save, Submit) | Accent fill, square, compact | Inverted block (text-coloured fill) with accent on hover and focus |
| Section strip `02 / OWNERSHIP` with a right-aligned note | Panel header with title and a right-aligned status or count | Panel titles in the app's title size and weight; a right-aligned muted note where useful | Panel headers as strips: mono uppercase muted label, optional index, right-aligned note, ruled above and below, full bleed |
| Hero: very large bold headline with a serif italic phrase | Welcome or empty start screen | Drop | One welcome or empty state at most; never in working views |
| Feature row: equal cells with shared borders, letter index, bold title | Dashboard tiles, stat tiles, cards | Tiles grouped by spacing and surface tone, no outlines | Shared-border grid of tiles, closed on all four sides; tile labels mono uppercase, values in the interface sans |
| Small square outlined button, mono uppercase label | Buttons | Square, `border-interactive`, sentence case in the interface family | Toolbar and panel command buttons with short verb labels: mono uppercase; dialog, form, and menu buttons: sentence case |
| Data-sheet tables: mono uppercase headers, thin rules, accent tint on hover | Data grid | Header labels small and muted, sentence case; row rules; accent-tint hover; selection tint | Mono headers, uppercase only where the header carries no unit or name (see "Label case"); header wrapping instead of truncation; column and row rules |
| Admonitions with a coloured left edge | Notices, banners, validation summaries, toasts | Left edge or icon in the tone colour on a tint | Same, with a mono uppercase title |
| Code blocks in the mono | Logs, identifiers, operation history, expressions | The app's code font | The reference's mono, if the owner adopts it |
| Small muted metadata labels | Status badges and pills (Simulated, Planned, Complete) | The app's badge style in tone colours, sentence case | Mono uppercase, muted, no fill; tone colour only for attention states |
| Section titles inside long pages | Form section headers, settings groups | The app's title size and weight | Strips: mono uppercase muted label with a rule |
| Breadcrumbs: small muted mono | Location or path indicator, selection path | Only if the app has one | Same |
| Muted page footer with meta line | Status bar | Status bar text muted, small; tone colours only for state | Status bar labels mono uppercase where they are labels, not messages |
| Square corners, no shadows | All controls and surfaces | Radii 0–2 px; overlays on a lighter surface with a rule | Radii 0; overlays separated by a rule and the overlay surface |
| 150 ms colour transitions | Hover and focus | Adopt; none under reduced motion | Same |
| Scroll ruler, oversized outline section names, page decoration | — | Drop | Drop |

## Surfaces

A documentation page puts its content on the base (black or white) and uses the raised surfaces for code blocks, strips,
and hover. An app's content panes are its "page", so in either precedence:

| Reference surface | App role |
| --- | --- |
| Base (`#000000` / `#ffffff` in the family) | Content panes: grids, charts, maps, forms, panel bodies |
| Surface 1 | The background behind panes (gutters, splitters), strips, the status bar, overlays in dark |
| Surface 2 | Raised headers, toolbars, hover, selected rows without a tint, overlays in light |
| Surface 3 | Non-text fills only (pressed controls, scrollbar thumbs); text and control edges fail on it in the family dark |

Check how the app uses its surface tokens (phase 1) before mapping: a token named `surface` may paint every pane, and a
token named `bg` only the gutters.

## Label case

Uppercase is a property of a few kinds of label, never of data.

| Kind of text | App wins | Reference wins |
| --- | --- | --- |
| Shell and panel tab labels | Uppercase | Uppercase, mono |
| Panel headers and section strips | Sentence case title, or uppercase muted label | Uppercase, mono, muted |
| Grid and table headers | Sentence case | Uppercase mono, except headers with a unit, symbol, or proper name |
| Toolbar command buttons (short verbs: Apply, Reset, Inspect) | Sentence case | Uppercase, mono |
| Dialog, form, and menu buttons; menu items | Sentence case | Sentence case |
| Form labels, messages, agent text, suggestions, notifications | Sentence case | Sentence case |
| Metadata badges | Sentence case | Uppercase, mono, muted |
| Anything with a unit, identifier, file name, place name, or value (`m²`, `kWh`, `kVA`, `B0001`, `Back Bay`) | Keep as written | Keep as written |

Change case with `text-transform` only: accessible names and `textContent` keep the source text, so screen readers and
tests that read names are unaffected (`innerText` does change). A label that mixes a word and a unit, such as
`Monthly demand (MWh)`, stays as written, or puts the unit in a child element with `text-transform: none`.

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
owner asks for a looser layout. Adopt the reference's typography by role (label, content, title), not its sizes. Mono
and uppercase labels are about 10 % wider than sentence-case sans at the same size: check tab strips and headers at the
minimum size and trade tracking and padding until they fit as before.

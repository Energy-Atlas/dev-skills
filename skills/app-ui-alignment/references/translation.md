# Translating a reference UI into an application

A reference UI is usually a page: a documentation site, a marketing site, a screenshot of one. An application has
different parts. Fill this table in phase 2 for the actual reference and app, mark every conflict with the app's own
design rules, and take the conflicts to the owner (phase 3).

The two right-hand columns are defaults for the two usual precedence decisions: **app wins** (the app's design rules
stand; the reference supplies palette, typography, and treatments where they leave room) and **reference wins** (the
reference's language applies across the app; the app's rules are amended by their owner). In both columns, "label"
means the label style, a separate decision ("Label style" below): where labels go follows precedence, how they are set
does not.

## Elements

The rows use the grid-framed editorial family of `wiki-ui-alignment` as the example reference.

| Reference element | App equivalent | App wins | Reference wins |
| --- | --- | --- | --- |
| Near-black page surface, off-white text, mid-grey secondary text | App background, pane surfaces, text tokens | Adopt in the dark theme; light theme takes the family's light palette | Same |
| Raised surfaces in steps (`surface-1`, `-2`, `-3`) | Gutters, strips, raised headers, hover, overlays | See "Surfaces" below | Same |
| Content column framed by two vertical rules | The shell's outer edge and pane boundaries | Pane boundaries and splitters only, in `border-subtle` | Shell framed; every pane and tab strip ruled; panel sections ruled |
| Horizontal rules between sections, meeting the frame | Rules under tab strips, toolbars, panel headers | Under tab strips and the shell's bars only; inside panels group by spacing and surface tone | Also between panel sections and dashboard rows |
| `+` registration marks at rule intersections | Shell corners | Drop | Optional, at the shell's outer corners only; never inside data views |
| Low one-line header with a bottom rule | Title bar, menu bar, ribbon | Keep the app's bar; adopt the bottom rule | Same, with menu names in the label style |
| Nav labels: small uppercase, widely tracked | Shell tabs, docked panel tabs, ribbon tab names | Label style, muted, the active tab in the text colour | Label style, muted; the active tab as below |
| Thin vertical dividers between nav groups | Toolbar separators | Adopt (1 px `border-subtle`) | Same |
| Active nav item: inverted block in a thin accent outline | Selected tab in tab strips | Selected tab: text colour and an inset accent edge (works inside overflow containers) | Inverted block (text-coloured fill, background-coloured label) with the accent outline drawn inset behind a strip-coloured gap; the accent never touches the fill (see pitfalls) |
| Primary action: full-height inverted block | Primary command (Run, Save, Submit) | Accent fill, square, compact | Inverted block (text-coloured fill) with accent on hover and focus |
| Section strip `02 / OWNERSHIP` with a right-aligned note | Panel header with title and a right-aligned status or count | The app's panel titles as they are; a right-aligned muted note where useful | The app's panel titles as they are (title style, no backdrop); a rule below only if the panel had one. Strips are opt-in |
| Hero: very large bold headline with a serif italic phrase | Welcome or empty start screen | Drop | One welcome or empty state at most; never in working views |
| Feature row: equal cells with shared borders, letter index, bold title | Dashboard tiles, stat tiles, cards | Tiles grouped by spacing and surface tone, no outlines | Shared-border grid of tiles, closed on all four sides; tile labels in the label style, values in the interface sans |
| Small square outlined button, mono uppercase label | Buttons | Square, `border-interactive`, sentence case in the interface family | Square, `border-interactive`; toolbar and panel command buttons may take the label style; dialog, form, and menu buttons stay in the interface family as written |
| Data-sheet tables: mono uppercase headers, thin rules, accent tint on hover | Data grid | Header labels small and muted, sentence case; row rules; accent-tint hover; selection tint | Headers in the label style; header wrapping instead of truncation if the label style is wider; column and row rules |
| Admonitions with a coloured left edge | Notices, banners, validation summaries, toasts | Left edge or icon in the tone colour on a tint | Same, with the title in the label style |
| Code blocks in the mono | Logs, identifiers, operation history, expressions | The app's code font | The reference's mono, if the owner adopts it |
| Small muted metadata labels | Status badges and pills (Simulated, Planned, Complete) | The app's badge style in tone colours, sentence case | Label style, muted, no fill; tone colour only for attention states |
| Section titles inside long pages | Form section headers, settings groups, Inspection sections | The app's title size and weight | The app's titles; a rule above the section where the reference rules sections |
| Breadcrumbs: small muted mono | Location or path indicator, selection path | Only if the app has one | Same |
| Muted page footer with meta line | Status bar | Status bar text muted, small; tone colours only for state | Status bar labels in the label style where they are labels, not messages |
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

## Label style

Where labels go (tab strips, side handles, grid headers, tile labels, the status bar, badges) follows precedence.
Titles are not labels: page, panel, card, form, dialog, and section titles keep the app's title style (size, weight,
text colour, no tracking) and no backdrop in either precedence; turning them into strips is an opt-in. How they are set is its own decision, made through tokens so it can change in one place:

| Token | As written (default) | Mono caps (opt-in) |
| --- | --- | --- |
| `--label-font` | `var(--font-sans)` | `var(--font-mono)` |
| `--label-case` | `none` | `uppercase` |
| `--label-size` | `var(--font-size-small)` | `var(--font-size-label)` (one step smaller) |
| `--label-tracking` | `0` | `0.04em` to `0.08em` |
| `--label-weight` | `600` | `600` |

Every label rule reads these five tokens; no rule sets `text-transform: uppercase` or the mono family itself.

**The default is as written, in the interface sans, in either precedence.** The reference's mono caps make the
documentation family's strips and navigation read like a technical drawing; on a dense app with dozens of tabs and
headers on screen, owners have found them tiring once they used them, and they widen labels, truncate grid headers, and
change units. Offer mono caps as an opt-in, show it on the running app, and decide from that.

With mono caps chosen, these keep their case and the interface font regardless: dialog, form, and menu buttons; menu
items; form labels; messages, agent text, suggestions, and notifications; and anything with a unit, identifier, file
name, place name, or value (`m²`, `kWh`, `kVA`, `B0001`, `Back Bay`). A label that mixes a word and a unit, such as
`Monthly demand (MWh)`, stays as written, or puts the unit in a child element with `text-transform: none`.

Change case with `text-transform` only: accessible names and `textContent` keep the source text, so screen readers and
tests that read names are unaffected (`innerText` does change).

## States

The reference shows a page at rest; an app's chrome is used. Every interactive kind needs its states designed, not
inherited from a library:

| State | Label | Indicator |
| --- | --- | --- |
| Rest | muted or text colour, 4.5:1 on the strip | none, or the rest edge |
| Hover | text colour, 4.5:1 on the hover background | an edge, underline, or fill whose boundary is 3:1 against the strip |
| Selected | 4.5:1 on the selected background (inverted: the surface colour on the text-coloured fill) | the fill, or an accent edge at 3:1 on the strip, never on the fill |
| Pressed | as hover | as hover, plus the fill of the next state |
| Focus | unchanged | a 2 px focus ring at 3:1, inset where the container clips |
| Disabled | muted, still legible | none; a reason on hover or beside it |

Hover and selected must also differ from each other. With an inverted selected tab, a hover that only lightens the
background is lost against the strip; a 1 px interactive edge with the text colour reads at once. Fade only the hover;
selection changes at once.

## Controls

A flat, square reference makes every control the same box: a 1 px edge around the pane colour. An app needs its
controls told apart by what they do: **fields hold a value, buttons act.** Each kind differs from the others in at
least two of fill, edge, and content, so it reads at a glance and in greyscale.

| Kind | Fill | Edge | Content | Hover / focus |
| --- | --- | --- | --- | --- |
| Text input, search field | A well: `--field-bg`, the pane colour (recessed on raised strips) | Even 1 px interactive edge with a 2 px bottom edge | Value left; muted placeholder; text cursor | No fill change; the edge turns accent on focus |
| Select, value picker | The same well | The same edges | Value left, then a chevron in its own cell behind a 1 px rule | As the input; the open picker inverts the chevron cell |
| Secondary button | Raised: `--button-bg` (the text colour at about 8 % over the surface) | Even 1 px interactive edge | Centred verb, optional leading icon | Fill steps up (`--button-bg-hover`), edge turns accent; pressed steps further |
| Primary button | Inverted block or accent fill | None needed | Centred verb | Accent fill |
| Quiet and icon buttons | None at rest | None at rest | Icon or short verb | An interactive edge and the hover fill appear (the state rule) |
| Split button | As primary or secondary | A rule before the chevron part | Verb, then chevron | Each part on its own |
| Segmented control, toggle group | Shared-border cells | Shared rules | Short labels | Selected cell inverted, as with tabs |
| Stepper buttons inside a number field | `--button-bg` | On the field's bottom line | Minus, plus | As secondary buttons |

- A dashed edge means disabled, and nothing else; a disabled button loses its fill.
- Every control keeps one height, so a toolbar of fields and buttons shares a baseline.
- The well and the raised fill are only a step apart; the edges carry the 3:1. Keep muted text off hover and pressed
  fills, and check it on the rest fill.

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
caps labels are about 10 % wider than sentence-case sans at the same size: if they are chosen, check tab strips and
headers at the minimum size and trade tracking and padding until they fit as before.

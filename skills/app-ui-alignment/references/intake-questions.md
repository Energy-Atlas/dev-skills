# Intake questions

Ask the questions the inputs leave open, each with a recommendation and the evidence from the audit (counts, contrast
ratios, screenshots). Record every answer in the decisions section (`spec-decisions-template.md`). Questions marked
*blocking* change what you build; ask them before implementing. The others have a sensible default: state it and go
ahead unless the owner objects.

## Blocking

1. **Precedence.** For each conflict between the reference and the app's own design rules (the translation table lists
   them), which wins? Ask per conflict, not once for all. *Default: the app's rules win; the reference contributes
   palette, typography, and the treatment of tabs, labels, and controls wherever the app's rules leave room.* If the
   owner wants to see both, build them as variants (SKILL.md, phase 3).
2. **Reference UI.** Is it attached? May a screenshot be committed, or must it be described in words?
3. **Brand.** Visual-family alignment (keep the app's name, logo, favicon, wording) or a rename? *Default: alignment.*
4. **Palette source of truth.** Which file or URL is authoritative? Where are the semantic state colours (success, info,
   warning, danger), which specs often omit? *Default: the sister site's live CSS; contrast fixes override it.*
5. **Pane surface.** Which reference surface do the app's content panes take: the reference's page base (black or
   white, where its content sits) or its first raised surface? This decides the whole dark look. *Default: the base for
   panes; the first surface for gutters, strips, and the status bar; the second for raised headers and hover
   (`translation.md`, "Surfaces").*
6. **Theme set.** The reference usually has a light and a dark theme; the app may ship more (curated appearances,
   high-contrast). Which take the reference palette: only light and dark, a new pair added beside the existing ones, or
   all of them? *Default: restyle the app's light and dark themes; the other themes keep their palettes but take the
   new structure (tokens, typography, shapes), with contrast-fixed values for every new role.*
7. **Default theme.** Follow the system preference, or force one? *Default: system preference with the app's switch; the
   dark theme may get the strongest expression of the reference, but is never forced.*
8. **Fonts.** The reference's families, the app's families, or a mix? A second monospace family (the reference's label
   font) next to the app's code font? Does the app limit its monospace to code? Labels are question 9, not this one.
   *Default: keep a font the owner chose
   deliberately (a decision record says so); otherwise adopt the reference's families, delivered from the bundle. If
   new font files are vendored rather than installed as a package, ask whether the package policy allows it.*
9. **Label style.** Labels keep the places precedence gives them (tab strips, strips, grid headers, the status bar);
   their font and case are a separate question, answered through the label tokens (`translation.md`, "Label style").
   *Default: as written, in the interface sans, in either precedence; offer the reference's mono caps as an opt-in and
   show both on the running app before deciding. Never change the case of a label that carries a unit, an identifier,
   a name, or a data value.*

## Defaults to confirm

10. **Titles.** Do page, panel, card, form, dialog, and section titles keep the app's design, or become the
    reference's strips (a raised backdrop, a muted label)? *Default: they keep the app's design in either precedence;
    strips only where the owner asks after seeing them.*

11. **Type scale.** Dense apps need fewer, smaller sizes than a documentation site. Keep the app's scale (often two or
    three sizes around 12–15 px) and map the reference's roles onto it, rather than importing editorial sizes; if the
    label style needs a smaller size (mono caps), add one label size. *Default: yes; the reference's display sizes and
    serif accent are dropped or kept for one empty or welcome state.*
12. **Borders and framing.** A grid-framed reference rules every section; an app with docked panes already has many
    edges. *Default (app wins): rules on pane boundaries, tab strips, and the shell; group inside panels by spacing and
    surface tone. Reference wins: also between panel sections and around tiles.*
13. **Minimum size.** What must still fit at the minimum supported size, for example every page tab visible at
    1280 × 800 with both side panels open? Wider labels (mono caps, tracking) are traded against padding and
    tracking until it does. *Default: everything that fitted before still fits.*
14. **Wider labels in fixed layouts.** When headers grow (mono caps, longer text), may the restyle change component
    configuration (grid header wrapping) rather than column widths or the label treatment? *Default: yes, wrapping;
    column widths stay.*
15. **Corners and elevation.** Square corners (0–2 px) and no shadows, except one overlay treatment (a lighter surface
    and a rule, or a shadow where it shows) for menus, popovers, and dialogs. *Default: yes.*
16. **Contrast.** Adjust colours that fail WCAG AA (give the ratios), split decorative and interactive borders, use a
    deep brand colour that fails on dark only as a fill. *Default: yes.*
17. **Red.** Red only for errors, destructive actions, and failures; amber warnings, green success, blue links,
    information, focus, and selection. *Default: yes.*
18. **Data colours.** Keep the app's chart and map palettes (they encode meaning and were validated), or derive new ones
    from the brand? *Default: keep them; re-check them at 3:1 against the new chart surfaces.*
19. **First frame.** May the restyle add an inline script to `index.html` that applies the stored theme before the first
    paint (a content security policy or the host may forbid inline scripts)? *Default: yes, unless a CSP forbids it;
    then a CSS media-query fallback for the system preference.*
20. **Agent rule.** Add a rule to `AGENTS.md` (or equivalent) that UI changes follow the recorded spec. *Default: yes.*

## Questions that come up later

- **Behaviour found during the restyle.** A control that does nothing, a state that is never shown, a label that is
  wrong: report it and ask; do not fix it inside the restyle.
- **Pre-existing accessibility findings.** A violation the base branch already had: fix it inside the restyle only if
  it is a colour or contrast finding the restyle touches; otherwise log it with the base commit. *Default: log.*
- **Theme descriptions.** When a theme's palette changes, may its user-facing description change with it? *Default:
  only if it would otherwise be wrong.*
- **Third-party limits.** A library cannot take the reference's treatment (a fixed tab shape, canvas text that cannot use
  the web font, map labels from glyph files). Ask whether to accept the limit, override the library's CSS (and own the
  maintenance), or replace the component (a package decision).
- **Font provenance.** A vendored font copied from a sister repository: record its source commit and date if the
  upstream version is unknown.
- **Tagging.** A restyle merge is not a release; ask whether to tag at all.

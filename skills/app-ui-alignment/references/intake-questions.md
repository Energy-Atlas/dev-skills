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
5. **Theme set.** The reference usually has a light and a dark theme; the app may ship more (curated appearances,
   high-contrast). Which of the app's themes take the reference palette: only light and dark, a new pair added beside
   the existing ones, or all of them? *Default: restyle the app's light and dark themes; leave other curated themes
   their palettes but give them the new structure (tokens, typography, shapes).*
6. **Default theme.** Follow the system preference, or force one? *Default: system preference with the app's switch; the
   dark theme may get the strongest expression of the reference, but is never forced.*
7. **Fonts.** The reference's families, the app's families, or a mix? A second monospace family (the reference's label
   font) next to the app's code font? *Default: keep a font the owner chose deliberately (a decision record says so);
   otherwise adopt the reference's families, delivered from the bundle.*

## Defaults to confirm

8. **Type scale.** Dense apps need fewer, smaller sizes than a documentation site. Keep the app's scale (often two or
   three sizes around 12–15 px) and map the reference's roles onto it, rather than importing editorial sizes.
   *Default: yes; the reference's display sizes and serif accent are dropped or kept for one empty or welcome state.*
9. **Borders and framing.** A grid-framed reference rules every section; an app with docked panes already has many
   edges. Keep the reference's rules on pane boundaries, tab strips, and the shell, and group inside panels by spacing
   and surface tone. *Default: yes.*
10. **Uppercase mono labels.** Use them for tab strips, panel headers, table headers, and small metadata; keep command
    buttons, menu items, and form labels in sentence case for scanning. *Default: yes.*
11. **Corners and elevation.** Square corners (0–2 px) and no shadows, except one overlay shadow (or a border) for menus,
    popovers, and dialogs so they separate from the content below. *Default: yes.*
12. **Contrast.** Adjust colours that fail WCAG AA (give the ratios), split decorative and interactive borders, use a
    deep brand colour that fails on dark only as a fill. *Default: yes.*
13. **Red.** Red only for errors, destructive actions, and failures; amber warnings, green success, blue links,
    information, focus, and selection. *Default: yes.*
14. **Data colours.** Keep the app's chart and map palettes (they encode meaning and were validated), or derive new ones
    from the brand? *Default: keep them; re-check them at 3:1 against the new chart surfaces.*
15. **Agent rule.** Add a rule to `AGENTS.md` (or equivalent) that UI changes follow the recorded spec. *Default: yes.*

## Questions that come up later

- **Behaviour found during the restyle.** A control that does nothing, a state that is never shown, a label that is
  wrong: report it and ask; do not fix it inside the restyle.
- **Third-party limits.** A library cannot take the reference's treatment (a fixed tab shape, canvas text that cannot use
  the web font, map labels from glyph files). Ask whether to accept the limit, override the library's CSS (and own the
  maintenance), or replace the component (a package decision).
- **Tagging.** A restyle merge is not a release; ask whether to tag at all.

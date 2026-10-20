# app-ui-alignment

Restyles a web application (shell, toolbars, docked panels, forms, data grids, charts, maps, and dialogs) so that it
follows a reference UI and a brand's palette, typography, and grid language. It works in eight phases from an audit of
the app's styling through the owner's decisions, a recorded spec, tested design tokens, and third-party theming to
browser verification in every theme. It keeps the app's identity and behaviour, settles every conflict with the app's
own design rules with the owner, and keeps the app's checks passing. For MkDocs documentation sites, use
[`wiki-ui-alignment`](wiki-ui-alignment.md).

## At a glance

| Field | Value |
| --- | --- |
| Skill | `app-ui-alignment` |
| Invoke | `/app-ui-alignment [context]`, or describe the task in your own words |
| Arguments | None declared; text after the command is passed on as context |
| Produces | A restyled app in reviewable commits, a decision record with the owner's choices, a contrast test for every theme, before-and-after screenshots, and a report of what changed and every deviation |
| Source | [`skills/app-ui-alignment`](https://github.com/Energy-Atlas/dev-skills/tree/main/skills/app-ui-alignment) |

## Arguments

The front matter declares no `argument-hint`: anything typed after the command reaches the skill as context, and the
skill collects the rest of its inputs (the reference UI, the palette source, the app's own design rules, and its
working rules) by reading the project and asking.

| Argument | Required | Default | Meaning |
| --- | --- | --- | --- |
| `context` | No | — | Free text: the app to restyle, the reference UI or sister site, the palette source, and any constraints |

```text
/app-ui-alignment
/app-ui-alignment align this React workbench with the EnergyAtlas dev-skills site
```

## When to use it

- Someone asks to align, restyle, or re-theme a web app, dashboard, or product demo to a design spec, a reference
  screenshot, or a sister site, such as a documentation site styled with `wiki-ui-alignment`.
- A request to apply a design system or a brand palette to an application.
- Later UI fixes on such an app, which must stay consistent with its recorded spec.

## What it does

1. **Read the app:** the stack and styling method, the token system and how themes switch, the third-party surfaces
   (docking, grids, charts, maps) and which of them draw to a canvas, fonts, and the app's checks.
2. **Audit:** a scripted inventory of colour literals, font sizes and families, borders, radii, shadows, and font-host
   URLs; baseline screenshots in every theme; a table translating each reference element into its app equivalent,
   with every conflict with the app's own design rules marked.
3. **Settle the decisions:** the owner rules on each conflict (or picks between variants built side by side), then the
   remaining intake questions, each with a recommendation.
4. **Record the spec:** where the project records design decisions, facts kept apart from decisions, and a rule in the
   agent instructions that UI changes follow it.
5. **Tokens and contrast:** one semantic token set for every theme, split decorative and interactive borders, a
   separate data palette, and a contrast test in the app's own test runner.
6. **Implement in layers:** fonts, tokens, shell chrome, controls, panels and docking, data surfaces, overlays and
   states, and reduced motion, each a reviewable commit.
7. **Verify in a browser:** the app's checks, every theme at two desktop sizes, fonts from the app's own origin, theme
   switches that restyle canvases without a reload, no first-frame flash, visible focus, and accessibility checks.
8. **Hand back and ship:** the alignment record with evidence; push, merge, and tag only with the owner's yes for each.

## Files

| File | Contents |
| --- | --- |
| [`SKILL.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/SKILL.md) | The inputs, hard rules, and the eight phases |
| [`references/intake-questions.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/references/intake-questions.md) | The decision questions, precedence first, with recommended defaults |
| [`references/spec-decisions-template.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/references/spec-decisions-template.md) | The template for the decision record or the spec's section of decisions |
| [`references/translation.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/references/translation.md) | Reference elements and their app equivalents, with defaults for either precedence |
| [`references/token-recipes.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/references/token-recipes.md) | Token layers, runtime themes, the contrast test, and the EnergyAtlas family palette |
| [`references/third-party-theming.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/references/third-party-theming.md) | Docking layouts, data grids, charts, maps, diagrams, component libraries, and editors |
| [`references/verification.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/references/verification.md) | The checks, browser snippets, and a screenshot matrix |
| [`references/pitfalls.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/references/pitfalls.md) | Failures met in practice and their fixes |
| [`scripts/style_audit.py`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/scripts/style_audit.py) | The styling inventory |
| [`scripts/contrast.py`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/app-ui-alignment/scripts/contrast.py) | Contrast of token pairs in every theme, with suggested replacements |

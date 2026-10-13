# wiki-ui-alignment

Restyles an MkDocs (Material for MkDocs) documentation site so that it follows a reference UI and a brand's palette,
typography, and grid language, in eight phases from intake questions through a recorded design spec, implementation,
and browser verification to the merge. It keeps the site's identity, never hand-edits generated pages, and keeps
`mkdocs build --strict` passing. This site was styled with it.

## At a glance

| Field | Value |
| --- | --- |
| Skill | `wiki-ui-alignment` |
| Invoke | `/wiki-ui-alignment [context]`, or describe the task in your own words |
| Arguments | None declared; text after the command is passed on as context |
| Produces | A restyled MkDocs site, a design spec with the owner's decisions kept outside the published pages, self-hosted fonts, and a report of what changed and every deviation from the spec |
| Source | [`skills/wiki-ui-alignment`](https://github.com/Energy-Atlas/dev-skills/tree/main/skills/wiki-ui-alignment) |

## Arguments

The front matter declares no `argument-hint`: anything typed after the command reaches the skill as context, and the
skill collects the rest of its inputs (the reference UI, the palette source, a design spec, the site's own rules) by
asking.

| Argument | Required | Default | Meaning |
| --- | --- | --- | --- |
| `context` | No | — | Free text: the site to restyle, the reference UI or sister site, the palette source, and any constraints |

```text
/wiki-ui-alignment
/wiki-ui-alignment restyle this MkDocs site in the style of the BEMGen documentation site
```

## When to use it

- Someone hands over a UI design spec, a reference screenshot, or a sister site whose look an MkDocs wiki or
  documentation site should adopt.
- A request to "align the UI", "restyle the docs", "make the wiki look like X", or apply a design system to MkDocs.
- Later UI fixes on such a site, which must stay consistent with its recorded spec.

## What it does

1. **Read the site:** `mkdocs.yml`, the pinned MkDocs and Material versions and their templates, the hand-written
   pages that will change, and a local server to drive in a browser.
2. **Settle the decisions:** computes the palette's contrast, then asks the owner the intake questions the inputs leave
   open, each with a recommendation.
3. **Record the spec:** saves it in the repository outside the published pages, opened by a section of decisions that
   wins over the rest, and adds a rule to the agent instructions that UI changes follow it.
4. **Tokens and contrast:** one set of tokens for the light and the dark scheme, split decorative and interactive
   borders, and text that meets WCAG AA on every surface.
5. **Implement:** self-hosted fonts, the framed page, chrome, content styles, numbered section strips, shared-border
   grids of clickable cells, a restrained hero, instant navigation, and reduced motion. Optionally, when the owner
   wants them, icon cards: an icon above each cell's title and, on hover, a faint oversized icon backdrop (icons can
   come from the [`editorial-icons`](editorial-icons.md) skill).
6. **Build:** `mkdocs build --strict` after every step that changes the configuration or templates.
7. **Verify in a browser:** light and dark, desktop and phone, fonts from the site's own origin only, no horizontal
   overflow, one left edge for all text, clickable cells, and page changes without reloads.
8. **Hand back and ship:** reviewable commits; push, merge, and tag only with the owner's yes for each.

## Files

| File | Contents |
| --- | --- |
| [`SKILL.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/wiki-ui-alignment/SKILL.md) | The inputs, hard rules, and the eight phases |
| [`references/intake-questions.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/wiki-ui-alignment/references/intake-questions.md) | The decision questions, with recommended defaults (including whether to use icon cards) |
| [`references/spec-decisions-template.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/wiki-ui-alignment/references/spec-decisions-template.md) | The template for the spec's section of decisions |
| [`references/material-recipes.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/wiki-ui-alignment/references/material-recipes.md) | Configuration, the template override, CSS recipes (including the optional icon cards), and Markdown markup |
| [`references/verification.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/wiki-ui-alignment/references/verification.md) | The contrast script, the font vendoring script, and the browser checks |
| [`references/pitfalls.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/wiki-ui-alignment/references/pitfalls.md) | Failures met in practice and their fixes |

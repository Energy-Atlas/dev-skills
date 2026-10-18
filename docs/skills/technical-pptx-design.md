# technical-pptx-design

Designs an editable PowerPoint (`.pptx`) deck for a technical research presentation (models, data analysis, maps,
charts, tables, code, and limited mathematical notation) in a restrained academic style centred on the evidence. It handles
layout, typography, colour, and the treatment of every figure, and checks the file by rendering every slide and running
an automated audit. It never changes research claims, values, units, equations, code, or sources: issues it finds go into its
report.

## At a glance

| Field | Value |
| --- | --- |
| Skill | `technical-pptx-design` |
| Invoke | `/technical-pptx-design [font family]`, or describe the task in your own words |
| Arguments | An optional font family; Calibri by default |
| Produces | An editable `.pptx` and a short report: the style sheet, the layout of each slide, every element that is not editable and why, content issues found, and slides to split or merge |
| Source | [`skills/technical-pptx-design`](https://github.com/Energy-Atlas/dev-skills/tree/main/skills/technical-pptx-design) |

## Arguments

The skill takes one optional argument, the deck's font family; it also picks the family up from the request ("set it in
Aptos").

| Argument | Required | Default | Meaning |
| --- | --- | --- | --- |
| `font family` | No | Calibri | The one family for the whole deck, set as the theme's heading and body font so that titles, body text, charts, tables, and captions inherit it. Used as named, even if it is not a sans-serif. |

```text
/technical-pptx-design
/technical-pptx-design Arial
```

## When to use it

- Building, laying out, restyling, or cleaning up slides for a research talk, a thesis defence, a conference, a
  seminar, or a lab meeting.
- Starting from an outline, speaker notes, figures, data, code, or an existing deck.
- Showing code: a listing with marked lines, two versions compared git-diff style, or code from two sources side by
  side.
- Wanting a deck that does not look AI-generated: no card grids, KPI tiles, gradients, or decorative icons.

## What it does

1. **Inventory:** lists each slide's evidence and message, assigns one of eight layouts, and flags gaps such as
   low-resolution images, missing units, uncited figures, and slides that try to show too much.
2. **Design system:** defines the font family, grid and margins, type scale, neutral background, one accent colour,
   one colour per variable across the deck, and the caption and citation styles, and writes them down.
3. **Master:** keeps only the layouts the deck uses, with no logos, footers, or furniture repeated on every slide.
4. **Compose:** builds each slide from its layout, following rules for charts, maps, modelling diagrams, equations,
   code, tables, imagery, and citations. Code goes in styled blocks with a grey backdrop, line numbers, syntax
   highlighting, and a monospace font chosen by availability, whatever the deck's family.
5. **Verify:** renders every slide to an image and looks at it, runs the automated audit, and works through the
   delivery checklist.
6. **Deliver:** the `.pptx` and the report.

## Files

| File | Contents |
| --- | --- |
| [`SKILL.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/technical-pptx-design/SKILL.md) | The scope, inputs, workflow, style, and the rules for each kind of element |
| [`references/layouts.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/technical-pptx-design/references/layouts.md) | The grid and the eight layouts, with geometry for a 16:9 slide |
| [`references/qa-checklist.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/technical-pptx-design/references/qa-checklist.md) | Rendering every slide, checking the font family, the automated audit, and the delivery checklist |
| [`scripts/pptx_helpers.py`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/technical-pptx-design/scripts/pptx_helpers.py) | `python-pptx` helpers: a 16:9 starting deck, the theme font, SVG pictures, and removing unused layouts |
| [`scripts/code_blocks.py`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/technical-pptx-design/scripts/code_blocks.py) | Code blocks as native tables: syntax highlighting, line numbers, yellow and blue line marks, git-diff comparisons in green and red, unified or side by side, and the monospace font choice |
| [`scripts/audit_pptx.py`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/technical-pptx-design/scripts/audit_pptx.py) | The automated audit: shapes outside the slide, overlaps, small text, stray fonts, low-resolution images, empty placeholders, animations, and transitions |

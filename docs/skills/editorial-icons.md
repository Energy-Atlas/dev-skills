# editorial-icons

Designs and generates a coherent family of hand-drawn, editorial SVG icons: ink strokes with a slight organic wobble and
tapered ends, minimal detail, and one accent mark per icon, rendered by a seeded script in a regular and a bold weight
with colour groups a site can theme. The icon definitions are the source; it never hand-edits a rendered SVG, and it
never ships the draw plugin's scribble sketches.

## At a glance

| Field | Value |
| --- | --- |
| Skill | `editorial-icons` |
| Invoke | `/editorial-icons [context]`, or describe the task in your own words |
| Arguments | None declared; text after the command is passed on as context |
| Produces | An icon-definition module, the rendered SVGs in every weight (`<name>.svg`, `<name>-bold.svg`), a preview page, and the site integration with CSS colour coding |
| Source | [`skills/editorial-icons`](https://github.com/Energy-Atlas/dev-skills/tree/main/skills/editorial-icons) |

## Arguments

The front matter declares no `argument-hint`: anything typed after the command reaches the skill as context, and the
skill settles the rest (subjects, display sizes, colours, destinations) by inspecting the project and asking.

| Argument | Required | Default | Meaning |
| --- | --- | --- | --- |
| `context` | No | — | Free text: the icons to draw and what each stands for, where they will appear, and the style or palette to follow |

```text
/editorial-icons
/editorial-icons hand-drawn icons for the eight sections of our docs sidebar, accent in the theme blue
```

## When to use it

- A request for hand-drawn, sketch-style, editorial, or Claude-illustration-style icons.
- Replacing a site's or app's navigation, section, or feature icons with a bespoke family.
- Needing bold and regular variants of the same icons for small and large sizes.

## What it does

1. **Prepare the dependencies:** finds the custom-icons skill and the draw plugin, installs whichever is missing at its
   latest version, and reports the validator and sketch renderer to use.
2. **Settle the contract:** the subjects and their metaphors, every display size, the ink and accent colours, and where
   the module and the icons live.
3. **Sketch (optional):** compares compositions with the draw renderer, then discards the sketches.
4. **Pilot:** authors one icon with the ink pen, renders its preview at large and small sizes on light and dark grounds,
   and has the owner approve the style.
5. **The set:** draws the rest in the pilot's grammar, renders every weight, and validates the files together on one
   canvas.
6. **Integrate:** includes the icons inline, colours the ink with the text colour and the accent with the theme's accent,
   picks the weight by size, and optionally adds icon cards with a hover backdrop.
7. **Iterate and deliver:** redraws on the owner's feedback, then delivers the module, the icons, and a note in the
   project's design spec.

## Example

The worked example in the skill: the eight subspace icons of the EnergyAtlas Wiki, as delivered (charcoal ink, accent
in the wiki's blue), regular at 40 px and bold at 24 px. On the wiki the ink follows the theme's text colour.

<div class="ea-icon-sample" markdown>

<div class="ea-icon-sample-row" markdown>

<span class="ea-icon-sample-label">Regular, 40 px</span>
![Quick Start](../assets/examples/editorial-icons/quick-start.svg){ width="40" height="40" }
![Workflows](../assets/examples/editorial-icons/workflows.svg){ width="40" height="40" }
![Architecture](../assets/examples/editorial-icons/architecture.svg){ width="40" height="40" }
![Python](../assets/examples/editorial-icons/python.svg){ width="40" height="40" }
![Web API](../assets/examples/editorial-icons/web-api.svg){ width="40" height="40" }
![Library](../assets/examples/editorial-icons/library.svg){ width="40" height="40" }
![User stories](../assets/examples/editorial-icons/user-stories.svg){ width="40" height="40" }
![Wiki guide](../assets/examples/editorial-icons/wiki-guide.svg){ width="40" height="40" }

</div>

<div class="ea-icon-sample-row" markdown>

<span class="ea-icon-sample-label">Bold, 24 px</span>
![Quick Start](../assets/examples/editorial-icons/quick-start-bold.svg){ width="24" height="24" }
![Workflows](../assets/examples/editorial-icons/workflows-bold.svg){ width="24" height="24" }
![Architecture](../assets/examples/editorial-icons/architecture-bold.svg){ width="24" height="24" }
![Python](../assets/examples/editorial-icons/python-bold.svg){ width="24" height="24" }
![Web API](../assets/examples/editorial-icons/web-api-bold.svg){ width="24" height="24" }
![Library](../assets/examples/editorial-icons/library-bold.svg){ width="24" height="24" }
![User stories](../assets/examples/editorial-icons/user-stories-bold.svg){ width="24" height="24" }
![Wiki guide](../assets/examples/editorial-icons/wiki-guide-bold.svg){ width="24" height="24" }

</div>

</div>

## Files

| File | Contents |
| --- | --- |
| [`SKILL.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/SKILL.md) | The hard rules and the workflow |
| [`scripts/ink_icons.py`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/scripts/ink_icons.py) | The seeded ink-stroke engine, the `Pen`, and the command that renders a set and its preview |
| [`scripts/prepare_dependencies.py`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/scripts/prepare_dependencies.py) | Finds or installs custom-icons and the draw plugin and reports their paths |
| [`references/style.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/references/style.md) | The editorial style, the colour roles, and what to avoid |
| [`references/authoring.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/references/authoring.md) | The grid, the `Pen` API, drawing recipes, and metaphors that worked or misread |
| [`references/weights.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/references/weights.md) | Choosing stroke weights by display size |
| [`references/integration.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/references/integration.md) | Inline inclusion, CSS colour coding, MkDocs themes and hooks, cards with a hover backdrop |
| [`references/pitfalls.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/references/pitfalls.md) | Failures met in practice and their fixes |
| [`references/icon-module-template.py`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/editorial-icons/references/icon-module-template.py) | A starting icon module |
| [`references/examples/energyatlas-subspaces/`](https://github.com/Energy-Atlas/dev-skills/tree/main/skills/editorial-icons/references/examples/energyatlas-subspaces) | A worked example: the EnergyAtlas Wiki's eight subspace icons, their module, rendered SVGs, and the feedback rounds |

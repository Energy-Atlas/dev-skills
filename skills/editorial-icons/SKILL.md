---
name: editorial-icons
description: Design and generate a coherent family of hand-drawn, editorial SVG icons - ink strokes with a slight organic wobble and tapered ends, minimal detail, generous negative space, and one accent mark per icon - rendered by a seeded script in two scale-dependent weights (regular for large display, bold for small sizes) with .ink and .accent groups so a site can colour them with its theme. Use when someone asks for hand-drawn, sketch-style, editorial, or Claude-illustration-style icons; wants to replace a site's or app's navigation, section, or feature icons with a bespoke family; or needs bold and regular variants of the same icons for small and large sizes. Builds on the custom-icons skill (asset contract and validation) and the draw plugin (optional composition sketches), and installs them when they are missing.
---

# Editorial icons

Draw a family of icons as hand-inked line art: a few centrelines per icon, rendered by `scripts/ink_icons.py` into
filled paths that wobble and taper like a pen line, with one accent mark each. The script is seeded, so the same
definitions always produce the same files; the definitions, not the SVGs, are the source.

The method was worked out on the EnergyAtlas Wiki's eight subspace icons (`references/examples/energyatlas-subspaces/`),
shown bold in the sidebar dropdown and regular on the Welcome page's cards and their hover backdrops.

## Hard rules

1. **Definitions are the source.** Never hand-edit a rendered SVG: change the icon module and render again. Version the
   module next to the project's design files, outside the published pages.
2. **Pilot first.** For three or more icons, render one representative icon, show it to the owner at large and small
   sizes, and get approval of its style before drawing the rest.
3. **Two colour roles only.** Ink in `<g class="ink">`, accent in `<g class="accent">`; one accent mark per icon (a
   brand logo that is two-tone by nature may give a whole half to the accent). No gradients, shadows, textures, or
   scribble fills in final assets.
4. **Scale decides the weight.** Every icon ships in every weight; each place that shows icons uses the weight whose
   stroke is at least about 1.5 px at that size (`references/weights.md`).
5. **Validate every file** with the custom-icons validator, the set together with `--require-matching-canvas`, and look at
   the preview on light and dark grounds before delivering.
6. **The draw plugin sketches; it never ships.** Its scribble fills, grain, and fixed palette are a different style.

## Workflow

### 0. Prepare the dependencies

```bash
python "<skill-dir>/scripts/prepare_dependencies.py" --json
```

It finds the custom-icons skill and the draw plugin, installs whichever is missing at its latest version (custom-icons
with the skills CLI; draw with the Claude Code CLI, or as a cached clone of its repository when that CLI is not on
PATH), and prints the paths to use: `custom-icons.validator` and `draw.renderer`. custom-icons is required; draw is
optional. Read custom-icons' `SKILL.md` for its asset-contract and validation steps, which this workflow follows.

### 1. Settle the contract

Inspect the project first: where icons appear, at which sizes, and on which themes. Then settle, asking the owner what
the project does not answer:

- **Subjects**: one line per icon on what it stands for, and the metaphor to draw (`references/authoring.md` has
  metaphors that worked and ones that misread).
- **Display sizes**: every place and size the icons will appear; they decide the weights (`references/weights.md`).
- **Colours**: the ink colour of the standalone files and the accent; on a themed site, whether the ink follows the
  text colour and the accent follows the theme's accent (`references/style.md`).
- **Destinations**: where the icon module, the rendered SVGs, and the preview live; how the site will include them
  (`references/integration.md`).

### 2. Sketch (optional)

When a subject's composition is unclear, sketch candidates with the draw renderer: write a draft SVG in its normalized
`viewBox="0 0 1 1"` format (see the draw plugin's `SKILL.md`) and render it with
`python "<draw.renderer>" draft.svg sketch.svg`. Compare metaphors quickly; then discard the sketches.

### 3. Author and render the pilot

Copy `references/icon-module-template.py` to the project's design folder, define the pilot icon with the `Pen`
(`references/authoring.md`), and render:

```bash
python "<skill-dir>/scripts/ink_icons.py" <module.py> --out <workspace> <pilot-name>
```

Open `<workspace>/preview.html` (inspection size, then 120, 48, 24, and 18 px on light, paper, and dark grounds) and
iterate until it meets `references/style.md`. Show the owner; adjust stroke weight, wobble, or composition on their
answer.

### 4. Draw and render the set

Add the remaining icons with the pilot's grammar: the same canvas, padding, stroke weights, ring overlap, and accent
size. Render the whole set and validate:

```bash
python "<skill-dir>/scripts/ink_icons.py" <module.py> --out <workspace>
python "<custom-icons.validator>" <workspace>/*.svg --require-matching-canvas
```

Compare the family side by side in the preview: equal optical size and density, every subject recognisable at the
smallest size, no stray marks, negative spaces open in the bold weight. Fix outliers by redrawing, not by scaling.

### 5. Integrate

Copy the validated SVGs to their destination and include them inline, so CSS can colour the groups
(`references/integration.md`): ink `currentColor`, accent the theme's accent token, the weight chosen per size.
Optionally show them on overview cards with a faint oversized hover backdrop; for MkDocs sites that recipe is in the
wiki-ui-alignment skill. Verify in a browser, in every theme and at every size the icons appear.

### 6. Iterate on feedback and deliver

Owners respond to drawings more than to descriptions: expect rounds such as "reads like a stick figure", "too thin in
the menu", "make it look like the language's logo". `references/pitfalls.md` lists the ones met so far and their fixes.
Deliver the icon module, the rendered SVGs, and a note in the project's design spec on the style, subjects, weights, and
colours; report the validation result and anything deliberately different from the request.

## References

- `references/style.md`: the editorial style, the colour roles, and what to avoid.
- `references/authoring.md`: the grid, the `Pen` API, drawing recipes, and metaphors.
- `references/weights.md`: choosing stroke weights by display size.
- `references/integration.md`: inline inclusion, CSS colour coding, MkDocs themes and hooks, cards and backdrops.
- `references/pitfalls.md`: failures met in practice and their fixes.
- `references/icon-module-template.py`: a starting icon module.
- `references/examples/energyatlas-subspaces/`: a complete worked example with its rendered SVGs.

# Pitfalls

Failures met while drawing the EnergyAtlas Wiki's subspace icons, with their causes and fixes.

## Drawing

- **Short strokes turn into commas or tadpoles.** A fixed taper ramp eats most of a short stroke. The engine limits the
  ramp to a fifth of the stroke; keep end tapers at 0.7 or more for marks shorter than about 4 units.
- **A line touching a ring reads as a hook, a head on a stick, or a chain link.** Leave a visible gap between marks that
  are separate ideas (centreline distance about 2 units or more).
- **A wandering line reads as a worm.** Fewer, wider turns; one S at most.
- **A metaphor reads as something else.** "Stick figure kicking a ball", "a 2", "a hook": change the metaphor, not the
  details. Prefer the symbol the audience already knows (a language's logo over its namesake animal).
- **One icon is denser than the rest.** Three outlined spines and a shelf outweighed every other icon: remove marks and
  let one filled accent carry the weight.
- **Reordering marks changes the wobble.** Every mark draws from the icon's seeded stream; reorder only on purpose.

## Weight and colour

- **Too thin in menus.** A regular line at 20-26 px renders around 1 px. Render a bold weight from the same drawing and
  use it at small sizes (`references/weights.md`); do not scale the regular file.
- **Charcoal ink disappears in dark mode.** Include the icons inline and set the ink to `currentColor`.
- **The accent clashes with the site.** A colour from the brief (terracotta) may not belong to the site's palette: the
  owner may want the theme's accent; keep the accent a CSS-overridable group so this is a one-line change.

## Tools

- **The draw plugin's style leaks in.** Its scribble fills, grain filter, and fixed 21-colour palette are its own style;
  use it only for composition sketches.
- **The Claude Code CLI is not on PATH** (the desktop app). `prepare_dependencies.py` then clones the draw plugin's
  repository into a cache folder and uses its `draw.py` directly.
- **Previews from a browser pane time out while the pane is hidden.** Bring the tab to the front before a screenshot, or
  inspect with page text and measurements.
- **`mkdocs serve` keeps showing the old icon.** It does not reload files included by templates: restart it.
- **Copying SVGs by hand drifts from the module.** Render, validate, then copy every file; a test that renders the module
  and compares it with the committed SVGs catches drift.

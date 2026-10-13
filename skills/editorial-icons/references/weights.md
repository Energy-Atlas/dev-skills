# Weights and display size

A hand-drawn line that looks right at 40 px is too thin at 20 px: its stroke falls below what the eye reads as a line.
So every icon ships in more than one weight, all rendered from the same strokes and seeds, and each place that shows
icons picks the weight that suits its size.

## The rule

The rendered stroke, in pixels, is

```text
stroke_px = width_units * display_px / 24
```

Aim for a stroke of about **1.5 px or more** at the display size, which gives the minimum width in grid units:

```text
width_units >= 36 / display_px
```

| Display size | Minimum width | Weight |
| --- | --- | --- |
| 40 px and up (cards, heroes, inspection) | 0.9 | regular (1.3): 2.2 px at 40 px |
| 28-36 px | 1.0-1.3 | regular |
| 20-26 px (menus, sidebars, tabs) | 1.4-1.8 | bold (1.85): 1.5-2.0 px |
| 16-18 px (inline with text) | 2.0-2.25 | add a heavier weight (2.2) or simplify the drawing |

Bold is a different weight of the same drawing, not a scaled copy: scaling the regular SVG up enlarges the whole icon,
while the bold weight keeps its size and thickens only the line.

## Defaults

- `WEIGHTS = {"regular": 1.3, "bold": 1.85}`: `<name>.svg` and `<name>-bold.svg`.
- Add a weight by adding an entry, for example `"heavy": 2.2`, written as `<name>-heavy.svg`.
- A backdrop copy (a faint, oversized icon behind a card) uses the regular weight: at several hundred pixels any weight
  reads, and the lighter line keeps it quiet.

## Check

- Look at `preview.html` at 24 and 18 px: a weight is too light when its lines break up or turn grey, too heavy when
  negative spaces close (the inside of a ring, a book, a box).
- In the bold weight, keep at least about 2 units between centrelines that must stay apart; move marks apart rather than
  thinning one weight only.

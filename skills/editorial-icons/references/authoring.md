# Authoring icons

An icon is a function that draws with a `Pen` on a 24 x 24 grid (y points down). The module that holds the functions is
the source of the set; `scripts/ink_icons.py` renders it.

## The module

```python
from ink_icons import Pen, arc_points, rotate, rounded_polyline

TITLE = "My site icons"                      # preview title (optional)
INK = "#3b3631"                              # colours written into the files (optional)
ACCENT = "#125dae"
WEIGHTS = {"regular": 1.3, "bold": 1.85}     # first = <name>.svg, others = <name>-<weight>.svg (optional)


def search(pen: Pen) -> None:
    """A magnifier: an open ring and a handle, the lens glint in the accent."""
    pen.stroke(arc_points(10.5, 10.5, 6.0, 200, 548), weight=0.95)
    pen.stroke([(15.0, 15.0), (17.6, 17.4), (20.4, 20.2)], taper=(0.85, 0.7))
    pen.dot(9.2, 9.2, 1.0, accent=True)


ICONS = {"search": (search, 31)}             # name -> (function, seed)
```

Start from `icon-module-template.py`. Render with `python ink_icons.py module.py --out folder [name ...]`.

## The pen

| Call | Draws | Notes |
| --- | --- | --- |
| `pen.stroke(points, weight=1.0, taper=(0.7, 0.62), closed=False, overshoot=0.0, spline=True, accent=False)` | an ink line through the points | `weight` scales the set's width; `taper` is the (start, end) width fraction; `closed=True, overshoot=0.8-0.9` for a hand-closed shape; `spline=False` keeps sharp corners |
| `pen.dot(cx, cy, r, accent=False)` | a slightly irregular filled dot | nodes, eyes, destinations; r 0.9-2.2 |
| `pen.blob(points, accent=False)` | a filled organic shape through the points | needles, ribbons, filled blocks |
| `pen.rounded_rect(x0, y0, x1, y1, r, jitter=0.12)` | returns points | pass to `stroke(..., closed=True)` or `blob` |

Point helpers: `arc_points(cx, cy, r, start, end, n=None)` (degrees, clockwise on screen; a span past 360 makes an
overlapping ring), `rounded_polyline(points, r=2.0)` (a polyline with rounded corners, for logos and boxes), and
`rotate(points, origin, degrees)`.

Every mark draws from the icon's seeded random stream: changing the order of calls, or adding a call, changes the wobble
of the marks after it. Choose any seed per icon; change it only to get a different hand.

## Grid and spacing

- Canvas 24 x 24, optical box about 2.5-21.5. Points are centreline points: a stroke's outline extends half its width
  beyond them (0.65 units regular, 0.93 bold), so keep centrelines at least 3 units from the canvas edge.
- Leave a gap between marks that should read as separate: centreline distance at least about 2 units.
- Ring radius 2.0-2.3 for nodes; 6-8.5 for a ring that is the whole icon. Dots 1.6-2.2 for accents, 0.9-1.1 for eyes.

## Recipes

| Subject part | Recipe |
| --- | --- |
| Open ring (node, head) | `pen.stroke(arc_points(cx, cy, r, 200, 548), weight=0.95)`: a loop that overlaps itself by about 12 degrees |
| Curve | 3-5 points; let the spline smooth it; keep turns few and wide |
| Arrowhead | a separate 3-point stroke with `spline=False`, its tip a little past the curve's end, `taper=(0.75, 0.75)` |
| Box or block | `pen.stroke(pen.rounded_rect(...), closed=True, overshoot=0.9)`; filled: `pen.blob(pen.rounded_rect(..., jitter=0.08), accent=True)` |
| Leaning object | `rotate(pen.rounded_rect(...), pivot, degrees)` |
| Brackets, chevrons | 5-point strokes with the apex in the middle; the spline rounds the apex softly |
| Logo built from boxes | `rounded_polyline` with r = 2 through the logo's corner points, one stroke per continuous outline |
| Needle, ribbon | `pen.blob` through 4-5 points |

## Metaphors

What worked, and what misread, on the EnergyAtlas Wiki:

| Subject | Worked | Misread |
| --- | --- | --- |
| Workflows | node, curved arrow, node (accent) | ring and wandering line ("worm"); ring on a stick ("stick figure kicking a ball"); stations on a line ("chain") |
| Quick start | compass ring with an accent needle | - |
| Architecture | three blocks on branching lines, one filled | - |
| Python | the language's logo, two snakes from rounded strokes, one in the accent | a snake animal ("a 2", "a hook") |
| Web API | `< / >` with an accent slash | - |
| Library | two upright books, one filled, a third leaning | three outlined spines on a shelf (too dense) |
| User stories | head-and-shoulders figure with an accent speech bubble | - |
| Wiki / guide | open book with an accent ribbon | - |

Prefer the metaphor the audience already knows for that word: a technology's own logo, the usual symbol for an action.

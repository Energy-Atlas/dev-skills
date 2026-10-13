"""<Project> icons: an editorial, hand-drawn family (rendered by the editorial-icons skill).

Render (adjust the paths):

    python <skill-dir>/scripts/ink_icons.py <this-file> --out <workspace> [name ...]

Edit this module, never the rendered SVGs. Keep each icon's seed; reordering the marks inside an icon changes its wobble.
"""

from ink_icons import Pen, arc_points, rotate, rounded_polyline  # noqa: F401  (helpers for your icons)

TITLE = "<Project> icons"
INK = "#3b3631"                              # standalone ink; a themed site sets .ink to currentColor
ACCENT = "#c2704f"                           # standalone accent; a themed site sets .accent to its accent token
WEIGHTS = {"regular": 1.3, "bold": 1.85}     # <name>.svg, <name>-bold.svg (references/weights.md)


def example(pen: Pen) -> None:
    """Node, curved arrow, node: replace with the pilot icon."""
    pen.stroke(arc_points(5.6, 17.6, 2.3, 200, 548), weight=0.95)                 # an open ring
    pen.stroke([(5.9, 14.4), (6.6, 10.0), (9.6, 7.2), (14.6, 6.5)], taper=(0.8, 0.9))
    pen.stroke([(12.4, 4.2), (14.9, 6.5), (12.5, 8.9)], taper=(0.75, 0.75), spline=False)   # the arrowhead
    pen.dot(18.9, 6.5, 2.2, accent=True)                                           # the accent mark


ICONS = {
    "example": (example, 11),                # name -> (function, seed)
}

"""Worked example: the eight subspace icons of the EnergyAtlas Wiki.

Render them (from the skill folder):

    python scripts/ink_icons.py references/examples/energyatlas-subspaces/icons.py \
        --out references/examples/energyatlas-subspaces/svg

The wiki shows the bold weight in its sidebar (20-26 px) and the regular weight on its Welcome cards (40 px) and as
the cards' faint hover backdrop. See README.md in this folder for the story of each drawing.
"""

from ink_icons import Pen, arc_points, rotate, rounded_polyline

TITLE = "EnergyAtlas Wiki subspace icons"
INK = "#3b3631"       # warm charcoal; the site replaces it with currentColor
ACCENT = "#125dae"    # the light theme's accent blue; the site replaces it with its --ui-accent token
WEIGHTS = {"regular": 1.3, "bold": 1.85}


def quick_start(pen: Pen) -> None:
    """A compass: the ring, an accent north needle, and a drawn south needle."""
    pen.stroke(arc_points(12.0, 12.0, 8.2, -100, 268, n=24))
    c, u, v = (12.0, 12.0), (0.707, -0.707), (0.707, 0.707)
    at = lambda a, b: (c[0] + u[0] * a + v[0] * b, c[1] + u[1] * a + v[1] * b)
    pen.blob([at(4.9, 0.0), at(0.2, 1.25), at(-0.2, 0.0), at(0.2, -1.25)], accent=True)
    pen.stroke([at(0.0, 1.2), at(-4.6, 0.05), at(0.0, -1.2)], weight=0.8, taper=(0.8, 0.8), spline=False)


def workflows(pen: Pen) -> None:
    """Node, curved arrow, node: one step of a workflow leading to the next."""
    pen.stroke(arc_points(5.6, 17.6, 2.3, 200, 548), weight=0.95)
    pen.stroke([(5.9, 14.4), (6.6, 10.0), (9.6, 7.2), (14.6, 6.5)], taper=(0.8, 0.9))
    pen.stroke([(12.4, 4.2), (14.9, 6.5), (12.5, 8.9)], taper=(0.75, 0.75), spline=False)
    pen.dot(18.9, 6.5, 2.2, accent=True)


def architecture(pen: Pen) -> None:
    """Three blocks on branching lines, one of them filled in the accent."""
    pen.stroke(pen.rounded_rect(9.0, 3.4, 15.0, 8.6, 1.3), closed=True, overshoot=0.9)
    pen.stroke(pen.rounded_rect(3.4, 15.2, 9.4, 20.4, 1.3), closed=True, overshoot=0.9)
    pen.blob(pen.rounded_rect(15.1, 15.5, 20.3, 20.1, 1.4, jitter=0.08), accent=True)
    pen.stroke([(12.0, 10.0), (11.4, 12.2), (8.6, 12.9), (6.5, 13.8)])
    pen.stroke([(12.0, 10.0), (12.6, 12.2), (15.4, 12.9), (17.6, 13.9)])


def python(pen: Pen) -> None:
    """The Python logo: two interlocking snakes, the upper one in ink and the lower one in the accent."""
    pen.stroke(rounded_polyline([(12.0, 12.0), (8.0, 12.0), (8.0, 4.8), (10.0, 3.0), (14.0, 3.0), (16.0, 4.8),
                                 (16.0, 10.0)], r=2.0), taper=(0.8, 0.8))
    pen.stroke(rounded_polyline([(12.4, 9.0), (3.0, 9.0), (3.0, 17.0), (8.0, 17.0)], r=2.0), taper=(0.8, 0.8))
    pen.dot(11.0, 6.0, 0.95)
    pen.stroke(rounded_polyline([(12.0, 12.0), (16.0, 12.0), (16.0, 19.2), (14.0, 21.0), (10.0, 21.0), (8.0, 19.2),
                                 (8.0, 14.0)], r=2.0), taper=(0.8, 0.8), accent=True)
    pen.stroke(rounded_polyline([(11.6, 15.0), (21.0, 15.0), (21.0, 7.0), (16.0, 7.0)], r=2.0), taper=(0.8, 0.8),
               accent=True)
    pen.dot(13.0, 18.0, 0.95, accent=True)


def web_api(pen: Pen) -> None:
    """< / > with the slash in the accent."""
    pen.stroke([(8.4, 6.4), (5.6, 9.4), (3.4, 12.0), (5.6, 14.6), (8.4, 17.6)])
    pen.stroke([(15.6, 6.4), (18.4, 9.4), (20.6, 12.0), (18.4, 14.6), (15.6, 17.6)])
    pen.stroke([(13.7, 4.6), (12.3, 11.6), (10.5, 19.4)], accent=True)


def library(pen: Pen) -> None:
    """Two upright books, the second filled in the accent, and a third leaning against them."""
    pen.stroke(pen.rounded_rect(3.4, 4.6, 8.0, 19.8, 1.0), closed=True, overshoot=0.9)
    pen.blob(pen.rounded_rect(9.4, 7.4, 13.0, 19.6, 0.9, jitter=0.08), accent=True)
    lean = rotate(pen.rounded_rect(14.2, 6.4, 18.4, 21.2, 1.0), (14.2, 19.8), 16)
    pen.stroke(lean, closed=True, overshoot=0.9)


def user_stories(pen: Pen) -> None:
    """A figure, head and shoulders, and its story: an accent speech bubble pointing at it."""
    pen.stroke(arc_points(8.2, 11.4, 2.7, -80, 290, n=16), weight=0.95)
    pen.stroke([(2.9, 20.4), (3.6, 17.0), (8.2, 15.4), (12.8, 17.0), (13.5, 20.4)])
    bubble = [(17.6, 3.2), (20.7, 4.3), (21.0, 7.2), (18.6, 9.0), (15.7, 9.0), (14.7, 10.9), (14.8, 8.4),
              (13.8, 6.6), (14.6, 4.2)]
    pen.stroke(bubble, closed=True, overshoot=0.8, weight=0.95, accent=True)


def wiki_guide(pen: Pen) -> None:
    """An open book drawn from the spine outwards, with an accent ribbon."""
    pen.stroke([(12.0, 7.6), (8.4, 5.5), (3.5, 6.2), (3.5, 12.0), (3.6, 17.6), (8.3, 17.2), (12.0, 19.2)])
    pen.stroke([(12.0, 7.6), (15.6, 5.5), (20.5, 6.2), (20.5, 12.0), (20.4, 17.6), (15.7, 17.2), (12.0, 19.2)])
    pen.stroke([(12.0, 8.6), (12.05, 13.4), (12.0, 18.2)], weight=0.85)
    pen.blob([(15.0, 5.9), (16.8, 5.6), (16.9, 12.4), (15.95, 11.2), (15.0, 12.6)], accent=True)


ICONS = {
    "quick-start": (quick_start, 3),
    "workflows": (workflows, 11),
    "architecture": (architecture, 5),
    "python": (python, 7),
    "web-api": (web_api, 13),
    "library": (library, 17),
    "user-stories": (user_stories, 19),
    "wiki-guide": (wiki_guide, 23),
}

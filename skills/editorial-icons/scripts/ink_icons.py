"""Ink-stroke engine for editorial, hand-drawn icon families.

An icon is authored as a few centrelines on a 24x24 grid. The engine renders every centreline as an ink stroke: a
Catmull-Rom spline, displaced by a small seeded low-frequency wobble, outlined with a width that swells gently along
the stroke and tapers at loose ends, then written as a filled path. The output reads as a pen line drawn by hand, not
as a geometric stroke, and it is identical on every run because every icon has its own seed.

Each SVG keeps its ink in a `<g class="ink">` group and its accent in a `<g class="accent">` group, so a site can
recolour both with CSS (for example ink = currentColor, accent = the theme's accent).

Author icons in a module of your own (see references/authoring.md and references/examples/):

    from ink_icons import Pen, arc_points

    def workflows(pen: Pen) -> None:
        pen.stroke(arc_points(5.6, 17.6, 2.3, 200, 548), weight=0.95)      # an open ring
        pen.stroke([(5.9, 14.4), (6.6, 10.0), (9.6, 7.2), (14.6, 6.5)])     # a curve
        pen.dot(18.9, 6.5, 2.2, accent=True)                                # the accent node

    ICONS = {"workflows": (workflows, 11)}        # name -> (function, seed)
    WEIGHTS = {"regular": 1.3, "bold": 1.85}      # optional; stroke width in grid units per weight
    INK, ACCENT = "#3b3631", "#125dae"            # optional; colours written into the files

Render every weight of every icon, plus preview.html:

    python ink_icons.py path/to/icons.py --out path/to/output [name ...]

Files: <name>.svg for the first weight, <name>-<weight>.svg for the others. Standard library only (Python 3.9+).
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import random
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Point = Tuple[float, float]
Outline = List[Point]

DEFAULT_INK = "#3b3631"       # warm charcoal
DEFAULT_ACCENT = "#c2704f"    # muted terracotta; most sites swap in their own accent
DEFAULT_WEIGHTS = {"regular": 1.3, "bold": 1.85}
WOBBLE = 0.09                 # displacement amplitude of the hand wobble, grid units
STEP = 0.18                   # centreline sampling step, grid units
CANVAS = 24


# ---------------------------------------------------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------------------------------------------------

def catmull_rom(points: Sequence[Point], closed: bool = False, step: float = STEP) -> Outline:
    """Sample a Catmull-Rom spline through points at roughly `step` spacing."""
    pts = list(points)
    if closed:
        ext = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        ext = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        seg = math.dist(p1, p2)
        n = max(2, int(seg / step))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[0] if closed else pts[-1])
    return out


def arc_points(cx: float, cy: float, r: float, start_deg: float, end_deg: float, n: int | None = None) -> Outline:
    """Points on a circular arc (degrees, y down). A span past 360 degrees makes a ring that overlaps its start."""
    span = end_deg - start_deg
    n = n or max(6, int(abs(span) / 18))
    return [(cx + r * math.cos(math.radians(start_deg + span * i / n)),
             cy + r * math.sin(math.radians(start_deg + span * i / n))) for i in range(n + 1)]


def rounded_rect(x0: float, y0: float, x1: float, y1: float, r: float, rng: random.Random,
                 jitter: float = 0.12) -> Outline:
    """Points around a rounded rectangle, starting at the middle of the top edge, with slightly unsteady corners."""
    j = lambda: rng.uniform(-jitter, jitter)
    corners = [(x1 - r + j(), y0 + r + j(), -90, 0), (x1 - r + j(), y1 - r + j(), 0, 90),
               (x0 + r + j(), y1 - r + j(), 90, 180), (x0 + r + j(), y0 + r + j(), 180, 270)]
    pts = [((x0 + x1) / 2 + j(), y0 + j() * 0.5)]
    for cx, cy, a0, a1 in corners:
        pts += arc_points(cx, cy, r, a0, a1, n=3)
    return pts


def rounded_polyline(points: Sequence[Point], r: float = 2.0, n: int = 4) -> Outline:
    """A polyline whose interior corners are rounded with radius r (quadratic corner curves)."""
    out = [points[0]]
    for prev, v, nxt in zip(points, points[1:], points[2:]):
        din = (v[0] - prev[0], v[1] - prev[1])
        dout = (nxt[0] - v[0], nxt[1] - v[1])
        lin, lout = math.hypot(*din) or 1.0, math.hypot(*dout) or 1.0
        rr = min(r, lin / 2, lout / 2)
        a = (v[0] - din[0] / lin * rr, v[1] - din[1] / lin * rr)
        b = (v[0] + dout[0] / lout * rr, v[1] + dout[1] / lout * rr)
        for k in range(n + 1):
            t = k / n
            out.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * v[0] + t * t * b[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * v[1] + t * t * b[1]))
    out.append(points[-1])
    return out


def rotate(points: Iterable[Point], origin: Point, degrees: float) -> Outline:
    """Rotate points about origin (degrees, clockwise on screen)."""
    a = math.radians(degrees)
    ox, oy = origin
    return [(ox + (x - ox) * math.cos(a) - (y - oy) * math.sin(a),
             oy + (x - ox) * math.sin(a) + (y - oy) * math.cos(a)) for x, y in points]


def cumulative(pts: Sequence[Point]) -> List[float]:
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + math.dist(a, b))
    return s


def normals(pts: Sequence[Point]) -> List[Point]:
    out = []
    for i in range(len(pts)):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1.0
        out.append((-dy / length, dx / length))
    return out


class Noise:
    """Smooth 1-D noise along arc length: a sum of a few seeded sines."""

    def __init__(self, rng: random.Random, octaves: int = 3, base_wavelength: float = 7.0):
        self.terms = []
        for o in range(octaves):
            wavelength = base_wavelength / (1.9 ** o) * rng.uniform(0.8, 1.25)
            self.terms.append((2 * math.pi / wavelength, rng.uniform(0, 2 * math.pi), 1.0 / (1.6 ** o)))
        self.norm = sum(t[2] for t in self.terms)

    def __call__(self, s: float) -> float:
        return sum(a * math.sin(w * s + p) for w, p, a in self.terms) / self.norm


# ---------------------------------------------------------------------------------------------------------------------
# Ink marks
# ---------------------------------------------------------------------------------------------------------------------

def ink_stroke(points: Sequence[Point], rng: random.Random, width: float, closed: bool = False,
               taper: Tuple[float, float] = (0.7, 0.62), wobble: float = WOBBLE, overshoot: float = 0.0,
               spline: bool = True) -> Outline:
    """The closed outline of a hand-inked stroke along points.

    taper: end widths as fractions of `width` at (start, end).
    overshoot: for closed shapes, draw past the start by this many units, as a hand closing a loop does.
    spline: False keeps sharp corners at the given points (arrowheads, chevrons).
    """
    centre = catmull_rom(points, closed=closed) if spline else list(points)
    if closed:
        s = cumulative(centre)
        extra = []
        for p, d in zip(centre[1:], s[1:]):
            if d > overshoot:
                break
            extra.append(p)
        centre = centre + extra[1:]
    s = cumulative(centre)
    total = s[-1] or 1.0
    nrm = normals(centre)
    displace = Noise(rng)
    swell = Noise(rng, octaves=2, base_wavelength=9.0)

    left, right = [], []
    for p, n, d in zip(centre, nrm, s):
        off = wobble * displace(d)
        cx, cy = p[0] + n[0] * off, p[1] + n[1] * off
        w = width * (1.0 + 0.10 * swell(d))
        # Loose ends taper over up to 1.4 units, never more than a fifth of a short stroke, so short marks stay
        # lines instead of turning into commas.
        ramp = min(1.4, total * 0.2)
        if d < ramp:
            w *= taper[0] + (1 - taper[0]) * _ease(d / ramp)
        if total - d < ramp:
            w *= taper[1] + (1 - taper[1]) * _ease((total - d) / ramp)
        half = w / 2
        left.append((cx + n[0] * half, cy + n[1] * half))
        right.append((cx - n[0] * half, cy - n[1] * half))

    end_out = _unit(centre[-1][0] - centre[-2][0], centre[-1][1] - centre[-2][1])
    start_out = _unit(centre[0][0] - centre[1][0], centre[0][1] - centre[1][1])
    return left + _cap(centre[-1], left[-1], end_out) + right[::-1] + _cap(centre[0], right[0], start_out)


def ink_dot(cx: float, cy: float, r: float, rng: random.Random) -> Outline:
    """A small, slightly irregular filled dot."""
    k = 18
    phase = rng.uniform(0, 2 * math.pi)
    return [(cx + r * (1 + 0.07 * math.sin(2 * a + phase)) * math.cos(a),
             cy + r * (1 + 0.07 * math.sin(3 * a + phase)) * math.sin(a))
            for a in (2 * math.pi * i / k for i in range(k))]


def ink_blob(points: Sequence[Point], rng: random.Random, wobble: float = 0.06) -> Outline:
    """A filled organic shape through points (a closed spline with a light wobble)."""
    centre = catmull_rom(points, closed=True, step=0.25)
    s = cumulative(centre)
    nrm = normals(centre)
    noise = Noise(rng, octaves=2, base_wavelength=5.0)
    return [(p[0] + n[0] * wobble * noise(d), p[1] + n[1] * wobble * noise(d)) for p, n, d in zip(centre, nrm, s)]


def _unit(dx: float, dy: float) -> Point:
    length = math.hypot(dx, dy) or 1.0
    return dx / length, dy / length


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _cap(c: Point, a: Point, outward: Point) -> Outline:
    """A round cap from outline point a, around stroke end c, bulging in the outward direction."""
    ax, ay = a[0] - c[0], a[1] - c[1]
    r = math.hypot(ax, ay)
    if r == 0:
        return []
    start = math.atan2(ay, ax)
    sign = 1 if math.cos(start + math.pi / 2) * outward[0] + math.sin(start + math.pi / 2) * outward[1] > 0 else -1
    return [(c[0] + r * math.cos(start + sign * math.pi * k / 6), c[1] + r * math.sin(start + sign * math.pi * k / 6))
            for k in range(1, 6)]


# ---------------------------------------------------------------------------------------------------------------------
# The pen: what icon functions draw with
# ---------------------------------------------------------------------------------------------------------------------

class Pen:
    """Collects the ink and accent marks of one icon at one weight.

    `width` is the weight's stroke width in grid units; `weight=` on a stroke scales it (0.95 for rings, 0.8 for fine
    details). Draw in a fixed order: every mark draws from the icon's seeded random stream, so reordering marks
    changes the wobble of the ones after them.
    """

    def __init__(self, seed: int, width: float, wobble: float = WOBBLE):
        self.rng = random.Random(seed)
        self.width = width
        self.wobble = wobble
        self.ink: List[Outline] = []
        self.accent: List[Outline] = []

    def _put(self, outline: Outline, accent: bool) -> None:
        (self.accent if accent else self.ink).append(outline)

    def stroke(self, points: Sequence[Point], *, weight: float = 1.0, taper: Tuple[float, float] = (0.7, 0.62),
               closed: bool = False, overshoot: float = 0.0, spline: bool = True, accent: bool = False) -> None:
        """An ink line through points; closed=True with overshoot=0.8-0.9 for hand-closed shapes."""
        width = self.width if weight == 1.0 else self.width * weight
        self._put(ink_stroke(points, self.rng, width, closed=closed, taper=taper, wobble=self.wobble,
                             overshoot=overshoot, spline=spline), accent)

    def dot(self, cx: float, cy: float, r: float, *, accent: bool = False) -> None:
        """A filled dot: a node, an eye, a destination."""
        self._put(ink_dot(cx, cy, r, self.rng), accent)

    def blob(self, points: Sequence[Point], *, accent: bool = False) -> None:
        """A filled organic shape through points: a needle, a ribbon, a filled block."""
        self._put(ink_blob(points, self.rng), accent)

    def rounded_rect(self, x0: float, y0: float, x1: float, y1: float, r: float, jitter: float = 0.12) -> Outline:
        """Points around a rounded rectangle with slightly unsteady corners (to pass to stroke or blob)."""
        return rounded_rect(x0, y0, x1, y1, r, self.rng, jitter=jitter)


IconFunction = Callable[[Pen], None]


# ---------------------------------------------------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------------------------------------------------

def outline_to_d(pts: Sequence[Point]) -> str:
    """A closed smooth path through outline points (Catmull-Rom to cubic Bezier), rounded to 2 decimals."""
    n = len(pts)
    f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".") if "." in f"{v:.2f}" else f"{v:.2f}"
    d = [f"M{f(pts[0][0])} {f(pts[0][1])}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    d.append("Z")
    return "".join(d)


def thin(pts: Outline, keep_every: int = 2) -> Outline:
    """Drop every other point of long outlines to keep files small; the Bezier fit restores smoothness."""
    return pts[::keep_every] if len(pts) > 40 else pts


def build_svg(icon: IconFunction, seed: int, width: float, ink: str = DEFAULT_INK,
              accent: str = DEFAULT_ACCENT) -> str:
    """Render one icon at one stroke width to a self-contained SVG with .ink and .accent groups."""
    pen = Pen(seed, width)
    icon(pen)
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS} {CANVAS}" width="{CANVAS}" '
             f'height="{CANVAS}">']
    if pen.ink:
        lines.append(f'  <g class="ink" fill="{ink}">')
        lines += [f'    <path d="{outline_to_d(thin(o))}"/>' for o in pen.ink]
        lines.append("  </g>")
    if pen.accent:
        # Accent outlines keep every point: they are few, and their shapes (dots, small blobs) are short.
        lines.append(f'  <g class="accent" fill="{accent}">')
        lines += [f'    <path d="{outline_to_d(o)}"/>' for o in pen.accent]
        lines.append("  </g>")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def file_name(name: str, weight: str, weights: Dict[str, float]) -> str:
    """<name>.svg for the first (default) weight, <name>-<weight>.svg for the others."""
    return f"{name}.svg" if weight == next(iter(weights)) else f"{name}-{weight}.svg"


PREVIEW = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<style>
  body {{ margin: 0; font: 13px/1.4 system-ui, sans-serif; color: #3b3631; background: #fff; }}
  section {{ padding: 24px 32px; }}
  h2 {{ margin: 0 0 12px; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; opacity: .6; }}
  .dark {{ background: #000; color: #b0b0b0; }}
  .dark .ink {{ fill: #e5e5e5; }}
  .paper {{ background: #f4f7fb; }}
  .row {{ display: flex; align-items: flex-end; gap: 28px; flex-wrap: wrap; margin-bottom: 16px; }}
  figure {{ margin: 0; text-align: center; }}
  figcaption {{ margin-top: 6px; font-size: 11px; opacity: 0.7; }}
  svg {{ display: block; margin: 0 auto; }}
  .s240 svg {{ width: 240px; height: 240px; }} .s120 svg {{ width: 120px; height: 120px; }}
  .s48 svg {{ width: 48px; height: 48px; }} .s24 svg {{ width: 24px; height: 24px; }} .s18 svg {{ width: 18px; height: 18px; }}
</style></head><body>
{sections}
</body></html>
"""


def write_preview(out: Path, names: Sequence[str], weights: Dict[str, float], title: str = "Icons") -> Path:
    """preview.html: every weight at 240, 120, 48, 24 and 18 px on light, paper and dark grounds."""
    files = [file_name(n, w, weights) for w in weights for n in names]

    def row(size: int) -> str:
        cells = "".join(f'<figure class="s{size}">{(out / f).read_text(encoding="utf-8")}'
                        f'<figcaption>{f[:-4]}</figcaption></figure>' for f in files)
        return f'<div class="row">{cells}</div>'

    sections = [f'<section class="paper"><h2>inspection</h2>{row(240)}</section>']
    for ground in ("light", "paper", "dark"):
        sizes = "".join(row(s) for s in (120, 48, 24, 18))
        sections.append(f'<section class="{ground}"><h2>{ground}</h2>{sizes}</section>')
    path = out / "preview.html"
    _write(path, PREVIEW.format(title=title, sections="\n".join(sections)))
    return path


def _write(path: Path, text: str) -> None:
    """Write with LF line endings on every platform, so a set renders to identical bytes everywhere."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def load_icon_module(path: Path):
    """Import an icon-definition module from a file path (it may import ink_icons from this folder)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    spec = importlib.util.spec_from_file_location(f"icon_set_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    if not isinstance(getattr(module, "ICONS", None), dict):
        raise SystemExit(f"{path} defines no ICONS dict (name -> (function, seed))")
    return module


def render_set(module, out: Path, names: Sequence[str] | None = None) -> List[Path]:
    """Write every weight of the named icons (all when none) and preview.html; return the written SVG paths."""
    icons: Dict[str, Tuple[IconFunction, int]] = module.ICONS
    weights: Dict[str, float] = getattr(module, "WEIGHTS", DEFAULT_WEIGHTS)
    ink = getattr(module, "INK", DEFAULT_INK)
    accent = getattr(module, "ACCENT", DEFAULT_ACCENT)
    unknown = [n for n in (names or []) if n not in icons]
    if unknown:
        raise SystemExit(f"unknown icon(s): {', '.join(unknown)}; known: {', '.join(icons)}")
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name in names or list(icons):
        fn, seed = icons[name]
        for weight, width in weights.items():
            path = out / file_name(name, weight, weights)
            _write(path, build_svg(fn, seed, width, ink, accent))
            written.append(path)
    # The preview shows every icon of the set that has been rendered into this folder, in the module's order.
    shown = [n for n in icons if all((out / file_name(n, w, weights)).is_file() for w in weights)]
    write_preview(out, shown, weights, title=getattr(module, "TITLE", "Icons"))
    return written


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Render an editorial icon set from its definition module.")
    parser.add_argument("module", type=Path, help="icon-definition module (.py) defining ICONS")
    parser.add_argument("--out", type=Path, required=True, help="output folder for the SVGs and preview.html")
    parser.add_argument("names", nargs="*", help="icons to render (default: all)")
    args = parser.parse_args(argv)
    for path in render_set(load_icon_module(args.module), args.out, args.names):
        print("wrote", path)
    print("wrote", args.out / "preview.html")


if __name__ == "__main__":
    main()

"""Regression tests for skills/editorial-icons/scripts/ink_icons.py.

Run from the repository root: python -m pytest tests (standard library and pytest only).
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SKILL = Path(__file__).parents[2] / "skills" / "editorial-icons"
sys.path.insert(0, str(SKILL / "scripts"))
import ink_icons  # noqa: E402
from ink_icons import Pen, arc_points, build_svg, file_name, load_icon_module, render_set  # noqa: E402

EXAMPLE = SKILL / "references" / "examples" / "energyatlas-subspaces"
SVG_NS = "{http://www.w3.org/2000/svg}"


def ring_and_dot(pen: Pen) -> None:
    pen.stroke(arc_points(12, 12, 6, 200, 548), weight=0.95)
    pen.dot(18, 6, 1.6, accent=True)


def outline_width(svg: str) -> float:
    """Width of the drawing's bounding box, a proxy for stroke weight on a fixed ring."""
    xs = [float(x) for x in re.findall(r"[MC ](-?\d+(?:\.\d+)?) -?\d+(?:\.\d+)?", svg.split('class="accent"')[0])]
    return max(xs) - min(xs)


def test_rendering_is_deterministic():
    assert build_svg(ring_and_dot, 5, 1.3) == build_svg(ring_and_dot, 5, 1.3)
    assert build_svg(ring_and_dot, 5, 1.3) != build_svg(ring_and_dot, 6, 1.3)


def test_svg_structure_has_canvas_and_colour_groups():
    root = ET.fromstring(build_svg(ring_and_dot, 5, 1.3, ink="#111111", accent="#222222"))
    assert root.get("viewBox") == "0 0 24 24"
    assert (root.get("width"), root.get("height")) == ("24", "24")
    groups = {g.get("class"): g for g in root.iter(f"{SVG_NS}g")}
    assert groups["ink"].get("fill") == "#111111"
    assert groups["accent"].get("fill") == "#222222"
    assert all(child.tag == f"{SVG_NS}path" for g in groups.values() for child in g)
    assert not [e for e in root.iter() if e.tag.split("}")[-1] in {"script", "image", "foreignObject", "linearGradient"}]


def test_bold_weight_draws_a_heavier_line_on_the_same_drawing():
    regular = build_svg(ring_and_dot, 5, 1.3)
    bold = build_svg(ring_and_dot, 5, 1.85)
    # Same drawing, thicker line: the box grows by roughly the extra stroke width, not by a rescale of the icon.
    assert 0.2 < outline_width(bold) - outline_width(regular) < 0.9


def test_file_names_follow_the_first_weight_convention():
    weights = {"regular": 1.3, "bold": 1.85}
    assert file_name("search", "regular", weights) == "search.svg"
    assert file_name("search", "bold", weights) == "search-bold.svg"


def test_template_module_renders(tmp_path):
    module = load_icon_module(SKILL / "references" / "icon-module-template.py")
    written = render_set(module, tmp_path)
    assert sorted(p.name for p in written) == ["example-bold.svg", "example.svg"]
    assert (tmp_path / "preview.html").is_file()


def test_authoring_guide_example_renders(tmp_path):
    guide = (SKILL / "references" / "authoring.md").read_text(encoding="utf-8")
    code = guide.split("```python\n", 1)[1].split("```", 1)[0]
    module_path = tmp_path / "guide_icons.py"
    module_path.write_text(code, encoding="utf-8")
    written = render_set(load_icon_module(module_path), tmp_path / "out")
    assert {p.name for p in written} == {"search.svg", "search-bold.svg"}


def test_worked_example_matches_its_committed_svgs(tmp_path):
    module = load_icon_module(EXAMPLE / "icons.py")
    written = render_set(module, tmp_path)
    committed = sorted((EXAMPLE / "svg").glob("*.svg"))
    assert [p.name for p in committed] == sorted(p.name for p in written)
    for path in committed:
        assert (tmp_path / path.name).read_text(encoding="utf-8") == path.read_text(encoding="utf-8"), path.name


def test_unknown_icon_names_are_rejected(tmp_path):
    module = load_icon_module(EXAMPLE / "icons.py")
    with pytest.raises(SystemExit):
        render_set(module, tmp_path, ["no-such-icon"])


def test_cli_writes_files(tmp_path, capsys):
    ink_icons.main([str(EXAMPLE / "icons.py"), "--out", str(tmp_path), "workflows"])
    assert (tmp_path / "workflows.svg").is_file()
    assert (tmp_path / "workflows-bold.svg").is_file()
    assert "preview.html" in capsys.readouterr().out

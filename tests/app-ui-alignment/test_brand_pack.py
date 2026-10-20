"""The EnergyAtlas brand pack: the same files in both alignment skills and on the site, and favicons of the right sizes.

Run from the repository root: python -m pytest tests (needs pytest and Pillow; the render test needs Chrome or Edge).
"""
import filecmp
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).parents[2]
PACKS = [ROOT / "skills" / name / "references" / "brand" for name in ("app-ui-alignment", "wiki-ui-alignment")]
SITE = ROOT / "docs" / "assets" / "brand"
FILES = ["README.md", "energyatlas-mark.svg", "energyatlas-mark-knockout.svg", "favicon.svg", "favicon.ico",
         "favicon-32.png", "apple-touch-icon.png"]
SITE_FILES = ["energyatlas-mark.svg", "favicon.svg", "favicon.ico", "favicon-32.png", "apple-touch-icon.png"]
SVG = "{http://www.w3.org/2000/svg}"

sys.path.insert(0, str(ROOT / "skills" / "app-ui-alignment" / "scripts"))
import brand_assets  # noqa: E402


def test_both_skills_carry_the_same_pack():
    for name in FILES:
        assert filecmp.cmp(PACKS[0] / name, PACKS[1] / name, shallow=False), name
    assert filecmp.cmp(ROOT / "skills" / "app-ui-alignment" / "scripts" / "brand_assets.py",
                       ROOT / "skills" / "wiki-ui-alignment" / "scripts" / "brand_assets.py", shallow=False)


def test_the_site_uses_the_pack():
    for name in SITE_FILES:
        assert filecmp.cmp(PACKS[0] / name, SITE / name, shallow=False), name
    assert filecmp.cmp(PACKS[0] / "energyatlas-mark.svg", PACKS[0] / "favicon.svg", shallow=False)


@pytest.mark.parametrize("name", ["energyatlas-mark.svg", "energyatlas-mark-knockout.svg"])
def test_marks_are_clean_square_svgs(name):
    text = (PACKS[0] / name).read_text(encoding="utf-8")
    assert text.isascii(), "no non-ASCII ids or comments"
    root = ET.fromstring(text)
    assert root.get("viewBox") == "0 0 800 800"
    assert root.find(f"{SVG}title").text == "EnergyAtlas"
    stops = [stop.get("stop-color") for stop in root.iter(f"{SVG}stop")]
    assert stops == ["#003978", "#f1392a"], "the brand gradient is never recoloured"
    white = [path for path in root.iter(f"{SVG}path") if path.get("fill") == "#ffffff"]
    assert len(white) == (1 if name == "energyatlas-mark.svg" else 0), "only the default mark has a white E"
    assert not re.search(r"<(script|image|foreignObject)\b", text)


def test_raster_favicons_have_their_sizes():
    pack = PACKS[0]
    assert Image.open(pack / "favicon-32.png").size == (32, 32)
    touch = Image.open(pack / "apple-touch-icon.png").convert("RGBA")
    assert touch.size == (180, 180)
    assert touch.getpixel((0, 0))[3] == 255, "iOS shows transparency as black: the touch icon is opaque"
    assert Image.open(pack / "favicon-32.png").convert("RGBA").getpixel((0, 0))[3] == 0, "the favicon is transparent"
    assert Image.open(pack / "favicon.ico").info["sizes"] == {(16, 16), (32, 32), (48, 48)}


def browser_or_skip():
    try:
        return brand_assets.find_browser()
    except SystemExit:
        pytest.skip("no Chromium-based browser")


@pytest.mark.skipif(shutil.which("chrome") is None and not any(Path(p).exists() for p in brand_assets.CANDIDATES[:3]),
                    reason="needs Google Chrome or Chromium")
def test_brand_assets_renders_the_set(tmp_path):
    assert brand_assets.main([str(PACKS[0] / "energyatlas-mark.svg"), str(tmp_path), "--browser", browser_or_skip()]) == 0
    assert Image.open(tmp_path / "favicon-32.png").size == (32, 32)
    assert Image.open(tmp_path / "apple-touch-icon.png").size == (180, 180)
    assert Image.open(tmp_path / "favicon.ico").info["sizes"] == {(16, 16), (32, 32), (48, 48)}
    centre = Image.open(tmp_path / "favicon-32.png").convert("RGBA").getpixel((16, 16))
    assert centre[3] == 255 and centre[0] > centre[2] * 0.5, "the hexagon is drawn, not a blank square"

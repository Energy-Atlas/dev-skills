"""The site's Example tile shows copies of the skill's worked example; keep them identical."""
from pathlib import Path

ROOT = Path(__file__).parents[2]
SKILL_SVGS = ROOT / "skills" / "editorial-icons" / "references" / "examples" / "energyatlas-subspaces" / "svg"
SITE_SVGS = ROOT / "docs" / "assets" / "examples" / "editorial-icons"


def test_site_example_icons_match_the_skill_example():
    skill = {p.name: p.read_bytes() for p in SKILL_SVGS.glob("*.svg")}
    site = {p.name: p.read_bytes() for p in SITE_SVGS.glob("*.svg")}
    assert skill and site == skill


def test_site_page_shows_every_example_icon():
    page = (ROOT / "docs" / "skills" / "editorial-icons.md").read_text(encoding="utf-8")
    for name in (p.name for p in SITE_SVGS.glob("*.svg")):
        assert f"../assets/examples/editorial-icons/{name}" in page, name

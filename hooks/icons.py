"""Inline example icons into skill pages, so CSS can colour them with the site's theme.

A page writes `<span class="ea-icon" data-icon="workflows-bold"></span>`; the build replaces it with the SVG
`docs/assets/examples/<skill>/<name>.svg` of the skill the page documents (design/ui-design-spec.md, section 0.14).
The SVG keeps its `.ink` and `.accent` groups; energyatlas.css sets them to the theme's text and accent colours.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1] / "docs" / "assets" / "examples"
PLACEHOLDER = re.compile(r'<span class="ea-icon" data-icon="([a-z0-9-]+)"></span>')


@lru_cache(maxsize=None)
def icon_svg(skill: str, name: str) -> str:
    path = EXAMPLES / skill / f"{name}.svg"
    if not path.is_file():
        raise ValueError(f"{skill}: no example icon '{name}' ({path.relative_to(EXAMPLES.parents[1])})")
    return path.read_text(encoding="utf-8").strip()


def on_page_content(html, page, config, files):
    if "ea-icon" not in html:
        return html
    skill = Path(page.file.src_uri).stem
    return PLACEHOLDER.sub(
        lambda m: f'<span class="ea-icon" role="img" aria-label="{m.group(1)}">{icon_svg(skill, m.group(1))}</span>',
        html,
    )

"""Regression tests for skills/app-ui-alignment/scripts/style_audit.py.

Run from the repository root: python -m pytest tests (needs pytest).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "skills" / "app-ui-alignment" / "scripts"))
from style_audit import audit, main, shadow_kind, to_markdown  # noqa: E402

TOKENS_TS = """\
export const LIGHT = {
  bg: '#f5f6f8',
  text: '#1b1f24',
  shadow: '0 8px 24px rgb(0 0 0 / 18%)',
  border: '#d5dae1',
  fontSize: 13,
}
"""

TOKENS_CSS = """\
:root {
  --radius-sm: 0;
  --radius-pill: 999px;
  --label-tracking: 0.08em;
}
"""

PANEL_CSS = """\
/* Literal colours in comments, like #ff0000, are not findings. */
.panel {
  border: 1px solid var(--color-border);
  border-bottom: none;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  color: #333;
  font-family: 'Segoe UI', sans-serif;
  font-size: 0.8125rem;
  transition: color 150ms ease;
}
#header .title { font-size: var(--font-size-small) !important; }
.tab[data-selected] {
  box-shadow:
    inset 0 0 0 1px var(--color-accent),
    inset 0 0 0 3px var(--color-surface);
  text-transform: uppercase;
  letter-spacing: var(--label-tracking);
  border-radius: var(--radius-sm);
}
.pill { border-radius: var(--radius-pill); }
.flat { border-radius: 0; transition: none; }
@import url('https://fonts.googleapis.com/css2?family=Inter');
"""

CHART_TSX = """\
// A whole-line comment with #abcdef is skipped.
export const option = {
  animation: false,
  textStyle: { fontFamily: 'system-ui, sans-serif', fontSize: 12 },
  color: ['#2a78d6', '#eb6834'],
  itemStyle: { borderRadius: [0, 4, 4, 0] },
}
export const gridTheme = { headerFontSize: TEXT_SIZE, fontFamily: 'var(--font-sans)' }
type Ink = { fontFamily: string; fontSize: number }
const url = 'https://example.com/#section'
"""


def make_app(root: Path) -> Path:
    src = root / "src"
    (src / "appearance").mkdir(parents=True)
    (src / "appearance" / "appearances.ts").write_text(TOKENS_TS, encoding="utf-8")
    (src / "tokens.css").write_text(TOKENS_CSS, encoding="utf-8")
    (src / "panel.module.css").write_text(PANEL_CSS, encoding="utf-8")
    (src / "Chart.tsx").write_text(CHART_TSX, encoding="utf-8")
    vendored = src / "node_modules" / "lib"
    vendored.mkdir(parents=True)
    (vendored / "index.css").write_text(".x { color: #123456; }", encoding="utf-8")
    return src


def run(tmp_path, **kwargs):
    return audit([make_app(tmp_path)], tokens=["appearance/*", "tokens.css"], **kwargs)


def test_counts_literals_outside_token_files(tmp_path):
    report = run(tmp_path)
    findings = {(Path(item["file"]).name, item["line"]) for item in report["colour_literals"]}
    # color: #333, the rgba() shadow, and the chart colours; not comments, not the token files, not node_modules,
    # not the #header selector, and not the URL fragment.
    assert findings == {("panel.module.css", 6), ("panel.module.css", 7), ("Chart.tsx", 5)}
    assert report["colour_literals_in_tokens"] == 4
    assert report["files"] == 4


def test_type_scale_and_families(tmp_path):
    report = run(tmp_path)
    assert report["font_sizes"] == {"0.8125rem": 1, "var(--font-size-small) !important": 1, "12": 1, "TEXT_SIZE": 1}
    literal_lines = sorted((Path(i["file"]).name, i["line"]) for i in report["font_size_literals"])
    assert literal_lines == [("Chart.tsx", 4), ("Chart.tsx", 8), ("panel.module.css", 9)]
    assert set(report["font_families"]) == {"'Segoe UI', sans-serif", "'system-ui, sans-serif'", "'var(--font-sans)'"}


def test_borders_radii_and_shadows(tmp_path):
    report = run(tmp_path)
    # border: 1px solid counts; border-bottom: none, radii, and the token file's border key do not.
    assert sum(report["borders_by_file"].values()) == 1
    # Zero radii are not counted, arrays are read whole, and tokens resolve to their value.
    assert report["radii"] == {"6px": 1, "[0, 4, 4, 0]": 1, "var(--radius-pill) = 999px": 1}
    assert report["elevation_shadows"] == {"0 1px 2px rgba(0, 0, 0, 0.2)": 1}
    assert list(report["edge_shadows"]) == [
        "inset 0 0 0 1px var(--color-accent), inset 0 0 0 3px var(--color-surface)"]


def test_labels_motion_and_requests(tmp_path):
    report = run(tmp_path)
    assert [Path(i["file"]).name for i in report["uppercase"]] == ["panel.module.css"]
    assert report["letter_spacing"] == {"var(--label-tracking) = 0.08em": 1}
    # transition: color counts; transition: none and the chart's animation: false do not.
    assert report["motion"] == 1
    assert report["reduced_motion_queries"] == 0
    assert len(report["important"]) == 1
    assert [item["text"].split("?")[0] for item in report["external_requests"]] == [
        "https://fonts.googleapis.com/css2"]


def test_shadow_kind():
    assert shadow_kind("0 8px 24px rgb(0 0 0 / 18%)") == "elevation"
    assert shadow_kind("inset 0 -2px 0 var(--accent)") == "edge"
    assert shadow_kind("0 0 0 2px var(--focus)") == "edge"


def test_globs_match_relative_and_given_paths(tmp_path):
    src = make_app(tmp_path)
    by_relative = audit([src], exclude=["*.tsx"])
    by_given = audit([src], exclude=[f"{src.as_posix()}/*.tsx"])
    assert by_relative["files"] == by_given["files"] == 3


def test_markdown_and_cli(tmp_path, capsys):
    report = run(tmp_path)
    text = to_markdown(report)
    assert "| Colour literals outside token files | 3 |" in text
    assert "## Font host and CDN URLs" in text and "## Uppercase labels" in text
    src = tmp_path / "src"
    assert main([str(src), "--tokens", "appearance/*", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["colour_literals_in_tokens"] == 4

"""Regression tests for skills/app-ui-alignment/scripts/style_audit.py.

Run from the repository root: python -m pytest tests (needs pytest).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "skills" / "app-ui-alignment" / "scripts"))
from style_audit import audit, main, to_markdown  # noqa: E402

TOKENS_TS = """\
export const LIGHT = {
  bg: '#f5f6f8',
  text: '#1b1f24',
  shadow: '0 8px 24px rgb(0 0 0 / 18%)',
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
#header .title { font-size: 0.75rem !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter');
"""

CHART_TSX = """\
// A whole-line comment with #abcdef is skipped.
export const option = {
  textStyle: { fontFamily: 'system-ui, sans-serif', fontSize: 12 },
  color: ['#2a78d6', '#eb6834'],
  borderRadius: 4,
}
const url = 'https://example.com/#section'
"""


def make_app(root: Path) -> Path:
    src = root / "src"
    (src / "appearance").mkdir(parents=True)
    (src / "appearance" / "appearances.ts").write_text(TOKENS_TS, encoding="utf-8")
    (src / "panel.module.css").write_text(PANEL_CSS, encoding="utf-8")
    (src / "Chart.tsx").write_text(CHART_TSX, encoding="utf-8")
    vendored = root / "src" / "node_modules" / "lib"
    vendored.mkdir(parents=True)
    (vendored / "index.css").write_text(".x { color: #123456; }", encoding="utf-8")
    return src


def test_counts_literals_outside_token_files(tmp_path):
    src = make_app(tmp_path)
    report = audit([src], tokens=["*/appearance/*"])
    findings = {(Path(item["file"]).name, item["line"]) for item in report["colour_literals"]}
    # color: #333, the rgba() shadow, and the chart colours; not comments, not the token file, not node_modules,
    # not the #header selector, and not the URL fragment.
    assert findings == {("panel.module.css", 6), ("panel.module.css", 7), ("Chart.tsx", 4)}
    assert report["colour_literals_in_tokens"] == 3
    assert report["files"] == 3


def test_inventories_type_borders_radii_and_motion(tmp_path):
    report = audit([make_app(tmp_path)])
    assert report["font_sizes"] == {"0.8125rem": 1, "0.75rem !important": 1, "12": 1}
    assert "'Segoe UI', sans-serif" in report["font_families"]
    assert "'system-ui, sans-serif'" in report["font_families"]
    # border: 1px solid counts; border-bottom: none and border-radius do not.
    assert sum(report["borders_by_file"].values()) == 1
    assert report["radii"] == {"6px": 1, "4": 1}
    assert report["transitions"] == 1
    assert report["reduced_motion_queries"] == 0
    assert report["important"] == 1
    assert [item["text"].split("?")[0] for item in report["external_requests"]] == [
        "https://fonts.googleapis.com/css2"]


def test_exclude_and_markdown(tmp_path):
    src = make_app(tmp_path)
    report = audit([src], exclude=["*.tsx"])
    assert report["files"] == 2
    text = to_markdown(report)
    assert "| Colour literals outside token files |" in text
    assert "## Font host and CDN URLs" in text


def test_cli_json(tmp_path, capsys):
    src = make_app(tmp_path)
    assert main([str(src), "--tokens", "*/appearance/*", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["colour_literals_in_tokens"] == 3


def test_token_files_and_type_annotations_are_not_uses(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "tokens.ts").write_text("export const T = { border: '#d5dae1', fontSize: 13 }\n", encoding="utf-8")
    (src / "types.ts").write_text("type Ink = { fontFamily: string; fontSize: number }\n", encoding="utf-8")
    report = audit([src], tokens=["*/tokens.ts"])
    assert sum(report["borders_by_file"].values()) == 0
    assert not report["font_sizes"] and not report["font_families"]
    assert report["colour_literals_in_tokens"] == 1

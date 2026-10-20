"""Regression tests for skills/app-ui-alignment/scripts/contrast.py.

Run from the repository root: python -m pytest tests (needs pytest).
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "skills" / "app-ui-alignment" / "scripts"))
from contrast import check, css_tokens, main, parse_colour, ratio, suggest  # noqa: E402


def test_known_ratios():
    assert ratio("#000000", "#ffffff") == pytest.approx(21.0)
    assert ratio("#ffffff", "#ffffff") == pytest.approx(1.0)
    # Values recorded in the dev-skills spec (section 0.6).
    assert ratio("#999999", "#1a1a1a") == pytest.approx(6.11, abs=0.01)
    assert ratio("#5f6b7a", "#ffffff") == pytest.approx(5.43, abs=0.01)
    assert ratio("#003978", "#000000") == pytest.approx(1.86, abs=0.01)


def test_parses_short_long_alpha_and_functional_colours():
    assert parse_colour("#fff") == (255, 255, 255, 1.0)
    assert parse_colour("#00000080")[3] == pytest.approx(128 / 255)
    assert parse_colour("rgb(0 0 0 / 50%)")[3] == pytest.approx(0.5)
    assert parse_colour("rgba(255, 0, 0, 0.25)")[:3] == (255, 0, 0)
    with pytest.raises(ValueError):
        parse_colour("red")


def test_translucent_foreground_is_composited():
    # Half-transparent black over white is mid grey, far below black's 21:1.
    assert ratio("#00000080", "#ffffff") < 5


def test_check_applies_pairs_per_theme_and_resolves_aliases():
    spec = {
        "themes": {
            "dark": {"bg": "#000000", "surface": "#1a1a1a", "muted": "#808080", "focus": "accent", "accent": "#4da3ff"},
            "light": {"bg": "#ffffff", "muted": "#6f7a89", "focus": "var(--accent)", "--accent": "#125dae"},
        },
        "pairs": [
            {"fg": "muted", "bg": ["bg", "surface"], "min": "text"},
            {"fg": "focus", "bg": "bg", "min": "ui"},
            {"fg": "muted", "bg": "bg", "min": "decorative", "themes": ["dark"]},
        ],
    }
    rows = check(spec)
    failing = {(r["theme"], r["fg"], r["bg"]) for r in rows if not r["pass"]}
    assert failing == {("dark", "muted", "surface"), ("light", "muted", "bg")}
    focus = [r for r in rows if r["fg"] == "focus"]
    assert {r["fg_value"] for r in focus} == {"#4da3ff", "#125dae"}
    assert all(r["pass"] for r in rows if r["min"] == 0)
    # "surface" is missing from light, so that pair is skipped there rather than failing.
    assert not any(r["theme"] == "light" and r["bg"] == "surface" for r in rows)


def test_suggestion_passes_on_every_background():
    backgrounds = ["#000000", "#1a1a1a", "#2a2a2a"]
    value = suggest("#808080", backgrounds, 4.5)
    assert value is not None
    assert all(ratio(value, bg) >= 4.5 for bg in backgrounds)
    # The nearest fix for a muted grey on dark surfaces is lighter, not darker.
    assert parse_colour(value)[0] > 0x80


def test_css_tokens_reads_custom_properties_per_block():
    css = """
    /* fallback */
    :root { --color-bg: #f5f6f8; --color-text: #1b1f24; --space-1: 0.25rem; }
    [data-theme="dark"] { --color-bg: #15181c; }
    body { margin: 0; }
    """
    blocks = css_tokens(css)
    assert blocks[":root"]["color-bg"] == "#f5f6f8"
    assert blocks['[data-theme="dark"]'] == {"color-bg": "#15181c"}
    assert "body" not in blocks


def test_cli_exit_status_and_suggestions(tmp_path, capsys):
    spec = {"themes": {"dark": {"bg": "#000000", "muted": "#555555"}}, "pairs": [{"fg": "muted", "bg": "bg"}]}
    path = tmp_path / "pairs.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    assert main(["check", str(path), "--suggest"]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out and "-> #" in out
    spec["themes"]["dark"]["muted"] = "#999999"
    path.write_text(json.dumps(spec), encoding="utf-8")
    assert main(["check", str(path)]) == 0

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


def test_mix_color_mix_and_over_expressions():
    theme = {"bg": "#000000", "success": "#28a745", "tint": "mix(success, bg, 0.16)",
             "css-tint": "color-mix(in srgb, var(--success) 16%, var(--bg))",
             "veil": "rgba(77, 163, 255, 0.08) over bg"}
    from contrast import evaluate, to_hex
    assert to_hex(evaluate(theme, "tint")) == to_hex(evaluate(theme, "css-tint")) == "#061b0b"
    assert to_hex(evaluate(theme, "veil")) == "#060d14"
    assert to_hex(evaluate(theme, "color-mix(in srgb, #ffffff 50%, #000000 50%)")) == "#808080"


def test_translucent_background_needs_over():
    spec = {"themes": {"dark": {"bg": "#000000", "veil": "rgba(77, 163, 255, 0.08)", "text": "#e5e5e5"}},
            "pairs": [{"fg": "text", "bg": "veil over bg"}]}
    assert check(spec)[0]["pass"]
    with pytest.raises(ValueError):
        check({**spec, "pairs": [{"fg": "text", "bg": "veil"}]})


def test_themes_from_a_json_dump(tmp_path):
    dump = {"light": {"chrome": {"bg": "#ffffff", "text": "#1b1f24"}}, "dark": {"chrome": {"bg": "#15181c"}}}
    (tmp_path / "themes.json").write_text(json.dumps(dump), encoding="utf-8")
    rows = check({"themes_file": "themes.json", "themes_key": "chrome", "pairs": [{"fg": "text", "bg": "bg"}]},
                 tmp_path)
    assert [(r["theme"], r["pass"]) for r in rows] == [("light", True)]


def test_hue_and_background_suggestions():
    from contrast import suggest_background, suggest_hue
    value = suggest_hue("#d6dde4", ["#ffffff"], 3.0)
    r, g, b, _ = parse_colour(value)
    assert ratio(value, "#ffffff") >= 3.0 and b > r          # still blue-grey, not neutral
    background = suggest_background("#188038", "#e1efe5", 4.5)
    assert ratio("#188038", background) >= 4.5
    assert parse_colour(background)[1] > parse_colour("#e1efe5")[1]   # a lighter tint, not a darker one


def test_cli_failures_only_ratio_and_mix(tmp_path, capsys):
    spec = {"themes": {"dark": {"bg": "#000000", "muted": "#555555", "text": "#ffffff", "rule": "#222222"}},
            "pairs": [{"fg": "muted", "bg": "bg"}, {"fg": "text", "bg": "bg"},
                      {"fg": "rule", "bg": "bg", "min": "decorative"}]}
    path = tmp_path / "pairs.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    assert main(["check", str(path), "--failures-only"]) == 1
    out = capsys.readouterr().out
    assert "muted" in out and "| dark | text" not in out
    assert "1 of 2 pairs pass; 1 decorative pairs not checked." in out
    assert main(["ratio", "#000000", "#ffffff"]) == 0
    assert capsys.readouterr().out.strip() == "21.00"
    assert main(["mix", "#ffffff", "#000000", "50%"]) == 0
    assert capsys.readouterr().out.strip() == "#808080"

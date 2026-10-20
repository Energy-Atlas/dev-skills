"""Check WCAG 2.2 contrast for every token pair of every theme or appearance, and suggest passing replacements.

    python contrast.py check PAIRS.json [--suggest]
    python contrast.py css-tokens FILE.css

PAIRS.json:

    {
      "themes": {
        "dark":  {"bg": "#000000", "surface": "#1a1a1a", "text": "#e5e5e5", "muted": "#808080"},
        "light": {"bg": "#ffffff", "surface": "#f4f7fb", "text": "#18202c", "muted": "#6f7a89"}
      },
      "pairs": [
        {"fg": "text",  "bg": ["bg", "surface"], "min": "text"},
        {"fg": "muted", "bg": ["bg", "surface"], "min": "text"},
        {"fg": "border-interactive", "bg": ["bg"], "min": "ui", "themes": ["dark"]}
      ]
    }

A pair names tokens (or literal colours) and a minimum: a number, or one of "text" (4.5), "large" (3), "ui" (3, borders
of controls, focus, state indicators, chart marks) and "decorative" (no target; reported only). A pair applies to every
theme that defines both tokens unless "themes" restricts it. Colours are #rgb, #rrggbb, #rrggbbaa, or rgb()/rgba();
a translucent foreground is composited over the background first. A token's value may name another token.

`check` exits 1 if any pair fails. `--suggest` finds, for each failing foreground, the nearest colour (mixed toward black
or white) that passes on every background it is checked against. `css-tokens` prints the custom properties of each rule
block of a stylesheet as JSON, to seed a themes object.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MINIMUMS = {"text": 4.5, "large": 3.0, "ui": 3.0, "decorative": 0.0}


def parse_colour(value: str) -> tuple[float, float, float, float]:
    value = value.strip()
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) in (3, 4):
            digits = "".join(c * 2 for c in digits)
        if len(digits) not in (6, 8):
            raise ValueError(f"not a colour: {value}")
        channels = [int(digits[i:i + 2], 16) for i in range(0, len(digits), 2)]
        alpha = channels[3] / 255 if len(channels) == 4 else 1.0
        return channels[0], channels[1], channels[2], alpha
    match = re.fullmatch(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)", value)
    if match:
        r, g, b, a = match.groups()
        alpha = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        return float(r), float(g), float(b), alpha
    raise ValueError(f"not a colour: {value}")


def to_hex(rgb) -> str:
    return "#" + "".join(f"{round(max(0, min(255, c))):02x}" for c in rgb[:3])


def composite(fg, bg):
    alpha = fg[3]
    return tuple(fg[i] * alpha + bg[i] * (1 - alpha) for i in range(3)) + (1.0,)


def luminance(rgb) -> float:
    channels = [c / 255 for c in rgb[:3]]
    channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def ratio(fg: str, bg: str) -> float:
    background = parse_colour(bg)
    if background[3] < 1:
        raise ValueError(f"background must be opaque: {bg}")
    foreground = composite(parse_colour(fg), background)
    high, low = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def resolve(theme: dict, name: str, depth: int = 0) -> str:
    if depth > 10:
        raise ValueError(f"token cycle at {name}")
    value = theme.get(name, name)
    if isinstance(value, str) and value in theme and value != name:
        return resolve(theme, value, depth + 1)
    if isinstance(value, str) and value.startswith("var("):
        inner = value[4:-1].split(",")[0].strip()
        return resolve(theme, inner if inner in theme else inner.removeprefix("--"), depth + 1)
    return value


def minimum(value) -> float:
    return MINIMUMS[value] if isinstance(value, str) else float(value)


def check(spec: dict) -> list[dict]:
    rows = []
    for pair in spec["pairs"]:
        backgrounds = pair["bg"] if isinstance(pair["bg"], list) else [pair["bg"]]
        for theme_name, theme in spec["themes"].items():
            if "themes" in pair and theme_name not in pair["themes"]:
                continue
            if pair["fg"] not in theme and not pair["fg"].startswith(("#", "rgb")):
                continue
            for bg in backgrounds:
                if bg not in theme and not bg.startswith(("#", "rgb")):
                    continue
                fg_value, bg_value = resolve(theme, pair["fg"]), resolve(theme, bg)
                value = ratio(fg_value, bg_value)
                target = minimum(pair.get("min", "text"))
                rows.append({"theme": theme_name, "fg": pair["fg"], "fg_value": fg_value, "bg": bg,
                             "bg_value": bg_value, "ratio": round(value, 2), "min": target,
                             "pass": value >= target or target == 0})
    return rows


def suggest(fg: str, backgrounds: list[str], target: float) -> str | None:
    """The smallest move toward black or white that passes on every background."""
    base = parse_colour(fg)
    best = None
    for anchor in ((0, 0, 0), (255, 255, 255)):
        for step in range(1, 101):
            t = step / 100
            candidate = tuple(base[i] + (anchor[i] - base[i]) * t for i in range(3)) + (base[3],)
            hex_value = to_hex(candidate)
            if base[3] < 1:
                hex_value += f"{round(base[3] * 255):02x}"
            if all(ratio(hex_value, bg) >= target for bg in backgrounds):
                if best is None or t < best[0]:
                    best = (t, hex_value)
                break
    return best[1] if best else None


def css_tokens(text: str) -> dict:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    blocks = {}
    for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text):
        found = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", body))
        if found:
            blocks.setdefault(" ".join(selector.split()), {}).update({k: v.strip() for k, v in found.items()})
    return blocks


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("pairs", type=Path)
    check_parser.add_argument("--suggest", action="store_true")
    css_parser = commands.add_parser("css-tokens")
    css_parser.add_argument("stylesheet", type=Path)
    args = parser.parse_args(argv)

    if args.command == "css-tokens":
        print(json.dumps(css_tokens(args.stylesheet.read_text(encoding="utf-8")), indent=2))
        return 0

    spec = json.loads(args.pairs.read_text(encoding="utf-8"))
    rows = check(spec)
    print("| Theme | Foreground | Background | Ratio | Minimum | Result |\n| --- | --- | --- | --- | --- | --- |")
    for row in rows:
        result = "pass" if row["pass"] else "FAIL"
        if row["min"] == 0:
            result = "decorative"
        print(f"| {row['theme']} | {row['fg']} `{row['fg_value']}` | {row['bg']} `{row['bg_value']}` | "
              f"{row['ratio']:.2f} | {row['min']:g} | {result} |")
    failures = [row for row in rows if not row["pass"]]
    if args.suggest and failures:
        print("\nSuggestions (nearest passing value on every background checked):\n")
        grouped = {}
        for row in rows:
            if row["min"] > 0:
                grouped.setdefault((row["theme"], row["fg"], row["fg_value"], row["min"]), []).append(row["bg_value"])
        for (theme, fg, value, target), backgrounds in grouped.items():
            if any(r["theme"] == theme and r["fg"] == fg and not r["pass"] for r in failures):
                print(f"- {theme} {fg}: {value} -> {suggest(value, backgrounds, target) or 'none found'}")
    print(f"\n{len(rows) - len(failures)} of {len(rows)} pairs pass.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

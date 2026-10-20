"""Check WCAG 2.2 contrast for every token pair of every theme or appearance, and suggest passing replacements.

    python contrast.py check PAIRS.json [--suggest] [--failures-only]
    python contrast.py ratio FG BG
    python contrast.py mix A B AMOUNT
    python contrast.py css-tokens FILE.css

PAIRS.json:

    {
      "themes": {
        "dark":  {"bg": "#000000", "surface": "#1a1a1a", "text": "#e5e5e5", "muted": "#808080",
                  "success": "#28a745", "success-tint": "mix(success, bg, 0.16)"},
        "light": {"bg": "#ffffff", "surface": "#f4f7fb", "text": "#18202c", "muted": "#6f7a89"}
      },
      "pairs": [
        {"fg": "text",  "bg": ["bg", "surface"], "min": "text"},
        {"fg": "muted", "bg": ["bg", "surface"], "min": "text"},
        {"fg": "success", "bg": ["success-tint"], "min": "text", "themes": ["dark"]},
        {"fg": "border-interactive", "bg": ["bg", "surface"], "min": "ui"}
      ]
    }

Instead of "themes", a spec may name a JSON dump of the app's token module, "themes_file" (relative to the spec), and
optionally "themes_key", a dotted path inside each theme ("chrome"). Dump a TypeScript module with, for example,
`npx tsx -e "import {APPEARANCES} from './src/theme.ts'; console.log(JSON.stringify(APPEARANCES))" > themes.json`.

A pair names tokens or colour expressions and a minimum: a number, or one of "text" (4.5), "large" (3), "ui" (3,
borders of controls, focus, state indicators, chart marks) and "decorative" (no target; reported apart). A pair applies
to every theme that defines its tokens unless "themes" restricts it. A colour expression is #rgb, #rrggbb, #rrggbbaa,
rgb()/rgba(), a token name, var(--token), `mix(A, B, AMOUNT)` (AMOUNT of A over B, 0-1 or a percentage),
`color-mix(in srgb, A P%, B)`, or `A over B` (a translucent A composited over B). Backgrounds must end up opaque.

`check` exits 1 if any pair fails. `--suggest` gives, for each failing foreground, the nearest passing colour mixed
toward black or white and the nearest with the same hue and saturation, and for each failing pair a background that
would pass. A pair that fails because two elements touch (an outline drawn on a fill) may need a gap rather than a new
colour. The functions (`ratio`, `mix`, `parse_colour`) can also be imported.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from pathlib import Path

MINIMUMS = {"text": 4.5, "large": 3.0, "ui": 3.0, "decorative": 0.0}

Colour = tuple[float, float, float, float]


def parse_colour(value: str) -> Colour:
    value = value.strip()
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) in (3, 4):
            digits = "".join(c * 2 for c in digits)
        if len(digits) not in (6, 8) or not re.fullmatch(r"[0-9a-fA-F]+", digits):
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


def to_hex(colour) -> str:
    text = "#" + "".join(f"{round(max(0, min(255, c))):02x}" for c in colour[:3])
    if len(colour) > 3 and colour[3] < 1:
        text += f"{round(colour[3] * 255):02x}"
    return text


def composite(fg: Colour, bg: Colour) -> Colour:
    alpha = fg[3]
    return tuple(fg[i] * alpha + bg[i] * (1 - alpha) for i in range(3)) + (bg[3] + alpha * (1 - bg[3]),)


def mix(a, b, amount: float) -> Colour:
    """`amount` of colour a over colour b, mixed in sRGB like color-mix(in srgb, a <amount>, b)."""
    a = parse_colour(a) if isinstance(a, str) else a
    b = parse_colour(b) if isinstance(b, str) else b
    return tuple(a[i] * amount + b[i] * (1 - amount) for i in range(4))


def luminance(colour) -> float:
    channels = [c / 255 for c in colour[:3]]
    channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def ratio(fg, bg) -> float:
    background = parse_colour(bg) if isinstance(bg, str) else bg
    if background[3] < 1:
        raise ValueError(f"background must be opaque (use 'X over <base>'): {to_hex(background)}")
    foreground = composite(parse_colour(fg) if isinstance(fg, str) else fg, background)
    high, low = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def split_arguments(text: str) -> list[str]:
    parts, depth, current = [], 0, ""
    for char in text:
        if char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
            continue
        depth += char == "("
        depth -= char == ")"
        current += char
    return parts + [current.strip()]


def amount(text: str) -> float:
    text = text.strip()
    return float(text[:-1]) / 100 if text.endswith("%") else float(text)


def evaluate(theme: dict, expression: str, depth: int = 0) -> Colour:
    """Evaluate a token name or colour expression in a theme."""
    if depth > 20:
        raise ValueError(f"token cycle at {expression}")
    expression = expression.strip()
    over = re.split(r"\s+over\s+", expression, maxsplit=1)
    if len(over) == 2:
        return composite(evaluate(theme, over[0], depth + 1), evaluate(theme, over[1], depth + 1))
    if expression.startswith("mix(") and expression.endswith(")"):
        a, b, share = split_arguments(expression[4:-1])
        return mix(evaluate(theme, a, depth + 1), evaluate(theme, b, depth + 1), amount(share))
    if expression.startswith("color-mix(") and expression.endswith(")"):
        _space, first, second = split_arguments(expression[10:-1])
        a, _, share = first.rpartition(" ")
        if second.endswith("%"):
            second = second.rpartition(" ")[0]
        return mix(evaluate(theme, a, depth + 1), evaluate(theme, second, depth + 1), amount(share))
    if expression.startswith("var(") and expression.endswith(")"):
        name = split_arguments(expression[4:-1])[0]
        return evaluate(theme, name if name in theme else name.removeprefix("--"), depth + 1)
    if expression in theme:
        return evaluate(theme, str(theme[expression]), depth + 1)
    if f"--{expression}" in theme:
        return evaluate(theme, str(theme[f"--{expression}"]), depth + 1)
    return parse_colour(expression)


def defines(theme: dict, expression: str) -> bool:
    try:
        evaluate(theme, expression)
        return True
    except (ValueError, KeyError):
        return False


def minimum(value) -> float:
    return MINIMUMS[value] if isinstance(value, str) else float(value)


def load_themes(spec: dict, base: Path | None = None) -> dict:
    if "themes" in spec:
        return spec["themes"]
    data = json.loads(((base or Path(".")) / spec["themes_file"]).read_text(encoding="utf-8"))
    for key in filter(None, spec.get("themes_key", "").split(".")):
        data = {name: theme[key] for name, theme in data.items()}
    return data


def check(spec: dict, base: Path | None = None) -> list[dict]:
    rows = []
    themes = load_themes(spec, base)
    for pair in spec["pairs"]:
        backgrounds = pair["bg"] if isinstance(pair["bg"], list) else [pair["bg"]]
        target = minimum(pair.get("min", "text"))
        for theme_name, theme in themes.items():
            if "themes" in pair and theme_name not in pair["themes"]:
                continue
            if not defines(theme, pair["fg"]):
                continue
            for bg in backgrounds:
                if not defines(theme, bg):
                    continue
                fg_value, bg_value = evaluate(theme, pair["fg"]), evaluate(theme, bg)
                value = ratio(fg_value, bg_value)
                rows.append({"theme": theme_name, "fg": pair["fg"], "fg_value": to_hex(fg_value), "bg": bg,
                             "bg_value": to_hex(bg_value), "ratio": round(value, 2), "min": target,
                             "decorative": target == 0, "pass": value >= target})
    return rows


def suggest(fg: str, backgrounds: list[str], target: float) -> str | None:
    """The smallest move toward black or white that passes on every background."""
    base = parse_colour(fg)
    best = None
    for anchor in ((0, 0, 0, base[3]), (255, 255, 255, base[3])):
        for step in range(1, 101):
            candidate = to_hex(mix(anchor, base, step / 100))
            if all(ratio(candidate, bg) >= target for bg in backgrounds):
                if best is None or step < best[0]:
                    best = (step, candidate)
                break
    return best[1] if best else None


def suggest_hue(fg: str, backgrounds: list[str], target: float) -> str | None:
    """The smallest change of lightness, keeping hue and saturation, that passes on every background."""
    r, g, b, alpha = parse_colour(fg)
    hue, light, saturation = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    for step in range(1, 101):
        for direction in (-1, 1):
            level = light + direction * step / 100
            if 0 <= level <= 1:
                candidate = to_hex(tuple(c * 255 for c in colorsys.hls_to_rgb(hue, level, saturation)) + (alpha,))
                if all(ratio(candidate, bg) >= target for bg in backgrounds):
                    return candidate
    return None


def suggest_background(fg: str, bg: str, target: float) -> str | None:
    """The nearest background, moved away from the foreground's luminance, on which the pair passes."""
    anchor = (255, 255, 255, 1) if luminance(composite(parse_colour(fg), parse_colour(bg))) < \
        luminance(parse_colour(bg)) else (0, 0, 0, 1)
    for step in range(1, 101):
        candidate = to_hex(mix(anchor, bg, step / 100))
        if ratio(fg, candidate) >= target:
            return candidate
    return None


def css_tokens(text: str) -> dict:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    blocks = {}
    for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text):
        found = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", body))
        if found:
            blocks.setdefault(" ".join(selector.split()), {}).update({k: v.strip() for k, v in found.items()})
    return blocks


def report(rows: list[dict], failures_only: bool, with_suggestions: bool) -> None:
    shown = [row for row in rows if not row["pass"] and not row["decorative"]] if failures_only else rows
    print("| Theme | Foreground | Background | Ratio | Minimum | Result |\n| --- | --- | --- | --- | --- | --- |")
    for row in shown:
        result = "decorative" if row["decorative"] else ("pass" if row["pass"] else "FAIL")
        print(f"| {row['theme']} | {row['fg']} `{row['fg_value']}` | {row['bg']} `{row['bg_value']}` | "
              f"{row['ratio']:.2f} | {row['min']:g} | {result} |")
    checked = [row for row in rows if not row["decorative"]]
    failures = [row for row in checked if not row["pass"]]
    if with_suggestions and failures:
        print("\nForeground suggestions (pass on every background checked; mixed / same hue):\n")
        grouped = {}
        for row in checked:
            grouped.setdefault((row["theme"], row["fg"], row["fg_value"], row["min"]), []).append(row["bg_value"])
        for (theme, fg, value, target), backgrounds in grouped.items():
            if any(r["theme"] == theme and r["fg"] == fg for r in failures):
                print(f"- {theme} {fg}: {value} -> {suggest(value, backgrounds, target) or 'none'} / "
                      f"{suggest_hue(value, backgrounds, target) or 'none'}")
        print("\nBackground suggestions (per failing pair):\n")
        for row in failures:
            print(f"- {row['theme']} {row['fg']} on {row['bg']}: {row['bg_value']} -> "
                  f"{suggest_background(row['fg_value'], row['bg_value'], row['min']) or 'none'}")
    decorative = len(rows) - len(checked)
    print(f"\n{len(checked) - len(failures)} of {len(checked)} pairs pass"
          + (f"; {decorative} decorative pairs not checked." if decorative else "."))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    check_parser = commands.add_parser("check", help="check every pair of a spec")
    check_parser.add_argument("pairs", type=Path)
    check_parser.add_argument("--suggest", action="store_true")
    check_parser.add_argument("--failures-only", action="store_true")
    ratio_parser = commands.add_parser("ratio", help="contrast of one pair")
    ratio_parser.add_argument("fg")
    ratio_parser.add_argument("bg")
    mix_parser = commands.add_parser("mix", help="AMOUNT of A over B, as hex")
    mix_parser.add_argument("a")
    mix_parser.add_argument("b")
    mix_parser.add_argument("amount")
    css_parser = commands.add_parser("css-tokens", help="custom properties per rule block, as JSON")
    css_parser.add_argument("stylesheet", type=Path)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    if args.command == "css-tokens":
        print(json.dumps(css_tokens(args.stylesheet.read_text(encoding="utf-8")), indent=2))
        return 0
    if args.command == "ratio":
        print(f"{ratio(evaluate({}, args.fg), evaluate({}, args.bg)):.2f}")
        return 0
    if args.command == "mix":
        print(to_hex(mix(args.a, args.b, amount(args.amount))))
        return 0
    spec = json.loads(args.pairs.read_text(encoding="utf-8"))
    rows = check(spec, args.pairs.parent)
    report(rows, args.failures_only, args.suggest)
    return 1 if any(not row["pass"] and not row["decorative"] for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())

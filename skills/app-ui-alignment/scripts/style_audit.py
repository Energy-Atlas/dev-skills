"""Inventory the styling of a web application's source before and after a UI alignment.

Counts what an alignment changes: colour literals outside the token files, font sizes and families, border, radius,
and shadow declarations, uppercase labels and letter spacing, transitions, `!important`, and requests to font hosts
and CDNs. The report is the factual "observed gaps" table of the alignment record (phase 2) and, run again, evidence
of what changed (phase 7). Counts are evidence, not goals: a grid-framed alignment adds borders on purpose.

    python style_audit.py SRC [SRC ...] [--tokens GLOB ...] [--exclude GLOB ...] [--json]

SRC is a folder or file. Globs are matched against the path as given and against the path relative to SRC, so
`--tokens "src/theme/*"` and `--tokens "theme/*"` both work for SRC `src`. --tokens names the files that may hold
literal values (token or appearance definitions): their literals are counted but not listed, their keys are not counted
as uses, and their custom properties (`--name: value`) are used to resolve `var(--name)` in the radius table.

Run it on a library's stylesheet too (`node_modules/<package>/style`) to list the radii, shadows, and transitions the
app will have to override. Exit status 0 always: the report informs, it does not gate.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less"}
EXTENSIONS = STYLE_EXTENSIONS | {".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue", ".svelte", ".html"}
SKIP_DIRS = {"node_modules", "dist", "build", "coverage", ".git", ".next", ".nuxt", ".svelte-kit", "out", "site",
             "playwright-report", "test-results", "__pycache__"}

HEX = re.compile(r"(?<![\w&/])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![\w-])")
COLOUR_FUNCTION = re.compile(r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(\s*[\d.]")
EXTERNAL = re.compile(r"https?://(?:fonts\.googleapis\.com|fonts\.gstatic\.com|use\.typekit\.net|fonts\.bunny\.net|"
                      r"cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com|rsms\.me)[^\s'\"<>)]*")
CUSTOM_PROPERTY = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+);")

# Property names in CSS (kebab case, value up to ";" across lines) and in JavaScript (camel case, with an optional
# prefix such as headerFontSize, value a quoted string, an array, or a bare expression on one line).
PROPERTIES = {
    "font_size": ("font-size", r"[A-Za-z]*[Ff]ontSize"),
    "font_family": ("font-family", r"[A-Za-z]*[Ff]ontFamily"),
    "border": (r"border(?:-(?:top|right|bottom|left|block|inline)(?:-(?:start|end))?)?",
               r"border(?:Top|Right|Bottom|Left|Block|Inline)?"),
    "radius": (r"border(?:-(?:top|bottom)-(?:left|right))?-radius", r"[A-Za-z]*[Bb]orderRadius"),
    "shadow": ("box-shadow", r"boxShadow"),
    "transform": ("text-transform", r"textTransform"),
    "tracking": ("letter-spacing", r"letterSpacing"),
    "motion": (r"transition(?:-[a-z]+)?|animation(?:-[a-z]+)?", r"transition|animation"),
}

# TypeScript annotations such as `fontFamily: string` are declarations, not values.
TYPE_NAMES = {"string", "number", "boolean", "unknown", "any", "string | number", "number | string"}
NO_VALUE = re.compile(r"^\s*(?:none|0|0px|unset|initial|inherit|false|null|undefined)\s*(?:!important)?\s*$")


def strip_comments(text: str) -> str:
    """Blank out /* */ blocks, HTML comments, and whole-line // comments, keeping line numbers."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))  # noqa: E731
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", text)


def matches(path: Path, source: Path, patterns: list[str]) -> bool:
    candidates = {path.as_posix()}
    if source.is_dir():
        candidates.add(path.relative_to(source).as_posix())
    return any(fnmatch.fnmatch(candidate, pattern) for candidate in candidates for pattern in patterns)


def iter_files(sources: list[Path], exclude: list[str]):
    for source in sources:
        if source.is_file():
            candidates = [source]
        else:
            candidates = (p for p in source.rglob("*")
                          if p.is_file() and not set(p.relative_to(source).parts[:-1]) & SKIP_DIRS)
        for path in sorted(candidates):
            if path.suffix in EXTENSIONS and not matches(path, source, exclude):
                yield source, path


def declarations(text: str, is_style: bool):
    """Yield (kind, value, offset) for every declaration of interest in a file."""
    for kind, (css_name, js_name) in PROPERTIES.items():
        if is_style:
            for match in re.finditer(rf"(?<![\w-])(?:{css_name})\s*:\s*([^;{{}}]+)", text):
                yield kind, " ".join(match.group(1).split()), match.start()
            continue
        seen = set()
        if "-" in css_name:
            # CSS inside template strings and <style> blocks of script and markup files, one line at a time.
            for match in re.finditer(rf"(?<![\w-])(?:{css_name})\s*:\s*([^\s;{{}}'\"`,][^;{{}}\n'\"`]*)", text):
                seen.add(match.start())
                yield kind, match.group(1).strip().rstrip(","), match.start()
        # JavaScript properties: a quoted string, an array, or a bare expression.
        js = rf"(?<![\w$.-])(?:{js_name})\s*:\s*(?:(['\"`])(.*?)\1|(\[[^\]]*\])|([^,;}}\n]+))"
        for match in re.finditer(js, text):
            if match.start() in seen:
                continue
            quote, quoted, array, bare = match.groups()
            yield kind, (f"{quote}{quoted}{quote}" if quote else (array or bare).strip()), match.start()


def shadow_kind(value: str) -> str:
    """'edge' for inset shadows and rings without blur (borders drawn with box-shadow), else 'elevation'."""
    if "inset" in value:
        return "edge"
    lengths = re.findall(r"(-?[\d.]+)(?:px|rem|em)?(?=[\s,)]|$)", re.sub(r"\([^)]*\)", "", value))
    numbers = [float(n) for n in lengths]
    return "edge" if len(numbers) >= 3 and numbers[2] == 0 else "elevation"


def audit(sources: list[Path], tokens: list[str] | None = None, exclude: list[str] | None = None) -> dict:
    tokens = tokens or []
    exclude = exclude or []
    report = {
        "files": 0,
        "colour_literals": [],          # outside the token files: {file, line, text}
        "colour_literals_in_tokens": 0,
        "font_sizes": Counter(),
        "font_size_literals": [],       # sizes that are not var(...): {file, line, text}
        "font_families": Counter(),
        "borders_by_file": Counter(),
        "radii": Counter(),
        "elevation_shadows": Counter(),
        "edge_shadows": Counter(),
        "uppercase": [],
        "letter_spacing": Counter(),
        "motion": 0,
        "reduced_motion_queries": 0,
        "important": [],
        "external_requests": [],
    }
    custom_properties = defaultdict(set)
    files = list(iter_files(sources, exclude))
    texts = {}
    for source, path in files:
        raw = path.read_text(encoding="utf-8", errors="replace")
        texts[path] = (source, raw, strip_comments(raw))
        for name, value in CUSTOM_PROPERTY.findall(texts[path][2]):
            custom_properties[name].add(" ".join(value.split()))

    def resolve(value: str) -> str:
        found = re.fullmatch(r"var\((--[\w-]+)(?:,[^)]*)?\)", value)
        if found and len(custom_properties.get(found.group(1), ())) == 1:
            return f"{value} = {next(iter(custom_properties[found.group(1)]))}"
        return value

    for path, (source, raw, text) in texts.items():
        report["files"] += 1
        posix = path.as_posix()
        is_token_file = matches(path, source, tokens)
        line_of = lambda offset: text.count("\n", 0, offset) + 1  # noqa: E731
        for match in EXTERNAL.finditer(raw):
            report["external_requests"].append({"file": posix, "line": raw.count("\n", 0, match.start()) + 1,
                                                "text": match.group(0)})
        lines = text.splitlines()
        for number, line in enumerate(lines, start=1):
            colours = HEX.findall(line) + COLOUR_FUNCTION.findall(line)
            if colours:
                if is_token_file:
                    report["colour_literals_in_tokens"] += len(colours)
                else:
                    report["colour_literals"].append({"file": posix, "line": number, "text": line.strip()[:120]})
            if not is_token_file:
                report["reduced_motion_queries"] += line.count("prefers-reduced-motion")
                if "!important" in line:
                    report["important"].append({"file": posix, "line": number, "text": line.strip()[:120]})
        if is_token_file:
            # Token files define values; their keys (border, fontSize, ...) are not uses.
            continue
        for kind, value, offset in declarations(text, path.suffix in STYLE_EXTENSIONS):
            plain = value.strip("'\"`")
            if plain in TYPE_NAMES:
                continue
            location = {"file": posix, "line": line_of(offset), "text": lines[line_of(offset) - 1].strip()[:120]}
            if kind == "font_size":
                report["font_sizes"][plain] += 1
                if not plain.startswith("var("):
                    report["font_size_literals"].append(location)
            elif kind == "font_family":
                report["font_families"][value] += 1
            elif kind == "border" and not NO_VALUE.match(plain):
                report["borders_by_file"][posix] += 1
            elif kind == "radius" and not NO_VALUE.match(plain) and not NO_VALUE.match(resolve(plain).split(" = ")[-1]):
                report["radii"][resolve(plain)] += 1
            elif kind == "shadow" and not NO_VALUE.match(plain):
                report[f"{shadow_kind(plain)}_shadows"][plain] += 1
            elif kind == "transform" and plain == "uppercase":
                report["uppercase"].append(location)
            elif kind == "tracking" and not NO_VALUE.match(plain):
                report["letter_spacing"][resolve(plain)] += 1
            elif kind == "motion" and not NO_VALUE.match(plain):
                report["motion"] += 1
    return report


def to_markdown(report: dict, limit: int = 40) -> str:
    out = [f"# Style audit\n\n{report['files']} files scanned. Borders count the `border` shorthand and its side "
           "shorthands (not `border-color` or radii); zero radii and `none` values are not counted. Edge shadows are "
           "inset or unblurred shadows used as rules and rings; elevation shadows are the rest.\n"]
    summary = [
        ("Colour literals outside token files", len(report["colour_literals"])),
        ("Colour literals in token files", report["colour_literals_in_tokens"]),
        ("Distinct font sizes", len(report["font_sizes"])),
        ("Font sizes not from a token", len(report["font_size_literals"])),
        ("Distinct font families", len(report["font_families"])),
        ("Border declarations", sum(report["borders_by_file"].values())),
        ("Distinct non-zero radii", len(report["radii"])),
        ("Distinct elevation shadows", len(report["elevation_shadows"])),
        ("Distinct edge shadows", len(report["edge_shadows"])),
        ("Uppercase labels", len(report["uppercase"])),
        ("Transitions and animations", report["motion"]),
        ("prefers-reduced-motion queries", report["reduced_motion_queries"]),
        ("!important", len(report["important"])),
        ("Font host or CDN URLs", len(report["external_requests"])),
    ]
    out.append("| Measure | Count |\n| --- | --- |")
    out += [f"| {name} | {count} |" for name, count in summary]

    def table(title, counter, header):
        if counter:
            out.append(f"\n## {title}\n\n| {header} | Uses |\n| --- | --- |")
            out.extend(f"| `{key}` | {count} |" for key, count in counter.most_common(limit))

    def listing(title, items):
        if items:
            out.append(f"\n## {title}\n")
            out.extend(f"- `{item['file']}:{item['line']}` {item['text']}" for item in items[:limit])
            if len(items) > limit:
                out.append(f"- … {len(items) - limit} more")

    table("Font sizes", report["font_sizes"], "Value")
    table("Font families", report["font_families"], "Value")
    table("Border declarations by file", report["borders_by_file"], "File")
    table("Radii", report["radii"], "Value")
    table("Elevation shadows", report["elevation_shadows"], "Value")
    table("Edge shadows", report["edge_shadows"], "Value")
    table("Letter spacing", report["letter_spacing"], "Value")
    listing("Colour literals outside token files", report["colour_literals"])
    listing("Font sizes not from a token", report["font_size_literals"])
    listing("Uppercase labels", report["uppercase"])
    listing("!important", report["important"])
    listing("Font host and CDN URLs", report["external_requests"])
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--tokens", nargs="*", default=[], help="glob(s) of files allowed to hold literal values")
    parser.add_argument("--exclude", nargs="*", default=[], help="glob(s) of files to skip")
    parser.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    parser.add_argument("--limit", type=int, default=40, help="rows per table in Markdown")
    args = parser.parse_args(argv)
    report = audit(args.sources, args.tokens, args.exclude)
    sys.stdout.reconfigure(encoding="utf-8")
    if args.json:
        print(json.dumps({key: (dict(value) if isinstance(value, Counter) else value)
                          for key, value in report.items()}, indent=2))
    else:
        print(to_markdown(report, args.limit), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

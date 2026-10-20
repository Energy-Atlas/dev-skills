"""Inventory the styling of a web application's source before and after a UI alignment.

Counts what an alignment changes: colour literals outside the token files, font sizes, font families, border, radius,
and shadow declarations, transitions, `!important`, and requests to font hosts and CDNs. The report is the factual
"observed gaps" table of the alignment record (phase 2) and, run again, the evidence that the gaps closed (phase 7).

    python style_audit.py SRC [SRC ...] [--tokens GLOB ...] [--exclude GLOB ...] [--json]

SRC is a folder or file. --tokens names the files that may hold literal values (the token or appearance definitions);
literals there are counted but not listed as findings. Exit status 0 always: the report informs, it does not gate.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from collections import Counter
from pathlib import Path

EXTENSIONS = {".css", ".scss", ".sass", ".less", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue", ".svelte", ".html"}
SKIP_DIRS = {"node_modules", "dist", "build", "coverage", ".git", ".next", ".nuxt", ".svelte-kit", "out", "site",
             "playwright-report", "test-results", "__pycache__"}

HEX = re.compile(r"(?<![\w&/])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![\w-])")
COLOUR_FUNCTION = re.compile(r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(\s*[\d.]")
FONT_SIZE = re.compile(r"(?:font-size\s*:\s*|fontSize\s*:\s*)([^;,}\n]+)")
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}\n]+)|fontFamily\s*:\s*(?:(['\"`])(.*?)\2|([\w.$()\[\]]+))")
BORDER = re.compile(r"(?<![\w-])border(?:-(?:top|right|bottom|left|block|inline)(?:-(?:start|end))?)?\s*:\s*([^;}\n]+)")
RADIUS = re.compile(r"(?:border-radius\s*:\s*|borderRadius\s*:\s*)([^;,}\n]+)")
SHADOW = re.compile(r"(?:box-shadow\s*:\s*|boxShadow\s*:\s*)([^;}\n]+)")
TRANSITION = re.compile(r"(?<![\w-])(?:transition|animation)(?:-[a-z]+)?\s*:")
IMPORTANT = re.compile(r"!important")
REDUCED_MOTION = re.compile(r"prefers-reduced-motion")
EXTERNAL = re.compile(r"https?://(?:fonts\.googleapis\.com|fonts\.gstatic\.com|use\.typekit\.net|fonts\.bunny\.net|"
                      r"cdn\.jsdelivr\.net|unpkg\.com|cdnjs\.cloudflare\.com|rsms\.me)[^\s'\"<>)]*")

# TypeScript annotations such as `fontFamily: string` are declarations, not values.
TYPE_NAMES = {"string", "number", "boolean", "unknown", "any"}
NO_BORDER = re.compile(r"^\s*(?:none|0|0px|unset|initial|inherit)\s*!?\w*\s*$")


def strip_comments(text: str) -> str:
    """Blank out /* */ blocks and whole-line // comments, keeping line numbers."""
    text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    text = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", text)


def iter_files(sources: list[Path], exclude: list[str]):
    for source in sources:
        if source.is_file():
            candidates = [source]
        else:
            candidates = (p for p in source.rglob("*") if p.is_file() and not (set(p.relative_to(source).parts[:-1])
                                                                              & SKIP_DIRS))
        for path in sorted(candidates):
            posix = path.as_posix()
            if path.suffix in EXTENSIONS and not any(fnmatch.fnmatch(posix, pattern) for pattern in exclude):
                yield path


def audit(sources: list[Path], tokens: list[str] | None = None, exclude: list[str] | None = None) -> dict:
    tokens = tokens or []
    exclude = exclude or []
    report = {
        "files": 0,
        "colour_literals": [],          # findings outside the token files: {file, line, text}
        "colour_literals_in_tokens": 0,
        "font_sizes": Counter(),
        "font_families": Counter(),
        "borders_by_file": Counter(),
        "radii": Counter(),
        "shadows": Counter(),
        "transitions": 0,
        "reduced_motion_queries": 0,
        "important": 0,
        "external_requests": [],
    }
    for path in iter_files(sources, exclude):
        report["files"] += 1
        posix = path.as_posix()
        is_token_file = any(fnmatch.fnmatch(posix, pattern) for pattern in tokens)
        raw = path.read_text(encoding="utf-8", errors="replace")
        for match in EXTERNAL.finditer(raw):
            line = raw.count("\n", 0, match.start()) + 1
            report["external_requests"].append({"file": posix, "line": line, "text": match.group(0)})
        text = strip_comments(raw)
        for number, line in enumerate(text.splitlines(), start=1):
            colours = HEX.findall(line) + COLOUR_FUNCTION.findall(line)
            if colours:
                if is_token_file:
                    report["colour_literals_in_tokens"] += len(colours)
                else:
                    report["colour_literals"].append({"file": posix, "line": number, "text": line.strip()[:120]})
            if is_token_file:
                # Token files define values; their keys (border, fontSize, ...) are not uses.
                continue
            for value in FONT_SIZE.findall(line):
                value = value.strip().strip("'\"")
                if value not in TYPE_NAMES:
                    report["font_sizes"][value] += 1
            for css, quote, quoted, expression in FONT_FAMILY.findall(line):
                value = css.strip() if css else (f"{quote}{quoted}{quote}" if quote else expression)
                if value not in TYPE_NAMES:
                    report["font_families"][value] += 1
            for value in BORDER.findall(line):
                if not NO_BORDER.match(value):
                    report["borders_by_file"][posix] += 1
            for value in RADIUS.findall(line):
                report["radii"][value.strip().strip("'\"")] += 1
            for value in SHADOW.findall(line):
                report["shadows"][value.strip()] += 1
            report["transitions"] += len(TRANSITION.findall(line))
            report["reduced_motion_queries"] += len(REDUCED_MOTION.findall(line))
            report["important"] += len(IMPORTANT.findall(line))
    return report


def to_markdown(report: dict, limit: int = 40) -> str:
    out = [f"# Style audit\n\n{report['files']} files scanned.\n"]
    summary = [
        ("Colour literals outside token files", len(report["colour_literals"])),
        ("Colour literals in token files", report["colour_literals_in_tokens"]),
        ("Distinct font sizes", len(report["font_sizes"])),
        ("Distinct font families", len(report["font_families"])),
        ("Border declarations", sum(report["borders_by_file"].values())),
        ("Distinct radii", len(report["radii"])),
        ("Distinct shadows", len(report["shadows"])),
        ("Transitions and animations", report["transitions"]),
        ("prefers-reduced-motion queries", report["reduced_motion_queries"]),
        ("!important", report["important"]),
        ("Font host or CDN URLs", len(report["external_requests"])),
    ]
    out.append("| Measure | Count |\n| --- | --- |")
    out += [f"| {name} | {count} |" for name, count in summary]

    def table(title, counter, header):
        if not counter:
            return
        out.append(f"\n## {title}\n\n| {header} | Uses |\n| --- | --- |")
        out.extend(f"| `{key}` | {count} |" for key, count in counter.most_common(limit))

    table("Font sizes", report["font_sizes"], "Value")
    table("Font families", report["font_families"], "Value")
    table("Border declarations by file", report["borders_by_file"], "File")
    table("Radii", report["radii"], "Value")
    table("Shadows", report["shadows"], "Value")
    for title, key in (("Colour literals outside token files", "colour_literals"),
                       ("Font host and CDN URLs", "external_requests")):
        items = report[key]
        if items:
            out.append(f"\n## {title}\n")
            out += [f"- `{item['file']}:{item['line']}` {item['text']}" for item in items[:limit]]
            if len(items) > limit:
                out.append(f"- … {len(items) - limit} more")
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
    if args.json:
        serialisable = {key: (dict(value) if isinstance(value, Counter) else value) for key, value in report.items()}
        print(json.dumps(serialisable, indent=2))
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(to_markdown(report, args.limit), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

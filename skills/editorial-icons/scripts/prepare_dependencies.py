"""Find, and install when missing, the two skills editorial-icons builds on.

- custom-icons (github.com/jkc66/custom-icons-skill): the asset-contract workflow and its validator,
  scripts/validate_icon.py, which every rendered icon must pass. Required.
- draw (the Claude Code plugin draw@claudedraw, github.com/Griffin2/claudedraw): a scribble renderer for quick
  composition sketches before a subject is authored. Optional; it is never used for final assets.

Missing dependencies are installed at their latest version without asking; --update refreshes installed ones too.

    python prepare_dependencies.py            # check, install what is missing, print a report
    python prepare_dependencies.py --json     # the same report as JSON (paths for the agent to use)
    python prepare_dependencies.py --dry-run  # only report what it would do
    python prepare_dependencies.py --update   # also update dependencies that are already installed

Installs: custom-icons with the skills CLI (`npx skills add ... -g -a claude-code --copy -y`, needs Node.js). draw
with the Claude Code CLI (`claude plugin marketplace add` and `claude plugin install`) when it is on PATH; otherwise
(for example in the desktop app) by cloning the plugin's repository into a cache folder, which is all the sketch step
needs (it runs draw.py directly). Exit status: 0 when custom-icons is ready, 1 when it is not.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

CUSTOM_ICONS = {
    "name": "custom-icons",
    "source": "jkc66/custom-icons-skill",
    "validator": Path("scripts") / "validate_icon.py",
}
DRAW = {
    "plugin": "draw@claudedraw",
    "marketplace": "Griffin2/claudedraw",
    "repo": "https://github.com/Griffin2/claudedraw.git",
    "renderer": Path("draw") / "skills" / "draw" / "draw.py",
}


def home() -> Path:
    return Path(os.environ.get("EDITORIAL_ICONS_HOME") or Path.home())


def cache_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_CACHE_HOME") or str(home() / ".cache")
    return Path(base) / "editorial-icons"


def skill_roots(project: Path) -> List[Path]:
    """Folders where agents install skills, project first."""
    h = home()
    return [project / ".claude" / "skills", project / ".agents" / "skills", h / ".claude" / "skills",
            h / ".agents" / "skills"]


def skill_name(skill_md: Path) -> Optional[str]:
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    if not match:
        return None
    name = re.search(r"^name:\s*['\"]?([\w.-]+)", match.group(1), re.M)
    return name.group(1) if name else None


def find_skill(name: str, project: Path) -> Optional[Path]:
    """The folder of an installed skill called `name`, or None."""
    for root in skill_roots(project):
        if not root.is_dir():
            continue
        for skill_md in sorted(root.glob("*/SKILL.md")):
            if skill_name(skill_md) == name:
                return skill_md.parent.resolve()
    return None


def find_draw_renderer() -> Optional[Path]:
    """draw.py from an installed draw plugin or from this script's cache clone, newest first."""
    h = home()
    candidates = sorted((h / ".claude" / "plugins" / "cache").glob("*/draw/*/skills/draw/draw.py"), reverse=True)
    candidates += sorted((h / ".claude" / "plugins" / "marketplaces").glob("*/draw/skills/draw/draw.py"))
    candidates.append(cache_dir() / "claudedraw" / DRAW["renderer"])
    return next((c.resolve() for c in candidates if c.is_file()), None)


def run(command: List[str], dry_run: bool, log: List[str]) -> bool:
    log.append("$ " + " ".join(command))
    if dry_run:
        return True
    executable = shutil.which(command[0])
    if not executable:
        log.append(f"  {command[0]} is not on PATH")
        return False
    result = subprocess.run([executable, *command[1:]], capture_output=True, text=True)
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip().splitlines()
        log.append("  failed" + (f": {output[-1]}" if output else ""))
    return result.returncode == 0


def prepare_custom_icons(project: Path, update: bool, dry_run: bool, log: List[str]) -> Dict[str, object]:
    found = find_skill(CUSTOM_ICONS["name"], project)
    action = "found"
    if found is None or update:
        verb = ["add", CUSTOM_ICONS["source"], "--skill", CUSTOM_ICONS["name"], "-g", "-a", "claude-code", "--copy"] \
            if found is None else ["update", CUSTOM_ICONS["name"], "-g"]
        ok = run(["npx", "-y", "skills", *verb, "-y"], dry_run, log)
        action = ("would install" if found is None else "would update") if dry_run else \
            (("installed" if found is None else "updated") if ok else "install failed")
        found = find_skill(CUSTOM_ICONS["name"], project) or found
    validator = found / CUSTOM_ICONS["validator"] if found else None
    ready = bool(validator and validator.is_file())
    return {"status": action, "ready": ready, "skill_dir": str(found) if found else None,
            "validator": str(validator) if ready else None}


def prepare_draw(update: bool, dry_run: bool, log: List[str]) -> Dict[str, object]:
    renderer = find_draw_renderer()
    action = "found"
    if renderer is None or update:
        installed = False
        if shutil.which("claude"):
            installed = run(["claude", "plugin", "marketplace", "add", DRAW["marketplace"]], dry_run, log) and \
                run(["claude", "plugin", "install", DRAW["plugin"]], dry_run, log)
        if not installed:
            clone = cache_dir() / "claudedraw"
            if (clone / ".git").is_dir():
                installed = run(["git", "-C", str(clone), "pull", "--ff-only"], dry_run, log)
            else:
                installed = run(["git", "clone", "--depth", "1", DRAW["repo"], str(clone)], dry_run, log)
        action = ("would install" if renderer is None else "would update") if dry_run else \
            (("installed" if renderer is None else "updated") if installed else "install failed")
        renderer = find_draw_renderer() or renderer
    return {"status": action, "ready": bool(renderer), "renderer": str(renderer) if renderer else None,
            "optional": True}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare the dependencies of the editorial-icons skill.")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="project root (default: current folder)")
    parser.add_argument("--update", action="store_true", help="also update dependencies that are installed")
    parser.add_argument("--dry-run", action="store_true", help="report what would be done; change nothing")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)

    log: List[str] = []
    report = {
        "custom-icons": prepare_custom_icons(args.project.resolve(), args.update, args.dry_run, log),
        "draw": prepare_draw(args.update, args.dry_run, log),
        "commands": log,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for name in ("custom-icons", "draw"):
            entry = report[name]
            path = entry.get("validator") or entry.get("renderer") or "-"
            note = " (optional)" if entry.get("optional") else ""
            print(f"{name}{note}: {entry['status']}, {'ready' if entry['ready'] else 'NOT ready'}: {path}")
        for line in log:
            print("  " + line)
        if not report["custom-icons"]["ready"]:
            print("custom-icons is required: install it with "
                  f"`npx skills add {CUSTOM_ICONS['source']} --skill custom-icons -g -a claude-code --copy`.")
    return 0 if report["custom-icons"]["ready"] or args.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())

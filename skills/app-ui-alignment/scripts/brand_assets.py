"""Render the raster favicons of a brand mark from its SVG: favicon-32.png, apple-touch-icon.png, and favicon.ico.

    python brand_assets.py MARK.svg OUT_DIR [--browser PATH]

The SVG is drawn by a headless Chromium-based browser (Google Chrome, Chromium, or Microsoft Edge, found in the usual
places, or --browser), so no SVG library is needed; on Windows prefer Chrome, as Edge's launcher can return before the
screenshot is written. Pillow assembles the ICO from 16, 32, and 48 px renders. The apple touch icon gets an opaque
white background, as iOS shows transparency as black. The SVG itself is the vector favicon: copy it next to these
files as favicon.svg.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
NAMES = ["google-chrome", "chromium", "chromium-browser", "chrome", "msedge", "microsoft-edge"]
ICO_SIZES = (16, 32, 48)


def find_browser(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    for path in CANDIDATES:
        if Path(path).exists():
            return path
    for name in NAMES:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("No Chromium-based browser found; pass --browser PATH.")


def render(browser: str, svg: Path, size: int, out: Path, background: str = "transparent") -> Image.Image:
    """Draw the SVG at size x size pixels and return it as an RGBA image."""
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "mark.html"
        page.write_text(
            "<!doctype html><html><head><style>html,body{margin:0;width:100%;height:100%;"
            f"background:{background}}}img{{display:block;width:{size}px;height:{size}px}}</style></head>"
            f'<body><img src="{svg.resolve().as_uri()}"></body></html>',
            encoding="utf-8",
        )
        shot = Path(tmp) / "shot.png"
        subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
             "--default-background-color=00000000", f"--window-size={size},{size}",
             f"--user-data-dir={Path(tmp) / 'profile'}", f"--screenshot={shot}", page.as_uri()],
            check=True, capture_output=True, timeout=120,
        )
        if not shot.exists():
            raise SystemExit(f"{browser} wrote no screenshot; try another browser with --browser.")
        image = Image.open(shot).convert("RGBA").crop((0, 0, size, size))
        image.load()
    image.save(out)
    return image


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("svg", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--browser")
    args = parser.parse_args(argv)
    browser = find_browser(args.browser)
    args.out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        icons = [render(browser, args.svg, size, Path(tmp) / f"{size}.png") for size in ICO_SIZES]
        icons[-1].save(args.out / "favicon.ico", sizes=[(s, s) for s in ICO_SIZES],
                       append_images=icons[:-1])
    render(browser, args.svg, 32, args.out / "favicon-32.png")
    render(browser, args.svg, 180, args.out / "apple-touch-icon.png", background="#ffffff")
    for name in ("favicon.ico", "favicon-32.png", "apple-touch-icon.png"):
        print(f"{(args.out / name).stat().st_size:>8}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Verification

Scripts and browser checks for phases 2, 5, and 7. Save Python scripts to a scratch file and run them; long inline
scripts in Bash on Windows are fragile (heredoc quoting).

## Contrast

Run before asking the owner (phase 2) and again after choosing replacement values. Targets: 4.5:1 for text below 24 px
(18.66 px bold), 3:1 for large text and for borders of controls, none for decorative rules.

```python
def luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def ratio(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


DARK_SURFACES = ["#000000", "#1a1a1a", "#2a2a2a", "#3a3a3a"]
LIGHT_SURFACES = ["#ffffff", "#f8fafc", "#f4f7fb", "#e7edf5"]
CANDIDATES = {
    "dark muted": ("#808080", DARK_SURFACES),
    "dark border-interactive": ("#6b6b6b", DARK_SURFACES[:2]),
    "light muted": ("#6f7a89", LIGHT_SURFACES),
    "light border-interactive": ("#768599", LIGHT_SURFACES),
    "dark brand on base": ("#003978", ["#000000"]),
}
for name, (colour, surfaces) in CANDIDATES.items():
    print(f"{name:26s}", "  ".join(f"{s}:{ratio(colour, s):.2f}" for s in surfaces))
```

Try a few darker or lighter candidates per failing token and pick the lightest that passes on every surface it sits on.
Prefer a value the brand's own CSS already uses for a similar role.

## Vendoring fonts

Downloads the Latin and Latin Extended WOFF2 subsets of Google Fonts families, their OFL licences from the google/fonts
repository, and writes `fonts.css`. Edit `FAMILIES`, run it from the site's root, then commit the files. A modern
browser user agent makes the CSS API serve WOFF2. Downloading files needs the owner's agreement; self-hosting decided in
phase 2 is that agreement.

```python
"""Vendor Google Fonts into an MkDocs site: WOFF2 subsets, OFL licences, and docs/assets/stylesheets/fonts.css."""
import pathlib
import re
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
FAMILIES = [
    # (CSS2 API family spec, family name, local file stem, licence path in github.com/google/fonts)
    ("Geist:wght@100..900", "Geist", "geist", "ofl/geist/OFL.txt"),
    ("Geist+Mono:wght@100..900", "Geist Mono", "geist-mono", "ofl/geistmono/OFL.txt"),
    ("Cormorant+Garamond:ital,wght@1,500", "Cormorant Garamond", "cormorant-garamond-italic-500",
     "ofl/cormorantgaramond/OFL.txt"),
]
SUBSETS = ("latin-ext", "latin")
FONTS = pathlib.Path("docs/assets/fonts")
CSS = pathlib.Path("docs/assets/stylesheets/fonts.css")


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request) as response:
        return response.read()


FONTS.mkdir(parents=True, exist_ok=True)
rules = []
for spec, family, stem, licence in FAMILIES:
    css = get(f"https://fonts.googleapis.com/css2?family={spec}&display=swap").decode("utf-8")
    blocks = dict(re.findall(r"/\* (\S+) \*/\s*@font-face \{(.*?)\}", css, re.S))
    for subset in SUBSETS:
        block = blocks[subset]
        style = re.search(r"font-style: (\w+);", block).group(1)
        weight = re.search(r"font-weight: ([\d ]+);", block).group(1)
        url = re.search(r"src: url\((\S+?)\)", block).group(1)
        unicode_range = re.search(r"unicode-range: ([^;]+);", block).group(1)
        name = f"{stem}-{subset}.woff2"
        (FONTS / name).write_bytes(get(url))
        rules.append(
            "@font-face {\n"
            "  font-display: swap;\n"
            f'  font-family: "{family}";\n'
            f"  font-style: {style};\n"
            f"  font-weight: {weight};\n"
            f'  src: url("../fonts/{name}") format("woff2");\n'
            f"  unicode-range: {unicode_range};\n"
            "}\n"
        )
    licence_name = "OFL-" + family.replace(" ", "") + ".txt"
    (FONTS / licence_name).write_bytes(get(f"https://raw.githubusercontent.com/google/fonts/main/{licence}"))

header = (
    "/*\n"
    " * Fonts of design/ui-design-spec.md, served from the site itself so that viewing it makes no request to a font\n"
    " * host. Latin and Latin Extended subsets; other characters fall back to system fonts. SIL Open Font License 1.1\n"
    " * (assets/fonts/OFL-*.txt).\n"
    " */\n\n"
)
CSS.parent.mkdir(parents=True, exist_ok=True)
CSS.write_text(header + "\n".join(rules), encoding="utf-8", newline="\n")
for path in sorted(FONTS.iterdir()):
    print(f"{path.stat().st_size:>8}  {path.name}")
```

Check the copyright line at the top of each licence file and name it in `fonts.css`. Confirm git stores the WOFF2 files
as binary (`git show --numstat` prints `-  -` for them).

## Browser checks

Drive the site served by `mkdocs serve`. If the browser pane is hidden, `innerWidth` is 0 and screenshots may time out:
emulate a viewport size (1440 x 900 for desktop, 375 x 812 for a phone) before measuring. Reset the emulation afterwards.

### Fonts and external requests

```js
await document.fonts.ready;
({
  loaded: [...document.fonts].filter(f => f.status === "loaded").map(f => `${f.family} ${f.style} ${f.weight}`),
  external: performance.getEntriesByType("resource").map(r => r.name).filter(u => !u.startsWith(location.origin)),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  scheme: document.body.dataset.mdColorScheme,
})
```

Expect every family loaded, `external` empty, and `overflow` 0. After the build, `grep -rl "fonts.googleapis\|fonts.gstatic" site`
must find nothing.

### Light and dark

Material stores the first scheme it chose. To see the default for a system preference, emulate the colour scheme, then:

```js
Object.keys(localStorage).filter(k => k.endsWith("__palette")).forEach(k => localStorage.removeItem(k));
location.reload();
```

### Alignment

On a page with sidebars and on a page that hides them, the hero, strip labels, cell text, and paragraphs share one left
edge, and strips and grids reach the frame:

```js
const content = document.querySelector(".md-content").getBoundingClientRect();
const left = el => el && Math.round(el.getBoundingClientRect().left - content.left);
const right = el => el && Math.round(content.right - el.getBoundingClientRect().right);
const strip = document.querySelector("h2.ui-strip");
const grid = document.querySelector(".grid.cards");
({
  hero: left(document.querySelector(".ui-hero h1")),
  paragraph: left(document.querySelector(".md-typeset > p")),
  stripText: strip && left(strip) + parseFloat(getComputedStyle(strip).paddingLeft),
  cellText: left(document.querySelector(".grid.cards li > p")),
  stripEdges: strip && [left(strip), right(strip)],   // expect [1, 1]: inside the frame rules
  gridEdges: grid && [left(grid), right(grid)],
})
```

### Clickable cells

```js
const cells = [...document.querySelectorAll(".grid.cards li")];
cells[0].scrollIntoView({ block: "center" });
cells.map(cell => {
  const r = cell.getBoundingClientRect();
  const corner = document.elementFromPoint(r.right - 10, r.top + 10);         // empty area
  const inner = cell.querySelector("p:not(:first-of-type) a, .md-button");
  const ir = inner && inner.getBoundingClientRect();
  const innerHit = ir && document.elementFromPoint(ir.left + 3, ir.top + ir.height / 2);
  return { corner: corner && corner.getAttribute("href"), inner: innerHit && innerHit.getAttribute("href") };
});
```

The corner must hit the title link; an inner link must hit itself. `elementFromPoint` returns `null` outside the viewport:
scroll first.

### Instant navigation

```js
window.__marker = "same-document";
document.querySelectorAll(".md-nav--primary a.md-nav__link")[1].click();
// after the page changes:
({ marker: window.__marker || "reloaded",
   fontRequests: performance.getEntriesByType("resource").filter(e => e.name.endsWith(".woff2")).length })
```

Expect `same-document` and no new font requests. Also navigate to and from the landing page: its hidden sidebars must
hide and reappear.

### Hero headline width

Measure the first phrase in em at the hero's font to size the container-query font size:

```js
const span = document.createElement("span");
span.textContent = "Generate building energy models";
span.style.cssText = "font-family:Geist;font-weight:700;letter-spacing:-0.03em;font-size:100px;white-space:nowrap;position:absolute;visibility:hidden";
document.body.append(span);
const em = span.getBoundingClientRect().width / 100;   // e.g. 15.2
span.remove();
({ em, cqi: (100 / em) * 0.94 })                         // use a little less than 100 / em
```

## Checklist

- [ ] `mkdocs build --strict` passes; the project's tests pass.
- [ ] Dark and light, desktop and phone: landing page, a section index, an ordinary page, a generated reference page with
      wide tables, search open with results, an admonition of each colour in use.
- [ ] Fonts from the site's origin only; no external requests; no horizontal overflow.
- [ ] One left edge for hero, strips, cells, and prose, with and without sidebars.
- [ ] Every clickable cell closed on four sides; hover, click, and keyboard focus work; inner links keep their targets.
- [ ] Page changes keep the same document; no flicker; the progress bar shows.
- [ ] Muted text, interactive borders, and state colours meet the contrast targets on the surfaces they use.

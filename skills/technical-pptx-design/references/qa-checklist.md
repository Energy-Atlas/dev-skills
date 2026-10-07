# QA checklist

Check every deck before delivering it: render every slide and look at it, run the automated audit, then go through the
checklist. Fix and re-check; report anything left as it is and why.

## Render every slide

Look at every slide as an image, at full size: overlaps, overflowing text, clipped labels, misalignment, and legibility
only show there.

On Windows with PowerPoint (tested), in PowerShell:

```powershell
$deck = (Resolve-Path deck.pptx).Path
$out = Join-Path (Split-Path $deck) "slides"
$app = New-Object -ComObject PowerPoint.Application
try {
  $pres = $app.Presentations.Open($deck, -1, 0, 0)   # read-only, untitled off, no window
  $pres.Export($out, "PNG", 1600, 900)               # slides\Slide1.PNG, Slide2.PNG, ...
  $pres.Close()
} finally { $app.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app) }
```

Elsewhere, with LibreOffice and Poppler:

```bash
soffice --headless --convert-to pdf deck.pptx
pdftoppm -png -r 110 deck.pdf slide
```

LibreOffice substitutes missing fonts and lays out some text differently from PowerPoint; when the deck will be shown in
PowerPoint, do the final visual check with PowerPoint's rendering if at all possible.

## Font family

The deck's family is the one the skill was given, or Calibri. Set it as the theme's heading and body font with
`python-pptx` (tested; PowerPoint reads the result as the theme fonts):

```python
from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

NS_A = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def set_theme_font(deck, family):
    """Set the heading and body Latin fonts of every slide master's theme, so all text inherits the family."""
    for master in deck.slide_masters:
        part = master.part.part_related_by(RT.THEME)
        theme = etree.fromstring(part.blob)
        for latin in theme.findall(".//a:majorFont/a:latin", NS_A) + theme.findall(".//a:minorFont/a:latin", NS_A):
            latin.set("typeface", family)
        part._blob = etree.tostring(theme, xml_declaration=True, encoding="UTF-8", standalone=True)


# deck = Presentation("deck.pptx"); set_theme_font(deck, "Calibri"); deck.save("deck.pptx")
```

Text then inherits the family everywhere, including native charts and tables; leave fonts unset on text runs. Only
equations (Cambria Math) and code (one monospace family) set their own.

Check that the family is installed where the slides are rendered, or the rendered images show a substitute. On Windows
(tested):

```powershell
Add-Type -AssemblyName System.Drawing
(New-Object System.Drawing.Text.InstalledFontCollection).Families.Name -contains "Calibri"
```

On macOS or Linux: `fc-list : family | grep -i "calibri"`.

## Automated audit

Needs `python-pptx`. Run `python audit_pptx.py deck.pptx --font <family>` (the deck's family; Calibri when omitted); it
reports, per slide, shapes outside the slide, overlapping shapes, text below 11 pt, text set in another font than the
family (Cambria Math, the equation font, is allowed), raster images below 200 dpi as displayed, empty placeholders,
animations, and transitions, and for the deck the theme's heading and body fonts, the fonts set on text, unused slide
layouts, and the number of native charts and tables. Intended overlaps
(a label placed on a map) are reported too: confirm them on the rendered slide. It cannot see text overflow: that needs
the rendered slides.

```python
"""Audit a .pptx for the technical-pptx-design checks that can be automated.

Usage: python audit_pptx.py deck.pptx [--font Calibri] [--min-pt 11] [--min-dpi 200]
Reports, per slide: shapes outside the slide, overlapping shapes, text below the minimum size, text set in a font other
than the deck's family (or the equation font), raster images below the minimum effective resolution, empty
placeholders, animations and transitions; and, for the deck: the theme fonts, fonts in use, slide layouts no slide
uses, and how many charts and tables are native. Text overflow is not detectable here: check the rendered slides.
"""
import argparse
import collections
import itertools

from lxml import etree
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.util import Emu

EMU_PER_INCH = 914400
NS_P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
NS_A = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
THEME_REFERENCES = {"+mj-lt", "+mn-lt"}  # "use the theme's heading or body font"


def theme_fonts(deck):
    """The Latin heading (major) and body (minor) fonts of each slide master's theme."""
    fonts = []
    for master in deck.slide_masters:
        theme = etree.fromstring(master.part.part_related_by(RT.THEME).blob)
        fonts.append((theme.find(".//a:majorFont/a:latin", NS_A).get("typeface"),
                      theme.find(".//a:minorFont/a:latin", NS_A).get("typeface")))
    return fonts


def box(shape):
    return shape.left or 0, shape.top or 0, (shape.left or 0) + (shape.width or 0), (shape.top or 0) + (shape.height or 0)


def overlap_area(a, b):
    width = min(a[2], b[2]) - max(a[0], b[0])
    height = min(a[3], b[3]) - max(a[1], b[1])
    return width * height if width > 0 and height > 0 else 0


def runs(shape):
    if shape.has_text_frame:
        for paragraph in shape.text_frame.paragraphs:
            yield from paragraph.runs
    if getattr(shape, "has_table", False) and shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                for paragraph in cell.text_frame.paragraphs:
                    yield from paragraph.runs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("deck")
    parser.add_argument("--font", default="Calibri", help="the deck's font family (default: Calibri)")
    parser.add_argument("--math-font", default="Cambria Math", help="the font PowerPoint equations use")
    parser.add_argument("--min-pt", type=float, default=11)
    parser.add_argument("--min-dpi", type=float, default=200)
    args = parser.parse_args()

    deck = Presentation(args.deck)
    allowed_fonts = {args.font, args.math_font} | THEME_REFERENCES
    slide_w, slide_h = deck.slide_width, deck.slide_height
    fonts = collections.Counter()
    used_layouts = set()
    counts = collections.Counter()
    problems = 0

    for number, slide in enumerate(deck.slides, start=1):
        used_layouts.add(id(slide.slide_layout))
        notes = []
        shapes = list(slide.shapes)
        for shape in shapes:
            left, top, right, bottom = box(shape)
            if left < 0 or top < 0 or right > slide_w or bottom > slide_h:
                notes.append(f"outside the slide: {shape.name}")
            for run in runs(shape):
                if run.font.name:
                    fonts[run.font.name] += 1
                    if run.font.name not in allowed_fonts:
                        notes.append(f"font {run.font.name!r} instead of {args.font!r} in {shape.name}: {run.text[:40]!r}")
                if run.font.size is not None and run.font.size.pt < args.min_pt:
                    notes.append(f"text at {run.font.size.pt:g} pt in {shape.name}: {run.text[:40]!r}")
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                counts["pictures"] += 1
                image = shape.image
                if image.content_type in ("image/png", "image/jpeg", "image/tiff", "image/bmp", "image/gif"):
                    px_w, px_h = image.size
                    dpi = min(px_w / (shape.width / EMU_PER_INCH), px_h / (shape.height / EMU_PER_INCH))
                    if dpi < args.min_dpi:
                        notes.append(f"image at {dpi:.0f} dpi as displayed: {shape.name}")
            if getattr(shape, "has_chart", False) and shape.has_chart:
                counts["native charts"] += 1
            if getattr(shape, "has_table", False) and shape.has_table:
                counts["native tables"] += 1
            if shape.is_placeholder and shape.has_text_frame and not shape.text_frame.text.strip():
                notes.append(f"empty placeholder: {shape.name}")
        for a, b in itertools.combinations(shapes, 2):
            area = overlap_area(box(a), box(b))
            smaller = min((a.width or 0) * (a.height or 0), (b.width or 0) * (b.height or 0)) or 1
            if area / smaller > 0.02:
                notes.append(f"overlap {area / smaller:.0%} of the smaller: {a.name} / {b.name}")
        xml = slide._element
        if xml.find(f"{NS_P}timing") is not None:
            notes.append("has animations (p:timing)")
        if xml.find(f"{NS_P}transition") is not None:
            notes.append("has a transition")
        if notes:
            problems += len(notes)
            print(f"slide {number}:")
            for note in notes:
                print(f"  - {note}")

    unused = [layout.name for master in deck.slide_masters for layout in master.slide_layouts if id(layout) not in used_layouts]
    print(f"slide size: {Emu(slide_w).inches:.3f} x {Emu(slide_h).inches:.3f} in")
    for heading, body in theme_fonts(deck):
        print(f"theme fonts: heading {heading!r}, body {body!r}")
        for role, name in (("heading", heading), ("body", body)):
            if name != args.font:
                print(f"  - the theme's {role} font is {name!r}, not {args.font!r}: set it, so all text inherits the family")
                problems += 1
    print("fonts set on runs:", dict(fonts) or "none (inherited from the theme)")
    print("counts:", dict(counts))
    print("layouts no slide uses:", unused or "none")
    print(f"{problems} problem(s)")


if __name__ == "__main__":
    main()
```

## Checklist

### Content unchanged

- [ ] Every claim, value, unit, equation, and source is as given; content issues found are listed in the report, not fixed.
- [ ] Every title is a direct subject or a conclusion the slide's own evidence supports.

### Composition

- [ ] Each slide uses one of the layouts in `layouts.md`, on the grid, with one strong composition and generous space.
- [ ] No floating rounded boxes, colour washes, highlight strips, card grids, KPI tiles, pills, badges, tabs, dashboards,
      gradients, glass, blobs, 3D objects, abstract technology imagery, or meaningless icons and callouts.
- [ ] No header, footer, section label, or logo repeated on every slide; the title slide is minimal.
- [ ] No overlaps (except intended labels), no overflowing or clipped text, nothing in the margins.

### Type and colour

- [ ] One family, the requested one or Calibri, set as the theme's heading and body font; no other font on text except
      Cambria Math for equations and one monospace for code; installed where the slides were rendered, and available on
      the presenting machine or embedded (say which in the report).
- [ ] Title slide 36–44 pt, slide titles 27–32 pt, body 18–22 pt, labels, captions, and citations at least 11–14 pt.
- [ ] Neutral background, one accent, only the data colours needed; each variable and category keeps its colour across
      the deck; colourblind-conscious scales suited to the data; meaning never carried by colour alone.

### Evidence

- [ ] Charts: native and editable where practical; axes, units, uncertainty, sample sizes, and baselines preserved; no
      heavy borders, shadows, redundant legends, or unnecessary gridlines; nothing undersized.
- [ ] Maps: useful area maximised, quiet basemap, missing data distinct from zero, only necessary legends, scales, insets,
      and labels; comparable maps share extent, projection, and colour scale.
- [ ] Modelling diagrams: inputs, parameters, states, calculations, and outputs distinguished and explained once;
      connectors directional and meaningful.
- [ ] Equations: proper notation, aligned, symbols defined nearby with units, interpretation separate, no boxes; native
      equations or a vector render with the source in the notes.
- [ ] Tables: native, lightly ruled, units in headers, consistent precision, decimal-aligned numbers, only important
      values highlighted.
- [ ] Images: authentic research material, no filler imagery, resolution preserved (vector, or at least 200 dpi as
      displayed), aspect ratios kept.
- [ ] Citations next to their evidence, concise on the slide, full on a references slide; one caption style.

### File

- [ ] No animations or transitions unless asked for.
- [ ] No unused layouts, empty placeholders, hidden leftover shapes, or template artefacts; speaker notes kept.
- [ ] The file opens in PowerPoint without a repair prompt; everything that should be editable is.

# QA checklist

Check every deck before delivering it: render every slide and look at it, run the automated audit, then go through the
checklist. Fix and re-check; report anything left as it is and why.

## Render every slide

Look at every slide as an image, at full size: overlaps, overflowing text, clipped labels, misalignment, and legibility
only show there.

On Windows with PowerPoint (tested), in PowerShell. It renders a copy of the deck, so a deck the owner has open in
PowerPoint is never touched, and it quits PowerPoint only if it started it. The copy stays in `slides\` with the images;
the folder is scratch output, not part of the delivery:

```powershell
$deck = (Resolve-Path deck.pptx).Path
$out = Join-Path (Split-Path $deck) "slides"
[void](New-Item -ItemType Directory -Force $out)
$copy = Join-Path $out "render-copy.pptx"
Copy-Item $deck $copy -Force                           # render a copy: never touch a deck the owner has open
$running = [bool](Get-Process POWERPNT -ErrorAction SilentlyContinue)
$app = New-Object -ComObject PowerPoint.Application   # joins the owner's PowerPoint if it is already running
$pres = $null
try {
  $pres = $app.Presentations.Open($copy, -1, 0, 0)   # read-only, untitled off, no window
  $width = 1600
  $height = [int]($width * $pres.PageSetup.SlideHeight / $pres.PageSetup.SlideWidth)
  $pres.Export($out, "PNG", $width, $height)          # slides\Slide1.PNG, Slide2.PNG, ...
} finally {
  if ($pres) { $pres.Close() }
  if (-not $running) { $app.Quit() }                  # leave the owner's PowerPoint and presentations open
  [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
}
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
`set_theme_font(deck, family)` from `scripts/pptx_helpers.py` (tested; PowerPoint reads the result as the theme fonts).
Text then inherits the family everywhere, including native charts and tables; leave fonts unset on text runs. Only
equations (Cambria Math) and code blocks (the monospace family `monospace_font()` in `scripts/code_blocks.py` picks
from what is installed) set their own.

Check that the family, and the code font if the deck shows code, is installed where the slides are rendered, or the
rendered images show a substitute. On Windows (tested):

```powershell
Add-Type -AssemblyName System.Drawing
(New-Object System.Drawing.Text.InstalledFontCollection).Families.Name -contains "Calibri"
```

On macOS or Linux: `fc-list : family | grep -i "calibri"`.

## Automated audit

Needs `python-pptx`. Run `python scripts/audit_pptx.py deck.pptx --font <family>` (the deck's family; Calibri when
omitted), adding `--code-font <monospace family>` if the deck shows code. It reports, per slide:

- shapes outside the slide and overlapping shapes;
- text below 11 pt as displayed: sizes inherited from the layout, master, or deck defaults, and shrinking by autofit,
  are taken into account;
- text set in another font than the family, the equation font (Cambria Math), or the code font;
- raster images below 200 dpi as displayed, cropping and pictures in placeholders included (SVG pictures are vector and
  pass);
- empty placeholders, animations, and transitions.

For the deck it reports the theme's heading and body fonts, the fonts set on text, unused slide layouts, and the number
of native charts, native tables, and vector and raster pictures. Intended overlaps (a label placed on a map) are
reported too: confirm them on the rendered slide. It cannot see text overflow or the text inside charts: those need the
rendered slides.

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
      Cambria Math for equations and the monospace family of code blocks; all installed where the slides were rendered,
      and available on the presenting machine or embedded (say which in the report).
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
- [ ] Code: styled blocks, never screenshots: grey backdrop, label row with the source, real line numbers, syntax
      highlighting, monospace at 12 pt or more, code exactly as given; marked lines and diff colours explained, diff
      lines carry `-` and `+`; side-by-side blocks share one size and no line wraps.
- [ ] Tables: native, lightly ruled, units in headers, consistent precision, decimal-aligned numbers, only important
      values highlighted.
- [ ] Images: authentic research material, no filler imagery, resolution preserved (vector, or at least 200 dpi as
      displayed), aspect ratios kept.
- [ ] Citations next to their evidence, concise on the slide, full on a references slide; one caption style.

### File

- [ ] No animations or transitions unless asked for.
- [ ] No unused layouts (`remove_unused_layouts(deck)`), empty placeholders, hidden leftover shapes, or template
      artefacts; speaker notes kept.
- [ ] The file opens in PowerPoint without a repair prompt; everything that should be editable is.

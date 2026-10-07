---
name: technical-pptx-design
description: Design and produce an editable PowerPoint (.pptx) deck for a technical research presentation with models, data analysis, maps, charts, tables, figures, and limited mathematical notation, in a restrained academic style centred on the evidence, in an optional font family (default Calibri). Use when someone asks to build, lay out, restyle, or clean up slides for a research talk, thesis defence, conference, seminar, or lab meeting from their content, figures, data, or an existing deck, or wants a deck that does not look AI-generated. Design only; it never changes research claims, values, units, equations, or sources.
argument-hint: "[font family, default Calibri]"
---

# Technical PPTX design

Produce a clean, fully editable `.pptx` that reads as if a technically literate researcher composed it: precise,
coherent, and centred on the evidence. One strong composition per slide, generous whitespace, a small set of layouts, and
no decoration that carries no analytical meaning.

## Scope

- **You handle design:** layout, typography, colour, and the treatment of figures, charts, maps, diagrams, equations,
  tables, captions, and citations, and the quality of the file.
- **You do not change content:** research claims, values, units, equations, data, sources, or conclusions stay exactly as
  given. If something looks wrong or inconsistent (a unit mismatch, a value that differs between a chart and a table, an
  uncited figure), list it in the report; never correct it silently.
- **Titles:** you may turn a topic title into a direct subject title or a conclusion title, but only with a claim the
  slide's own evidence supports. When unsure, use the plain subject.
- **File mechanics:** if a skill or library for `.pptx` files is available (a pptx skill, `python-pptx`), use it to read
  and write the file; this skill decides how the slides look.

## Inputs

**Font family (optional, default Calibri).** Take it from the skill's argument (for example `technical-pptx-design Arial`)
or from the request ("use Arial", "set it in Aptos"). Use the family as named, even if it is not a sans-serif: it is the
owner's choice. Without one, use **Calibri**. See *Typography* for how to apply and check it.

Collect the rest before designing; ask for what is missing rather than inventing it:

- the content: an outline, speaker notes, or a draft deck;
- figures as originals: vector files (SVG, PDF, EMF) or high-resolution rasters, not screenshots;
- the data behind charts that should stay editable, and table data as values, not images;
- equations as LaTeX or another exact source;
- the citations, and the citation style if one is required;
- constraints: slide size (default 16:9, 13.333 x 7.5 in), a required template, fonts available on the presenting
  machine, talk length, and audience.

## Workflow

1. **Inventory.** For each slide, list its evidence and its message, and assign one layout from
   `references/layouts.md`. Flag gaps: low-resolution images, missing units or sample sizes, uncited figures, slides
   that try to show too much (propose a split rather than shrinking).
2. **Design system.** Define it once and apply it everywhere: the font family, grid and margins, type scale, the neutral
   background, the single accent colour, one data colour per variable or category across the whole deck, caption and
   citation styles.
   Write it down (a short style sheet in the report) before building.
3. **Master.** Build or clean the slide master: only the layouts the deck uses, no logos, footers, page furniture, or
   section labels repeated on every slide, no leftover placeholders.
4. **Compose.** Build each slide from its layout, following the element rules below.
5. **Verify.** Run every check in `references/qa-checklist.md`, including a rendered image of every slide that you look
   at, and fix before delivering.
6. **Deliver.** The `.pptx` and a short report: the style sheet, the layout of each slide, every element that is not
   editable and why, content issues found, and slides you propose to split or merge.

## Style

### Avoid

These read as AI-generated presentation aesthetics. Do not use them:

- floating rounded boxes, colour washes, decorative highlight strips;
- card grids, KPI tiles, pills, badges, tabs, or dashboard layouts;
- decorative gradients, glass effects, blobs, synthetic 3D objects, abstract technology imagery;
- icons, callouts, or infographics that add no analytical meaning;
- headers, footers, section labels, or institutional branding repeated on every slide;
- generic titles such as "Key Insights", "Unlocking Potential", or "The Road Ahead".

### Titles

- A direct subject ("Hourly cooling load, case study building") or a conclusion the slide supports ("Zoning
  simplification changes annual heating by less than 3%").
- Sentence case, no ending full stop on subject titles, one or two lines at most.
- The title slide is minimal: title, presenter, affiliation, date or venue. No imagery unless it is the research's own.

### Typography

- **One family for the whole deck:** the requested family, or Calibri by default. Set it as both the heading (major) and
  the body (minor) font of the theme, so titles, body text, charts, tables, and captions all inherit it; with Calibri,
  titles are in Calibri, not Calibri Light. Do not set a font on individual text runs, except Cambria Math for equations
  (PowerPoint's equation font) and one monospace family for code, if the deck shows code. The snippet is in
  `references/qa-checklist.md`, *Font family*.
- **Availability:** check that the family is installed on the machine that renders the slides (an uninstalled family is
  silently substituted, and the check images lie). If it is not common on presenting machines (Calibri and Arial ship
  with Office and Windows; many others do not), say so in the report and recommend embedding fonts when saving in
  PowerPoint (*File > Options > Save > Embed fonts in the file*); `python-pptx` cannot embed fonts.
- Hierarchy comes from size and weight within the one family, not from a second family.
- Deck title 36–44 pt; slide titles 27–32 pt; body 18–22 pt; figure labels, captions, and citations at least 11–14 pt,
  never smaller.
- Left-aligned text; consistent line spacing; no full justification, no all-caps paragraphs, no text effects.

### Colour

- A neutral background (white or near-white, or near-black for a dark-room venue; not both in one deck).
- One principal accent for emphasis, used sparingly; then only the data colours the evidence needs.
- Keep each variable's and each category's colour the same on every slide.
- Colourblind-conscious scales chosen by the data: sequential for magnitudes (for example viridis or cividis),
  diverging with a meaningful neutral midpoint for signed differences (for example ColorBrewer RdBu or PuOr), and
  categorical for classes (for example Okabe–Ito). Never encode meaning by colour alone where shape, label, or position
  can carry it too.

## Element rules

### Charts

- Keep charts editable (native PowerPoint charts with their data) when practical; when a chart must be an image (a
  complex plot from analysis code), use a vector format or a raster at the displayed size and at least 200 dpi, and say
  so in the report.
- Preserve axes, units, uncertainty (intervals, bands, error bars), sample sizes, baselines, and statistical meaning.
  Do not truncate an axis in a way that changes the reading, and do not drop error bars to declutter.
- Remove heavy borders, shadows, 3D effects, redundant legends (label lines directly), and unnecessary gridlines.
- Favour one readable plot over several undersized plots; split across slides rather than shrinking below legible size.

### Maps

- Treat maps as analytical figures: maximise the useful geographic area and crop away empty extent.
- Quiet basemaps (light grey or none); the data layer carries the colour.
- Distinguish missing data from zero (a hatch or a neutral "no data" colour that is not on the scale).
- Only the legend, scale bar, north arrow, insets, and labels the reading needs.
- Comparable maps share extent, projection, and colour scale, and sit side by side at the same size.

### Modelling diagrams

- Accurate and economical: every box and arrow is a real input, parameter, state, calculation, or output of the model.
- Distinguish the kinds of node consistently (for example by shape or line style, explained once): observed inputs,
  parameters, states, calculations, outputs.
- Directional connectors that mean "flows into" or "is computed from"; no decorative arrows, no crossing lines that a
  better arrangement avoids.
- Left-to-right or top-to-bottom reading order; align nodes to the grid.

### Equations

- Proper mathematical notation: italic variables, upright units and operators, correct sub- and superscripts.
- Prefer native PowerPoint equations (editable). When they cannot be produced reliably, insert a vector render of the
  exact source and keep the LaTeX in the speaker notes; say so in the report.
- Align related expressions on the relation sign; define every symbol nearby, with units; keep the mathematical
  definition separate from its interpretation in words.
- No decorative boxes around equations.

### Tables

- Native, editable tables; never images of tables and never card grids.
- Light rules (a top and bottom rule and one under the header; no vertical rules); no fills except to mark the few
  analytically important values.
- Units in the column headers; consistent decimal precision per column; numbers right-aligned or aligned on the decimal
  point; text left-aligned.
- Split or move to an appendix slide rather than shrinking text below the minimum size.

### Imagery

- Prefer authentic technical material: maps, simulation outputs, geometry, schematics, field photographs, experimental
  setups.
- Never add generic stock or AI-generated imagery to fill space.
- Preserve resolution: do not upscale; crop instead of distorting; keep aspect ratios.

### Captions and citations

- Each citation sits with the evidence it supports (under the figure or table, or after the claim), in a concise form
  ("Author et al., 2024") with the full reference on a references slide.
- One caption style throughout: what the figure shows, the data source, and units if not on the axes.
- No large footer repeated on every slide.

### Animation and delivery

- No animations or transitions by default; add a build only when the reasoning needs a step-by-step reveal and the
  owner asks for it.
- A clean, fully editable `.pptx`: legible figures, preserved image resolution, no overlaps or text overflowing its box,
  no unused layouts, placeholders, or template artefacts, speaker notes kept.

## References

- `references/layouts.md`: the grid and the seven layouts, with geometry for a 16:9 slide.
- `references/qa-checklist.md`: rendering every slide, automated checks, and the delivery checklist.

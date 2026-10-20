# Pitfalls

Failures met while aligning an application's UI, with their causes and fixes. Most come from aligning a React workbench
(FlexLayout, AG Grid, ECharts, MapLibre, React Flow) with the EnergyAtlas documentation family.

## Precedence and scope

- **The reference silently overrides the app's own rules.** A documentation-site reference rules every section; an
  app's guidelines may ask for fewer borders and two or three type sizes. List every conflict in the translation table
  and get a decision per conflict before styling; record it.
- **Editing an owner-maintained document.** Some projects mark their design guidelines as maintained by the owner only.
  Record decisions in a decision record or the alignment record, and write the amendments the guidelines would need
  there for the owner.
- **Behaviour changes ride along.** A restyle that also renames a command, reorders a menu, or changes a shortcut breaks
  tests and muscle memory. Keep them out; list them as follow-ups.
- **The record is committed before implementation disproves it.** Decisions on header case, tracking, and which
  notices get edges change once they are seen. Mark the first commit as decided before implementation and keep a
  deviations section that the last commit fills.

## Labels and density

- **Uppercase changes what units say.** `text-transform: uppercase` renders `Floor area (m²)` as `FLOOR AREA (M²)`,
  `MWh` as `MWH`, `kVA` as `KVA`. Chart titles, legend titles, grid headers, and row headers often carry units, names,
  or values; keep them as written, or wrap the unit in a child with `text-transform: none`. Read the audit's uppercase
  list for them.
- **Mono caps widen labels past the minimum width.** Uppercase semibold labels at the small size are about
  10 % wider than sentence-case sans; with tracking, the last page tab left the centre tab strip at 1280 px with both
  side panels open. Measure the tab bars' `scrollWidth` before and after at the minimum size and trade tracking
  (0.04–0.06 em) and padding until they fit as before.
- **Mono caps grid headers truncate.** Headers ellipsize at the app's column widths ("YEAR BU…"). Enable header
  wrapping (AG Grid `wrapHeaderText`, `autoHeaderHeight`) and tighten tracking rather than widening columns.
- **Mono caps labels wear on the owner.** In the trial the owner chose the reference-wins variant but found its mono
  uppercase tab titles and header labels tiresome once they used it, and kept the rest. Default to labels as written in
  the interface sans, put the label style in tokens so it changes in one place, and show the opt-in on the running app.
- **Label styles hard-coded rule by rule.** Thirty-five label rules each setting `font-family: var(--font-mono)` and
  `text-transform: uppercase` turned a one-word decision into a sweep across twelve stylesheets. Every label rule reads
  the label tokens.

- **Titles turned into labels.** The first build made every page and panel title a raised strip with a muted, small
  label. Titles carry hierarchy; the owner wanted them back as they were. Restyle labels, not titles, unless asked.

## Tokens and themes

- **The reference's surfaces land on the wrong app roles.** Mapping the reference's first surface onto the token named
  `surface` puts every dark pane on `#1a1a1a` and leaves the near-black base in the gutters, the opposite of the
  reference. Map by use: panes take the reference's base (`translation.md`, "Surfaces").
- **The family's interactive border fails on its own raised surface.** Dark `#6b6b6b` is 2.69:1 on `#2a2a2a`, and
  controls sit on raised surfaces in apps (toolbars, forms). Test `border-interactive` on every surface; `#747474`
  passes.
- **Tone colours fail on their own tints.** The family's dark success and danger, and light success and warning, drop
  below 4.5:1 on 10–18 % tints. Test tone text on its tint and on raised surfaces, then adjust the tone or lighten the
  tint (`contrast.py --suggest` gives both).
- **The inverted active tab fails its own outline.** An accent outline drawn on a text-coloured fill measures 2.08:1 in
  the family dark, 2.50:1 in the light, and 1:1 where the accent equals the text colour (monochrome themes). Draw it
  inset as two shadows, `inset 0 0 0 1px var(--accent), inset 0 0 0 3px var(--strip)`, so the outline sits on the strip
  colour behind a gap, and test the accent against the strip.
- **Shadows vanish on black.** On a `#000000` pane a menu's shadow is invisible; menus, popovers, and dialogs need a
  lighter overlay surface and a rule edge in the darkest theme.
- **Canvases keep the old theme.** Charts and maps draw resolved colours once. Re-render them on every theme change and
  after the web font loads; a `var(--token)` string inside a chart option is not a colour.
- **Custom properties read back as declared.** `getPropertyValue('--font-size-small')` returns `0.75rem`, not `12px`,
  so canvas renderers and numeric grid parameters cannot read sizes from CSS; take them from the token module.
- **The default theme flashes on reload.** The stored theme is applied after the app boots. Apply it before the first
  paint (an inline script) or give the CSS a media-query fallback for the system preference.
- **A dev server has no stylesheet in the first frame.** Vite and other bundlers inject CSS from JavaScript in
  development, so a first-frame check against the dev server always reads an unstyled page. Check the production build
  with the app script held back (`verification.md`).
- **Portals miss the theme.** Menus, tooltips, and toasts rendered into `document.body` outside the themed element keep
  the fallback tokens; put the theme attribute and tokens on `<html>`.
- **Colours derived from tokens collapse when two tokens get one value.** A map style recoloured from chrome roles
  (roads from the pane surface, land from the background) lost its roads when the restyle gave panes and gutters the
  same black. Before giving two roles one value, grep where each is read, derived renderers included, and give the
  derived colours their own tokens if needed.
- **A stored preference hides the default.** The app remembers the last theme; clear its storage key before judging the
  default for a system preference.

## Libraries

- **A library's hover reuses the selected colours.** FlexLayout's hover rule sets an unselected tab's label to the
  selected-tab colour. After the selected tab was inverted, that colour was the strip's own, so a hovered side handle
  turned into an empty box. Override hover explicitly for every interactive kind and measure it (`verification.md`,
  "States").
- **Transitions on selection fail accessibility checks.** A 150 ms colour transition on the tab base rule made axe sample
  a tab halfway between selected and unselected (2.6:1). Fade only the hover; selection changes at once.
- **Libraries hard-code radii, focus glows, and transitions.** FlexLayout (tabs, popups, drag rectangles), MapLibre
  (control groups, a fixed blue focus glow), and ECharts (bars, tooltips) round corners with literal values; FlexLayout's
  splitter hover sets its own transition. Override each one, list the overrides in the record, and run
  `style_audit.py` on the library's stylesheet to find them.
- **A docking library's font variable is the content font.** FlexLayout's `--flexlayout-font-family` styles every pane;
  setting it to the mono turns all content mono. Style the tab buttons instead.
- **Making a translucent library surface opaque exposes its hard-coded colours.** React Flow's attribution was
  translucent, so axe could not measure its `#999` link; on an opaque surface it measured 2.84:1 and failed. Re-run
  axe after theming a library's backgrounds.
- **Numeric theme parameters do not take variables.** Data-grid font sizes and heights are numbers, and prefixed keys
  (`headerFontSize`) are easy to miss; use the token module's pixel value and change both together.
- **Map labels ignore the web font.** They come from glyph files named in the style; accept the basemap's font or
  generate glyphs.

## Verification

- **Verification snippets lie on some libraries.** ECharts canvases are transparent (a corner pixel is `rgba(0 0 0 0)`
  in every theme); AG Grid shows cell focus with a border, not an outline; visually hidden labels look clipped, and
  ellipsized headers look fine. Use the snippets in `verification.md` and confirm doubtful cases by screenshot.
- **Network stubs hide the real basemap.** Browser-test fixtures that stub map tiles keep screenshots offline, but the
  map then shows a plain background, so a restyle of the basemap is never seen. Take at least one screenshot per theme
  of the map with the real tiles.
- **Empty screenshots hide the restyle.** Without data, grids, charts, tiles, and legends do not render. Build a
  populated state once (a setup project and `storageState`) and reuse it.
- **A screenshot matrix in one file runs serially.** Playwright runs the tests of one file in one worker unless the file
  or config is parallel; a theme × size × surface matrix then takes many minutes. Set `mode: 'parallel'`.
- **`addInitScript` runs on every navigation.** A storage write in it resets the app's own changes on reload; guard it
  with a `sessionStorage` flag.

## Tooling

- **A harness outside the repository cannot import the app's fixtures.** Playwright resolves `@playwright/test` and the
  app's fixture (network stubs) from the repository. Put the harness in an ignored folder inside it, or link the
  repository's `node_modules` next to it.
- **Deleting a junction can delete its target.** A harness folder that links the repository's `node_modules` with a
  junction, removed with a recursive delete, can empty the repository's `node_modules`. Remove the junction itself
  (`rmdir <link>` on Windows) before deleting the folder.
- **Local-only files break the project's checks.** ESLint with typed linting reports any `.ts` outside a tsconfig, and
  `prettier --check .` scans untracked files; keep local configs and harnesses in ignored folders or pass ignore
  patterns, and do not commit them.
- **Browser tests time out when the dev server is cold.** Heavy pages (maps, grids, charts) starve a dev server under
  many parallel workers; cap the workers as the project does.
- **Two checkouts share a port.** A second worktree's tests reuse the first one's dev server (`reuseExistingServer`) and
  test the wrong code. Give each checkout its own port.
- **Stopping a background dev server on Windows can leave it running.** Ending the shell does not always end
  `node vite.js`; find the process on the port (`Get-NetTCPConnection -LocalPort <port>`) and stop it.
- **Line endings.** On Windows with `core.autocrlf=true`, a formatter that checks LF reports every file, and Python's
  `write_text` writes CRLF; respect the project's `.gitattributes` and write with `newline="\n"` (or bytes).
- **Vendored licence texts carry trailing spaces.** `git diff --check` flags them; keep the licence byte-identical and
  record the exception.

# Pitfalls

Failures met while aligning an application's UI, with their causes and fixes.

## Precedence and scope

- **The reference silently overrides the app's own rules.** A documentation-site reference rules every section; an
  app's guidelines may ask for fewer borders and two or three type sizes. List every conflict in the translation table
  and get a decision per conflict before styling; record it.
- **Editing an owner-maintained document.** Some projects mark their design guidelines as maintained by the owner only.
  Record decisions in a decision record or the alignment record; propose guideline changes in the report instead.
- **Behaviour changes ride along.** A restyle that also renames a command, reorders a menu, or changes a shortcut breaks
  tests and muscle memory. Keep them out; list them as follow-ups.

## Tokens and themes

- **Canvases keep the old theme.** Charts and maps draw resolved colours once. Re-render them on every theme change and
  after the web font loads; a `var(--token)` string inside a chart option is not a colour.
- **The default theme flashes on reload.** The stored theme is applied after the app boots. Apply it before the first
  paint (inline script) or give the CSS a media-query fallback for the system preference.
- **Portals miss the theme.** Menus, tooltips, and toasts rendered into `document.body` outside the themed element keep
  the fallback tokens; put the theme attribute and tokens on `<html>`.
- **A stored preference hides the default.** The app remembers the last theme; clear its storage key before judging the
  default for a system preference.

## Shapes and focus

- **Outlines vanish in tab strips.** Tab bars and scroll containers clip overflow, so an outer outline or a focus ring
  with a positive offset is cut. Draw the active-tab outline and focus rings inset.
- **Uppercase mono everywhere.** Uppercase tracked labels read well on a few tabs and headers; on every button and menu
  item they slow scanning and widen labels until they clip at the minimum width. Limit them to tab strips, panel
  headers, and table headers.

## Libraries

- **Numeric theme parameters do not take variables.** Data-grid font sizes and heights are numbers; use the token's pixel
  value and change both together.
- **Map labels ignore the web font.** They come from glyph files named in the style; accept the basemap's font or
  generate glyphs.

## Tooling

- **Browser tests time out when the dev server is cold.** Heavy pages (maps, grids, charts) starve a dev server under
  many parallel workers; cap the workers as the project does.
- **Line endings.** On Windows with `core.autocrlf=true`, a formatter that checks LF reports every file; respect the
  project's `.gitattributes` rather than reformatting.

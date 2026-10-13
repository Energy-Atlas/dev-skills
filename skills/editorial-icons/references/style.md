# Style

The family should read like the restrained editorial illustrations of a print publication or of Anthropic's Claude: a
confident pen line, a few marks, a lot of air, and one quiet colour accent. It should never read like a doodle, a
cartoon, or a geometric icon kit.

## The line

- **Ink strokes, not geometric strokes.** Every line is a filled outline whose width swells by about 10% along its length
  and tapers at loose ends (`taper=(start, end)` as fractions of the width). Closed shapes are drawn as one stroke that
  overlaps its start slightly (`overshoot` 0.8-0.9, or an arc span past 360 degrees), the way a hand closes a loop.
- **A slight wobble.** The centreline is displaced by low-frequency noise of about 0.09 grid units (`WOBBLE`). More reads
  as shaky or childish; less reads as vector geometry.
- **Weight.** Regular 1.3 and bold 1.85 grid units on the 24-unit canvas (`references/weights.md`). Rings and fine details
  a little lighter (`weight=0.95`, `0.8-0.85`).
- **Ends.** Round caps. Sharp corners only where the subject has them, for example an arrowhead (`spline=False`).

## The composition

- **Minimal detail.** Two to five marks per icon. A subject that needs more is the wrong metaphor, or a logo that has to
  be literal (keep it, and accept a denser icon).
- **Generous negative space.** Keep marks apart where they are not meant to touch: a line that runs into a ring turns
  two ideas into a hook or a chain. Leave a visible gap (about 0.8 units plus the stroke widths) between separate marks.
- **Consistent optical size.** The family shares the canvas (24 x 24) and an optical bounding box of about 2.5-21.5;
  balance heavy subjects (rings, blocks) against light ones (arrows, brackets) by eye in the preview, not by bounding box.
- **One accent per icon**: a dot, a needle, a ribbon, a slash, one filled block. It marks the point of the icon - the
  destination, the north, the bookmark - not decoration.

## Colour roles

| Role | Standalone file | On a themed site |
| --- | --- | --- |
| Ink | warm charcoal `#3b3631` (or the site's text colour) | `fill: currentColor`, so the icon takes the text colour of its row in every theme |
| Accent | the site's accent, or muted terracotta `#c2704f` by default | the theme's accent token, for example `fill: var(--ui-accent)` |

- Write the colours into the files (`INK`, `ACCENT` in the module) so the SVGs stand alone, and keep the two groups so a
  site can override them with CSS.
- On a dark theme a charcoal ink disappears: a themed site must recolour the ink. Check both themes.
- The accent is a colour role of the site's palette, not a new brand colour: align it with the theme's accent unless the
  owner chooses otherwise. If it is a colour the site reserves for a state (red for errors), pick another.
- A faint backdrop copy of an icon (cards, heroes) uses one colour for both groups at low opacity (12-16%).

## Avoid

- Cartoonish doodles, exaggerated wobble, scribble fills, hatching, grain, and texture.
- Gradients, shadows, glows, and outlines around fills.
- Generic icon-kit geometry: perfect circles at constant width, uniform 2 px strokes, mitred corners.
- More than one accent mark (except a two-tone logo), and accents that only decorate.
- Text inside icons, except the few characters a subject is made of (`< / >`).

# Worked example: the EnergyAtlas Wiki subspace icons

Eight icons for the subspaces of the EnergyAtlas Wiki, a custom-themed MkDocs site with a light and a dark theme.

- `icons.py`: the icon module (the source).
- `svg/`: the rendered files, `<name>.svg` (regular, 1.3) and `<name>-bold.svg` (bold, 1.85); ink `#3b3631`, accent
  `#125dae`. Render them again with
  `python scripts/ink_icons.py references/examples/energyatlas-subspaces/icons.py --out <folder>`; the repository's tests
  check that the result matches `svg/` byte for byte.

## Where they appear

| Place | Size | Weight | Colours |
| --- | --- | --- | --- |
| Sidebar subspace dropdown (current and options) | 26 px | bold | ink = the row's text colour, accent = the theme's accent |
| Welcome page cards, above each title | 40 px | regular | ink = primary text, accent = the theme's accent |
| Card hover backdrop | 105% of the card, 14% opacity, centred at 70% / 72% | regular | both groups in the accent |

The theme includes the bold files from a Jinja macro; a Markdown hook replaces
`<span class="ui-icon" data-icon="..."></span>` on the Welcome page with the regular file and its backdrop copy
(`references/integration.md`).

## Subjects

| Icon | Drawing | Accent |
| --- | --- | --- |
| `quick-start` | compass ring, drawn south needle | north needle |
| `workflows` | open ring, curved arrow | the node it points to |
| `architecture` | two outlined blocks on branching lines | the third block, filled |
| `python` | the Python logo from rounded strokes, upper snake | lower snake |
| `web-api` | `<` and `>` | the slash |
| `library` | an upright book and a leaning one | the middle book, filled |
| `user-stories` | head and shoulders | speech bubble |
| `wiki-guide` | open book and spine | ribbon |

## How it got there

The rounds of owner feedback, each a lesson now in `references/pitfalls.md`:

1. Pilot `workflows`: a ring and a wandering route read as a worm; a ring joined to the line read as a hook; stations
   on the line read as chain links. Settled: ring, one calm S, an accent destination; approved with "align colour with
   the theme".
2. The set: `library` (three outlined spines on a shelf) was too dense, `python` (a snake) read as a "2"; redrawn.
3. On the site: terracotta accents became the theme's blue; the sidebar icons grew to 26 px and were still too thin, so
   the bold weight was added for small sizes while the cards kept the regular one.
4. `workflows` again, "like a git merge": a single trunk with one branch read as a stick figure kicking a ball; a
   two-commit merge read correctly, but the owner then chose node, curved arrow, node. `python` became the language's
   logo instead of the animal.

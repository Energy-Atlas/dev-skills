# Integration

Include the icons **inline**, not as `<img>`: only inline SVG lets CSS recolour the `.ink` and `.accent` groups, so the
icons follow the theme. Keep the rendered files in one folder and include them from there; never paste their paths
into pages by hand.

## CSS colour coding

```css
.icon { display: inline-flex; width: 20px; height: 20px; flex: 0 0 20px; }
.icon svg { width: 100%; height: 100%; display: block; }
.icon .ink { fill: currentColor; }          /* the text colour of the row, in every theme */
.icon .accent { fill: var(--ui-accent); }   /* the theme's accent */
```

CSS overrides the `fill` attributes written into the files. Size per place, and pick the weight per size
(`references/weights.md`): for example 26 px bold in a dropdown, 20 px bold in a sidebar, 40 px regular on a card.

## MkDocs with a custom theme (Jinja)

Put the SVGs in the theme folder, for example `theme/icons/<set>/`, and include them from a macro. MkDocs also publishes
the theme's static files, so the standalone SVGs are downloadable at `icons/<set>/`.

```jinja
{% set space_icons = {'Quick Start': 'quick-start', 'Workflows': 'workflows'} %}
{% macro render_icon(title) %}
    {% set slug = space_icons.get(title) %}
    {% if slug %}
        <span class="icon icon-{{ slug }}" aria-hidden="true">{% include 'icons/subspaces/' ~ slug ~ '-bold.svg' %}</span>
    {% endif %}
{% endmacro %}
```

`mkdocs serve` does not notice a changed included SVG: restart it after rendering again.

## MkDocs with Material

Put the SVGs under `overrides/icons/<set>/` (the `custom_dir`) and include them the same way from a template override,
for example a partial you extend. For page content use the hook below.

## Icons in Markdown pages (an MkDocs hook)

Pages write a placeholder; a hook replaces it at build time with the inline SVG, so pages stay readable and icons stay
single-source.

```markdown
-   <span class="ui-icon" data-icon="workflows"></span>[Workflows](workflows/index.md)
```

```python
# hooks/icons.py  (mkdocs.yml: hooks: [hooks/icons.py])
import re
from functools import lru_cache
from pathlib import Path

ICON_DIR = Path(__file__).resolve().parents[1] / "theme" / "icons" / "subspaces"
PLACEHOLDER = re.compile(r'<span class="ui-icon" data-icon="([a-z0-9-]+)"></span>')


@lru_cache(maxsize=None)
def icon_svg(name):
    return (ICON_DIR / f"{name}.svg").read_text(encoding="utf-8").strip()


def on_page_content(html, page, config, files):
    def render(match):
        svg = icon_svg(match.group(1))
        return (f'<span class="ui-icon ui-icon-{match.group(1)}" aria-hidden="true">{svg}</span>'
                f'<span class="ui-card-backdrop" aria-hidden="true">{svg}</span>')
    return PLACEHOLDER.sub(render, html)
```

The second copy is the optional card backdrop below; drop it if the site does not use one. A missing icon file fails the
build, which is what `mkdocs build --strict` should do.

## Cards with an icon and a hover backdrop (optional)

On an overview grid of clickable cards, each card can show its icon (regular weight, about 2.5rem) above the title, and on
hover a soft accent gradient with a faint, oversized copy of the icon, cropped by the card:

```css
.cards > ul > li { position: relative; overflow: hidden; isolation: isolate; }
.cards > ul > li::before {                      /* the gradient wash */
  content: ""; position: absolute; inset: 0; z-index: -1; opacity: 0;
  background: linear-gradient(140deg, transparent 30%, color-mix(in srgb, var(--ui-accent) 16%, transparent));
  transition: opacity 180ms ease;
}
.cards .ui-icon { display: block; width: 2.5rem; height: 2.5rem; margin-bottom: 1rem; }
.cards .ui-icon .ink { fill: var(--ui-text-primary); }
.cards .ui-icon .accent, .cards .ui-card-backdrop :is(.ink, .accent) { fill: var(--ui-accent); }
.cards .ui-card-backdrop {                      /* the faint, oversized icon */
  position: absolute; left: 70%; top: 72%; z-index: -1; width: 105%; aspect-ratio: 1;
  transform: translate(-50%, -50%); opacity: 0; pointer-events: none; transition: opacity 180ms ease;
}
.cards > ul > li:is(:hover, :focus-within)::before { opacity: 1; }
.cards > ul > li:is(:hover, :focus-within) .ui-card-backdrop { opacity: 0.14; }
```

Tune the backdrop's size (`width`, 100-175% of the card) and centre (`left`/`top`, about 70-80% / 72-85%) with the owner:
larger and further out reads as decoration, smaller and closer to the centre shows more of the drawing. If the title
link is stretched over the card with `a:only-child::after`, change it to `a:only-of-type::after`: the icon span is now
its sibling. For Material for MkDocs `grid cards`, the full recipe is in the wiki-ui-alignment skill
(`references/material-recipes.md`, "Icon cards").

## Record it

Add to the project's design spec: the subjects, the weights and where each is used, the colour roles, the generator's
location, and "edit the generator, not the SVGs". Add the same rule to the agent instructions (`AGENTS.md`).

# Intake questions

Ask the questions the inputs leave open, each with a recommendation. Record every answer in section 0 of the spec
(`spec-decisions-template.md`). Questions marked *blocking* change what you build; ask them before implementing. The
others have a sensible default: state it and go ahead unless the owner objects.

## Blocking

1. **Reference UI.** The spec names a reference; is it attached? If it is a screenshot, may it be committed to the
   repository? If not, it will be described in words in the spec.
2. **Brand.** Is this a visual-family alignment (keep the site's name, logo, favicon) or a rename? Is there an official
   logo or favicon to use? *Default: alignment, keep the identity.*
3. **Palette source of truth.** Is the spec's palette final, or should the live sister site's CSS be authoritative? What is
   its URL? Where are the semantic state colours (success, warning, error, info), which specs often omit?
   *Default: the live CSS is authoritative; contrast fixes override it.*
4. **Default theme.** Follow the system preference with the toggle, or force one scheme? *Default: system preference; the
   dark theme gets the strongest expression of the reference, but is never forced.*
5. **Fonts.** Load from a font host at runtime, or self-host? *Default: self-host; no runtime request to any font host.*
6. **Landing page.** A real hero (large headline, an editorial serif phrase, short copy) or only a restyle of the existing
   cards? If a hero, what is the headline, and which phrase gets the serif? *Default: a restrained hero followed
   immediately by the shared-border grid; not a marketing page.*
7. **Numbered section strips** (`01 / SECTION`): on which pages? *Default: the landing page, section index pages, and other
   deliberately designed overview pages; never automatic on every `##` of ordinary pages.*

## Defaults to confirm

8. **Contrast.** Adjust spec colours that fail WCAG AA (give the ratios), split decorative and interactive borders, and
   use a deep brand colour that fails on dark only as a fill. *Default: yes.*
9. **Width.** Cap long-form prose at a readable measure (about 760–900 px), but exempt reference pages, diagrams, data
   matrices, and wide tables; wide tables scroll inside their own container. *Default: yes.*
10. **Breadcrumbs.** Turn on `navigation.path`, styled as small muted mono labels with no bar. *Default: yes.*
11. **Red.** Restrict the brand's red to error, destructive, and failure states; amber for warnings, green for success, blue
    for links, navigation, information, and active states. *Default: yes.*
12. **Agent rule.** Add a rule to `AGENTS.md` (or equivalent) that UI changes follow the spec. *Default: yes.*
13. **Header in light mode.** A reference with a dark header may look heavy on a light page; use the page background with a
    bottom rule in light mode? *Default: yes, and say so in the report.*

## Questions that come up later

- **Tagging.** If the project reserves `v<version>` tags for releases, a redesign merge is not one: ask whether to tag and
  with what name, or not at all.
- **Hidden sidebars.** A page that hides its sidebars looks stretched; keep their widths as empty margins (no rules), so
  its text lines up with other pages? *Default: yes; strips and grid rules still run frame to frame, and grids draw their
  own outer edges at the margins.*
- **Clickable cells.** Should a cell whose title is a link be clickable as a whole? *Default: yes, with inner links keeping
  their own targets.*

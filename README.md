# dev-skills

Reusable agent skills for the development work of the Energy Atlas organisation. Each skill is a folder of Markdown: a
`SKILL.md` with a `name` and a `description` in its front matter, which tell an agent when to use it, and a
`references/` folder that the skill loads only when a step needs it.

## Skills

| Skill | Use it to |
| --- | --- |
| [`wiki-ui-alignment`](skills/wiki-ui-alignment/SKILL.md) | Restyle an MkDocs (Material for MkDocs) documentation site to a reference UI and a brand palette: intake questions, a recorded design spec, tokens and contrast, self-hosted fonts, Material CSS recipes, browser verification, and merging, and the EnergyAtlas mark as logo and favicon when the owner chooses it. |
| [`app-ui-alignment`](skills/app-ui-alignment/SKILL.md) | Restyle a web application (shell, docked panels, controls, data grids, charts, maps, dialogs) to a reference UI and a brand palette: a scripted styling audit, the owner's decisions on every conflict with the app's own design rules, a recorded spec, tokens with a contrast test for every theme, third-party theming, and browser verification, and the EnergyAtlas mark as logo and favicon when the owner chooses it. |
| [`technical-pptx-design`](skills/technical-pptx-design/SKILL.md) | Design an editable `.pptx` for a technical research presentation (models, data analysis, maps, charts, tables, equations, code, pseudocode) in a restrained academic style and an optional font family (default Calibri), without changing any research content: layouts on a grid, element rules, rendering every slide, `python-pptx` helpers, and an automated audit. |
| [`editorial-icons`](skills/editorial-icons/SKILL.md) | Design and generate a coherent family of hand-drawn, editorial SVG icons with a seeded ink-stroke script: a regular and a bold weight for large and small sizes, ink and accent groups a site can theme, a pilot approved by the owner, validation through the `custom-icons` skill, optional sketches with the `draw` plugin (both installed when missing), and inline site integration with optional icon cards. |

## Layout

```text
skills/
  <skill-name>/
    SKILL.md          when to use the skill and its workflow
    references/       details loaded on demand: templates, recipes, checklists
    scripts/          code the skill runs or imports (optional)
tests/
  <skill-name>/       regression tests for a skill's scripts (not installed with the skill)
```

## Install

Install with the [`skills`](https://github.com/vercel-labs/skills) CLI through `npx`; it needs Node.js and reads the
skills straight from this repository.

See which skills the repository offers:

```bash
npx skills add energy-atlas/dev-skills --list
```

Install a skill for every project on the machine (`-g`), for Claude Code (`-a claude-code`):

```bash
npx skills add energy-atlas/dev-skills --skill wiki-ui-alignment -g -a claude-code
```

Leave out `-g` to install it into the current project's `.claude/skills/` instead, so it is committed with the project.
Leave out `-a claude-code` to choose the agents interactively.

On Windows, add `--copy`: the CLI links installed skills by default, and Windows refuses symbolic links unless developer
mode is on.

```bash
npx skills add energy-atlas/dev-skills --skill wiki-ui-alignment -g -a claude-code --copy
```

Update installed skills after this repository changes:

```bash
npx skills update -g
```

## Adding a skill

- One folder per skill under `skills/`, named in kebab case; the folder name equals the `name` in its front matter.
- Write the `description` for the agent that decides whether to load the skill: what it does and the requests that should
  trigger it.
- Keep `SKILL.md` to the workflow and the rules; move long recipes and templates to `references/` and code to
  `scripts/`, with tests for that code under `tests/<skill-name>/` (run them with `python -m pytest tests`).
- Keep skills free of credentials, personal paths, and private repository links.
- Give the skill its page on the site in the same change (see *Site*).
- Commits: `type(scope): imperative summary in lower case`, with the types `feature`, `fix`, `refactor`, `test`, `docs`,
  `build`, `chore`, `perf` and the skill name as the scope, for example `feature(wiki-ui-alignment): ...`; `site` is
  the scope for the site.

## Site

[energy-atlas.github.io/dev-skills](https://energy-atlas.github.io/dev-skills/) has a landing page with the install and
update commands, and one page per skill. Its sources are `mkdocs.yml`, `docs/`, and `overrides/`; `design/` holds its UI
specification and the skill-page template and is not published.

- UI and styling changes follow [`design/ui-design-spec.md`](design/ui-design-spec.md); its section 0 wins over the
  rest.
- Each skill page follows [`design/skill-page-template.md`](design/skill-page-template.md). A new skill gets its page
  and an entry in the `nav` of `mkdocs.yml`.
- Build it with `mkdocs build --strict`, or serve it with `mkdocs serve`, from the repository root, with the packages of
  `requirements-docs.txt` in a virtual environment outside the repository.
- `.github/workflows/pages.yml` builds every push to `feature/mkdocs-site` and `main` and every pull request, and
  deploys only pushes to `main`; the `github-pages` environment accepts no other branch. Site work happens on
  `feature/mkdocs-site` and reaches `main` only by a merge the owner has approved.

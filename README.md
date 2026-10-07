# dev-skills

Reusable agent skills for the development work of the Energy Atlas organisation. Each skill is a folder of Markdown: a
`SKILL.md` with a `name` and a `description` in its front matter, which tell an agent when to use it, and a
`references/` folder that the skill loads only when a step needs it.

## Skills

| Skill | Use it to |
| --- | --- |
| [`wiki-ui-alignment`](skills/wiki-ui-alignment/SKILL.md) | Restyle an MkDocs (Material for MkDocs) documentation site to a reference UI and a brand palette: intake questions, a recorded design spec, tokens and contrast, self-hosted fonts, Material CSS recipes, browser verification, and merging. |

## Layout

```text
skills/
  <skill-name>/
    SKILL.md          when to use the skill and its workflow
    references/       details loaded on demand: templates, recipes, scripts, checklists
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
- Keep `SKILL.md` to the workflow and the rules; move long recipes, templates, and scripts to `references/`.
- Keep skills free of credentials, personal paths, and private repository links.
- Commits: `type(scope): imperative summary in lower case`, with the types `feature`, `fix`, `refactor`, `test`, `docs`,
  `build`, `chore`, `perf` and the skill name as the scope, for example `feature(wiki-ui-alignment): ...`.

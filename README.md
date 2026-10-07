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

Copy a skill folder into a skills directory that Claude Code reads.

For every project on a machine (user level), in Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force skills\wiki-ui-alignment "$HOME\.claude\skills\"
```

On macOS or Linux:

```bash
mkdir -p ~/.claude/skills && cp -R skills/wiki-ui-alignment ~/.claude/skills/
```

For one project only, copy it into that project's `.claude/skills/` instead. Copy again after pulling a new version of
this repository; a copied skill does not update itself.

## Adding a skill

- One folder per skill under `skills/`, named in kebab case; the folder name equals the `name` in its front matter.
- Write the `description` for the agent that decides whether to load the skill: what it does and the requests that should
  trigger it.
- Keep `SKILL.md` to the workflow and the rules; move long recipes, templates, and scripts to `references/`.
- Keep skills free of credentials, personal paths, and private repository links.
- Commits: `type(scope): imperative summary in lower case`, with the types `feature`, `fix`, `refactor`, `test`, `docs`,
  `build`, `chore`, `perf` and the skill name as the scope, for example `feature(wiki-ui-alignment): ...`.

---
hide:
  - navigation
  - toc
---

<div class="ea-hero" markdown>

# EnergyAtlas<br>*dev-skills*

Skills for the development across the EnergyAtlas ecosystem.

</div>

## Install { .ea-strip data-index="01" data-note="npx skills" }

Skills install with the [`skills`](https://github.com/vercel-labs/skills) command-line tool through `npx`. It needs
Node.js and reads the skills straight from the [repository](https://github.com/Energy-Atlas/dev-skills).

See which skills the repository offers:

```bash
npx skills add energy-atlas/dev-skills --list
```

Install a skill for every project on the machine (`-g`), for Claude Code (`-a claude-code`):

```bash
npx skills add energy-atlas/dev-skills --skill wiki-ui-alignment -g -a claude-code
```

Leave out `-g` to install it into the current project's `.claude/skills/` instead, so that it is committed with the
project. Leave out `-a claude-code` to choose the agents interactively.

On Windows, add `--copy`: the tool links installed skills by default, and Windows refuses symbolic links unless developer
mode is on.

```bash
npx skills add energy-atlas/dev-skills --skill wiki-ui-alignment -g -a claude-code --copy
```

## Update { .ea-strip data-index="02" data-note="After each change" }

Update installed skills after the repository changes:

```bash
npx skills update -g
```

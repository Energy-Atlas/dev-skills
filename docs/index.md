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

Install with the [`skills`](https://github.com/vercel-labs/skills) CLI; it needs Node.js.

List the skills:

```bash
npx skills add energy-atlas/dev-skills --list
```

Install one for all projects (`-g`) in Claude Code (`-a claude-code`):

```bash
npx skills add energy-atlas/dev-skills --skill wiki-ui-alignment -g -a claude-code
```

Without `-g`, it installs into the current project only; without `-a`, it asks which agents.

On Windows, add `--copy`, since symbolic links need developer mode:

```bash
npx skills add energy-atlas/dev-skills --skill wiki-ui-alignment -g -a claude-code --copy
```

## Update { .ea-strip data-index="02" data-note="After each change" }

Update installed skills after the repository changes:

```bash
npx skills update -g
```

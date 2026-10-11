---
hide:
  - navigation
  - toc
---

<div class="ea-hero" markdown>

# EnergyAtlas<br>*dev-skills*

Reusable agent skills for the development work of the EnergyAtlas organisation. Each skill is a folder of Markdown that
tells a coding agent such as Claude Code how to carry out one kind of task, and installs with one command.

</div>

## Skills { .ea-strip data-index="01" data-note="One page each" }

<div class="grid cards" markdown>

-   [wiki-ui-alignment](skills/wiki-ui-alignment.md)

    Restyle an MkDocs (Material for MkDocs) documentation site to a reference UI and a brand palette: intake questions,
    a recorded design spec, tokens and contrast, self-hosted fonts, browser verification, and merging.

    [Open the skill](skills/wiki-ui-alignment.md){ .md-button }

-   [technical-pptx-design](skills/technical-pptx-design.md)

    Design an editable `.pptx` for a technical research presentation in a restrained academic style, without changing
    any research content: layouts on a grid, element rules, rendering every slide, and an automated audit.

    [Open the skill](skills/technical-pptx-design.md){ .md-button }

</div>

## Install { .ea-strip data-index="02" data-note="npx skills" }

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

## Update { .ea-strip data-index="03" data-note="After each change" }

Update installed skills after the repository changes:

```bash
npx skills update -g
```

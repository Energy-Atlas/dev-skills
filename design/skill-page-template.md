# Skill page template

Every skill has one page on the site, `docs/skills/<skill-name>.md`, written by hand in this format
(`ui-design-spec.md`, section 0.14). Keep the sections, their order, and their headings; replace the angle-bracket
placeholders. Write from the skill's `SKILL.md` and its files, never beyond them: the page summarises the skill, it does
not extend it. Add the page to the `nav` of `mkdocs.yml` and a cell for it to the grid of `docs/index.md` in the same
change that adds the skill.

``````markdown
# <skill-name>

<Two or three sentences: what the skill produces, for whom, and what it never does.>

## At a glance

| Field | Value |
| --- | --- |
| Skill | `<skill-name>` |
| Invoke | `/<skill-name> <arguments>`, or describe the task in your own words |
| Arguments | <one line; "None declared" when the front matter has no `argument-hint`> |
| Produces | <the deliverables> |
| Source | [`skills/<skill-name>`](https://github.com/Energy-Atlas/dev-skills/tree/main/skills/<skill-name>) |

## Arguments

<One sentence on how the skill reads its arguments.>

| Argument | Required | Default | Meaning |
| --- | --- | --- | --- |
| `<argument>` | <Yes / No> | <default or —> | <meaning> |

```text
/<skill-name> <example arguments>
```

## When to use it

- <the requests and situations that should trigger the skill, from its description>

## What it does

1. <the workflow, one short step per phase>

## Files

| File | Contents |
| --- | --- |
| [`SKILL.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/<skill-name>/SKILL.md) | <the workflow and the rules> |
| [`references/<file>.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/<skill-name>/references/<file>.md) | <contents> |

## Install

```bash
npx skills add energy-atlas/dev-skills --skill <skill-name> -g -a claude-code
```

On Windows, add `--copy`. See [Install](../index.md#install) for the other options and for updating.

## SKILL.md

The current file, included from the repository when the site is built.

`````markdown
--8<-- "skills/<skill-name>/SKILL.md"
`````
``````

The copy uses a fence of five backticks, so that code fences inside a `SKILL.md` cannot close it.

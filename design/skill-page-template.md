# Skill page template

Every skill has one page on the site, `docs/skills/<skill-name>.md`, written by hand in this format
(`ui-design-spec.md`, section 0.14). Keep the sections, their order, and their headings; replace the angle-bracket
placeholders. Write from the skill's `SKILL.md` and its files, never beyond them: the page summarises the skill, it does
not extend it. Add the page to the `nav` of `mkdocs.yml` in the same change that adds the skill.

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

## Example

<Optional, only for a skill whose output is visual (icons): one sentence on what the example is, then a
`<div class="ea-icon-sample" markdown>` tile with one `<div class="ea-icon-sample-row ea-icon-sample-regular" markdown>`
(or `-bold`) per row, each holding a label and `<span class="ea-icon" data-icon="<file-name>"></span>` placeholders that
`hooks/icons.py` replaces with the files of `docs/assets/examples/<skill-name>/`, copies of the skill's own example.
Leave the section out otherwise.>

## Files

| File | Contents |
| --- | --- |
| [`SKILL.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/<skill-name>/SKILL.md) | <the workflow and the rules> |
| [`references/<file>.md`](https://github.com/Energy-Atlas/dev-skills/blob/main/skills/<skill-name>/references/<file>.md) | <contents> |
``````
